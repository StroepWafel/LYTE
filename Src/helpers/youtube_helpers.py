# =============================================================================
# YOUTUBE INTEGRATION
# =============================================================================

# Standard Library Imports
import re
import time
import logging
from typing import Dict, Optional

# Third-Party Imports
import requests  # HTTP requests for faster fetching
import yt_dlp  # YouTube video/audio extraction (still needed for audio URLs)

# =============================================================================

# =============================================================================
# yt-dlp Logger Integration
# =============================================================================

class YtDlpLogger:
    """Forward yt-dlp logs into the application's logging system.

    Methods match yt-dlp's expected interface: debug, warning, error.
    We forward debug as INFO so it appears in the GUI and log files
    with the current application logging level.
    """

    def debug(self, msg):
        try:
            logging.info(f"[yt-dlp] {msg}")
        except Exception:
            pass

    def warning(self, msg):
        try:
            logging.warning(f"[yt-dlp] {msg}")
        except Exception:
            pass

    def error(self, msg):
        try:
            logging.error(f"[yt-dlp] {msg}")
        except Exception:
            pass

# Cache for video titles and channel names to avoid repeated requests
_video_title_cache: Dict[str, str] = {}
_channel_name_cache: Dict[str, str] = {}
_cache_timestamps: Dict[str, float] = {}
CACHE_DURATION = 3600  # Cache for 1 hour

def _is_cache_valid(key: str) -> bool:
    """Check if cached data is still valid."""
    if key not in _cache_timestamps:
        return False
    return time.time() - _cache_timestamps[key] < CACHE_DURATION

def _get_from_cache(key: str, cache_dict: Dict[str, str]) -> Optional[str]:
    """Get value from cache if valid."""
    if _is_cache_valid(key) and key in cache_dict:
        return cache_dict[key]
    return None

def _set_cache(key: str, value: str, cache_dict: Dict[str, str]) -> None:
    """Set value in cache with timestamp."""
    cache_dict[key] = value
    _cache_timestamps[key] = time.time()

def get_video_title_fast(video_id: str) -> str:
    """
    Get video title using YouTube oEmbed API (much faster than yt_dlp).
    
    Args:
        video_id: YouTube video ID
        
    Returns:
        str: Video title or "Unknown Video" if not found
    """
    # Check cache first
    cached_title = _get_from_cache(video_id, _video_title_cache)
    if cached_title:
        return cached_title
    
    try:
        # Use YouTube oEmbed API - much faster than yt_dlp
        oembed_url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
        
        # Use session for connection pooling and better performance
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        response = session.get(oembed_url, timeout=3)  # Reduced timeout for faster failure
        response.raise_for_status()
        
        data = response.json()
        title = data.get('title', 'Unknown Video')
        
        # Cache the result
        _set_cache(video_id, title, _video_title_cache)
        return title
        
    except Exception as e:
        logging.error(f"Error fetching video title via oEmbed: {e}")
        # Fallback to yt_dlp if oEmbed fails
        try:
            url = f"https://www.youtube.com/watch?v={video_id}"
            ydl_opts = {
                'quiet': False,
                'extract_flat': True,
                'logger': YtDlpLogger()
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                title = info.get('title', 'Unknown Video')
                _set_cache(video_id, title, _video_title_cache)
                return title
        except Exception:
            return 'Unknown Video'

def get_channel_name_fast(channel_id: str) -> str:
    """
    Get channel name using lightweight web scraping (faster than yt_dlp).
    
    Args:
        channel_id: YouTube channel ID
        
    Returns:
        str: Channel name or "Unknown Channel" if not found
    """
    # Check cache first
    cached_name = _get_from_cache(channel_id, _channel_name_cache)
    if cached_name:
        return cached_name
    
    try:
        # Try to get channel name from channel page
        url = f"https://www.youtube.com/channel/{channel_id}"
        
        # Use session for connection pooling and better performance
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        response = session.get(url, timeout=5)  # Reduced timeout
        response.raise_for_status()
        
        # Look for channel name in page title or meta tags
        content = response.text
        
        # Try to extract from page title
        title_match = re.search(r'<title>([^<]+)</title>', content)
        if title_match:
            title = title_match.group(1)
            # Remove " - YouTube" suffix if present
            channel_name = title.replace(' - YouTube', '').strip()
            if channel_name and channel_name != 'YouTube':
                _set_cache(channel_id, channel_name, _channel_name_cache)
                return channel_name
        
        # Try to extract from JSON-LD structured data
        json_ld_match = re.search(r'"name":\s*"([^"]+)"', content)
        if json_ld_match:
            channel_name = json_ld_match.group(1)
            _set_cache(channel_id, channel_name, _channel_name_cache)
            return channel_name
            
    except Exception as e:
        logging.error(f"Error fetching channel name via web scraping: {e}")
    
    # Fallback to yt_dlp if web scraping fails
    try:
        url = f"https://www.youtube.com/channel/{channel_id}"
        ydl_opts = {
            "quiet": False,
            "no_warnings": False,
            "skip_download": True,
            "logger": YtDlpLogger()
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            channel_name = info.get("uploader", "Unknown Channel")
            _set_cache(channel_id, channel_name, _channel_name_cache)
            return channel_name
    except Exception:
        return "Unknown Channel"

# Legacy functions for backward compatibility (now use fast versions)
def get_video_title(youtube_url: str) -> str:
    """
    Extract video title from YouTube URL (legacy function).
    
    Args:
        youtube_url: Full YouTube URL
        
    Returns:
        str: Video title
    """
    # Extract video ID from URL
    video_id_match = re.search(r'(?:v=|/)([a-zA-Z0-9_-]{11})', youtube_url)
    if video_id_match:
        video_id = video_id_match.group(1)
        return get_video_title_fast(video_id)
    
    # Fallback to yt_dlp for non-standard URLs
    ydl_opts = {
        'quiet': False,
        'extract_flat': True,
        'logger': YtDlpLogger()
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(youtube_url, download=False)
        return info['title']

def get_video_name_fromID(video_id: str) -> str:
    """
    Get video title from YouTube video ID (now uses fast method).
    
    Args:
        video_id: YouTube video ID
        
    Returns:
        str: Video title
    """
    return get_video_title_fast(video_id)

def get_direct_url(youtube_url: str) -> str:
    """
    Get direct audio stream URL from YouTube URL.
    
    Args:
        youtube_url: Full YouTube URL
        
    Returns:
        str: Direct audio stream URL for VLC playback
    """
    ydl_opts = {
        'format': 'bestaudio',
        'quiet': False,
        'logger': YtDlpLogger()
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(youtube_url, download=False)
        return info['url']

def fetch_channel_name(channel_id: str) -> str:
    """
    Fetch channel name from YouTube channel ID (now uses fast method).
    
    Args:
        channel_id: YouTube channel ID
        
    Returns:
        str: Channel name or "Unknown Channel" if not found
    """
    return get_channel_name_fast(channel_id)

def fetch_video_name(video_id: str) -> str:
    """
    Fetch video name from YouTube video ID (now uses fast method).
    
    Args:
        video_id: YouTube video ID
        
    Returns:
        str: Video title
    """
    return get_video_title_fast(video_id)
