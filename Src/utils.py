# =============================================================================
# LYTE - Utility Functions
# All utility functions for the main program are defined here.
# =============================================================================

# Standard Library Imports
import json
import logging
import os
import sys
from datetime import datetime

# Third-Party Imports
import requests  # HTTP requests
import yt_dlp  # YouTube video/audio extraction
import forex_python.converter  # Currency conversion for superchat values

# =============================================================================
# FILE AND CONFIGURATION
# =============================================================================

def get_app_folder() -> str:
    """
    Determine the application folder path.
    
    Returns:
        str: Path to the application directory (executable dir if frozen, script dir otherwise)
    """
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

def ensure_file_exists(filepath: str, default_content) -> None:
    """
    Create a file with default content if it doesn't exist.
    
    Args:
        filepath: Path to the file to create
        default_content: Default content to write to the file
    """
    if not os.path.isfile(filepath):
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(default_content, f, indent=4)
        logging.info(f"Created missing file: {filepath}")

def ensure_json_valid(filepath: str, default_content: dict) -> None:
    """
    Validate and clean a JSON configuration file.
    
    This function ensures the JSON file is valid and contains only expected keys.
    If the file is corrupted or contains extra keys, it will be cleaned up.
    
    Args:
        filepath: Path to the JSON file to validate
        default_content: Default configuration structure to validate against
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                # Reset to defaults if file is corrupted
                with open(filepath, 'w', encoding='utf-8') as fw:
                    json.dump(default_content, fw, indent=4)
                logging.warning(f"Invalid JSON in {filepath}. Resetting to default.")
                return

        modified = False
        cleaned_data = {}

        # Copy over valid keys from default_config
        for key, default_value in default_content.items():
            if key in data:
                cleaned_data[key] = data[key]
            else:
                cleaned_data[key] = default_value
                modified = True
                logging.info(f"Added missing key '{key}' to {filepath}")

        # Check for and remove extra keys
        extra_keys = set(data.keys()) - set(default_content.keys())
        if extra_keys:
            modified = True
            logging.info(f"Removing extra keys from {filepath}: {extra_keys}")

        if modified:
            # Create a backup before making changes
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = f"{filepath}.backup_{timestamp}.json"
            with open(backup_path, 'w', encoding='utf-8') as backup_file:
                json.dump(data, backup_file, indent=4)
            logging.info(f"Backed up original config file to {backup_path}")

            # Write cleaned data
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(cleaned_data, f, indent=4)
            logging.info(f"Successfully cleaned and updated {filepath}")

    except Exception as e:
        logging.error(f"Error validating JSON file {filepath}: {e}")

# =============================================================================
# TIME FORMATTING
# =============================================================================

def format_time(seconds: float) -> str:
    """
    Format time in seconds to MM:SS format.
    
    Args:
        seconds: Time in seconds
        
    Returns:
        str: Formatted time string (MM:SS)
    """
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes:02d}:{seconds:02d}"

# =============================================================================
# YOUTUBE INTEGRATION
# =============================================================================

def get_video_title(youtube_url: str) -> str:
    """
    Extract video title from YouTube URL.
    
    Args:
        youtube_url: Full YouTube URL
        
    Returns:
        str: Video title
    """
    ydl_opts = {'quiet': True, 'extract_flat': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(youtube_url, download=False)
        return info['title']

def get_video_name_fromID(video_id: str) -> str:
    """
    Get video title from YouTube video ID.
    
    Args:
        video_id: YouTube video ID
        
    Returns:
        str: Video title
    """
    url = f"https://music.youtube.com/watch?v={video_id}"
    return get_video_title(url)

def get_direct_url(youtube_url: str) -> str:
    """
    Get direct audio stream URL from YouTube URL.
    
    Args:
        youtube_url: Full YouTube URL
        
    Returns:
        str: Direct audio stream URL for VLC playback
    """
    ydl_opts = {'format': 'bestaudio'}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(youtube_url, download=False)
        return info['url']

def fetch_channel_name(channel_id: str) -> str:
    """
    Fetch channel name from YouTube channel ID.
    
    Args:
        channel_id: YouTube channel ID
        
    Returns:
        str: Channel name or "Unknown Channel" if not found
    """
    url = f"https://www.youtube.com/channel/{channel_id}"
    ydl_opts = {"quiet": True, "no_warnings": True, "skip_download": True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        return info.get("uploader", "Unknown Channel")

def fetch_video_name(video_id: str) -> str:
    """
    Fetch video name from YouTube video ID.
    
    Args:
        video_id: YouTube video ID
        
    Returns:
        str: Video title
    """
    return get_video_name_fromID(video_id)

# =============================================================================
# VERSION MANAGEMENT
# =============================================================================

def compare_versions(version1: str, version2: str) -> int:
    """
    Compare two version strings.
    
    Args:
        version1: First version string (e.g., "1.5.0")
        version2: Second version string (e.g., "1.6.0")
        
    Returns:
        int: -1 if version1 < version2, 0 if equal, 1 if version1 > version2
    """
    def version_tuple(v):
        # Remove any non-numeric suffixes (like "-Release", "-beta", etc.)
        # and split by dots, converting to integers
        clean_version = v.split('-')[0].split('_')[0]  # Remove suffixes after - or _
        parts = clean_version.split('.')
        
        # Convert each part to int, handling cases where parts might be empty
        result = []
        for part in parts:
            if part.isdigit():
                result.append(int(part))
            else:
                # If any part is not a digit, treat as 0
                result.append(0)
        return tuple(result)
    
    v1_tuple = version_tuple(version1)
    v2_tuple = version_tuple(version2)
    
    if v1_tuple < v2_tuple:
        return -1
    elif v1_tuple > v2_tuple:
        return 1
    else:
        return 0

def fetch_latest_version() -> str:
    """
    Fetch the latest release version from GitHub API.
    
    Returns:
        str: Latest version string, or empty string if failed
    """
    try:
        url = "https://api.github.com/repos/StroepWafel/LYTE/releases/latest"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        latest_version = data.get("tag_name", "")
        
        # Remove 'v' prefix if present
        if latest_version.startswith("v"):
            latest_version = latest_version[1:]
            
        logging.info(f"Latest version available: {latest_version}")
        return latest_version
        
    except Exception as e:
        logging.warning(f"Failed to fetch latest version: {e}")
        return ""

# =============================================================================
# CURRENCY CONVERSION
# =============================================================================

def convert_to_usd(value: float = 1, currency_name: str = "USD") -> float:
    """
    Convert currency value to USD.
    
    Args:
        value: Amount to convert
        currency_name: Source currency code
        
    Returns:
        float: Value in USD
    """
    converter = forex_python.converter.CurrencyRates()
    usd_value = converter.convert(currency_name, 'USD', value)
    return usd_value

# =============================================================================
# DATA MANAGEMENT UTILITIES
# =============================================================================

def load_banned_users(banned_users_path: str) -> list:
    """
    Load banned users list from file.
    
    Args:
        banned_users_path: Path to the banned users JSON file
        
    Returns:
        list: List of banned users
    """
    if os.path.exists(banned_users_path):
        with open(banned_users_path, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        return []

def load_banned_ids(banned_ids_path: str) -> list:
    """
    Load banned video IDs list from file.
    
    Args:
        banned_ids_path: Path to the banned IDs JSON file
        
    Returns:
        list: List of banned video IDs
    """
    if os.path.exists(banned_ids_path):
        with open(banned_ids_path, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        return []

def load_whitelisted_users(whitelisted_users_path: str) -> list:
    """
    Load whitelisted users list from file.
    
    Args:
        whitelisted_users_path: Path to the whitelisted users JSON file
        
    Returns:
        list: List of whitelisted users
    """
    if os.path.exists(whitelisted_users_path):
        with open(whitelisted_users_path, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        return []

def load_whitelisted_ids(whitelisted_ids_path: str) -> list:
    """
    Load whitelisted video IDs list from file.
    
    Args:
        whitelisted_ids_path: Path to the whitelisted IDs JSON file
        
    Returns:
        list: List of whitelisted video IDs
    """
    if os.path.exists(whitelisted_ids_path):
        with open(whitelisted_ids_path, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        return []

def save_banned_users(banned_users: list, banned_users_path: str) -> None:
    """Save banned users list to file."""
    with open(banned_users_path, "w", encoding="utf-8") as f:
        json.dump(banned_users, f, indent=4)

def save_banned_ids(banned_ids: list, banned_ids_path: str) -> None:
    """Save banned video IDs list to file."""
    with open(banned_ids_path, "w", encoding="utf-8") as f:
        json.dump(banned_ids, f, indent=4)

def save_whitelisted_users(whitelisted_users: list, whitelisted_users_path: str) -> None:
    """Save whitelisted users list to file."""
    with open(whitelisted_users_path, "w", encoding="utf-8") as f:
        json.dump(whitelisted_users, f, indent=4)

def save_whitelisted_ids(whitelisted_ids: list, whitelisted_ids_path: str) -> None:
    """Save whitelisted video IDs list to file."""
    with open(whitelisted_ids_path, "w", encoding="utf-8") as f:
        json.dump(whitelisted_ids, f, indent=4)

# =============================================================================
# UPDATE MANAGEMENT UTILITIES
# =============================================================================

def run_installer(app_folder: str) -> None:
    """
    Run the downloaded installer.
    
    Args:
        app_folder: Path to the application folder
    """
    try:
        installer_path = os.path.join(app_folder, "LYTE_Installer.exe")
        
        if os.path.exists(installer_path):
            logging.info("Running installer...")
            os.startfile(installer_path)  # Windows-specific
            logging.info("Installer started successfully")
        else:
            logging.error("Installer not found. Please download it first.")
            
    except Exception as e:
        logging.error(f"Error running installer: {e}")

def download_installer_worker(app_folder: str) -> None:
    """
    Worker function that downloads the installer in the background.
    
    Args:
        app_folder: Path to the application folder
    """
    try:
        installer_url = "https://github.com/StroepWafel/LYTE-NSIS-Installer/releases/download/latest/LYTE_Installer.exe"
        download_path = os.path.join(app_folder, "LYTE_Installer.exe")
        
        logging.info("Starting installer download...")
        
        response = requests.get(installer_url, stream=True, timeout=30)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        downloaded_size = 0
        
        with open(download_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    file.write(chunk)
                    downloaded_size += len(chunk)
        
        logging.info(f"Installer downloaded successfully to: {download_path}")
            
    except Exception as e:
        logging.error(f"Error downloading installer: {e}")

def check_for_updates(current_version: str, toast_notifications: bool) -> str:
    """
    Check for available updates and notify the user if a new version is available.
    
    Args:
        current_version: Current application version
        toast_notifications: Whether to show desktop notifications
        
    Returns:
        str: Latest version if available, empty string otherwise
    """
    try:
        latest_version = fetch_latest_version()
        if not latest_version:
            return ""
            
        if compare_versions(current_version, latest_version) < 0:
            logging.info(f"Update available! Current: {current_version}, Latest: {latest_version}")
            logging.info("Visit https://github.com/StroepWafel/LYTE/releases/latest to download the update")
            
            # Show desktop notification if enabled
            if toast_notifications:
                from plyer import notification
                notification.notify(
                    title="LYTE Update Available",
                    message=f"Version {latest_version} is now available! Current version: {current_version}",
                    timeout=10
                )
            
            return latest_version
        else:
            logging.info(f"LYTE is up to date (version {current_version})")
            return ""
            
    except Exception as e:
        logging.error(f"Error checking for updates: {e}")
        return ""
