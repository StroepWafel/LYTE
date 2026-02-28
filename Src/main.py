# ==============================================================================
# LYTE - YouTube Live Music Queue Bot
# A bot that allows YouTube live stream viewers to queue music via chat commands
# ==============================================================================

# ==============================================================================
# Application version
CURRENT_VERSION = "1.9.0"
# ==============================================================================

# Standard Library Imports
import json
import logging
import os
import re
import threading
import time
import traceback
from collections import defaultdict
from datetime import datetime
from time import time as current_time
import webbrowser


# Third-Party Imports
import pytchat  # YouTube live chat integration
import requests  # HTTP requests
from plyer import notification  # Desktop notifications
import vlc  # Media player (python-vlc)
# GUI: PySide6 via gui module
from watchdog.observers import Observer  # File system monitoring
from watchdog.events import FileSystemEventHandler  # File system event handling
# Currency conversion is handled by helpers.currency_helpers

# Local Imports
from settings import Settings
from helpers.moderation_helpers import (
    load_banned_users,
    load_banned_ids,
    load_whitelisted_users,
    load_whitelisted_ids,
    save_banned_users,
    save_banned_ids,
    save_whitelisted_users,
    save_whitelisted_ids
)
from helpers.currency_helpers import (
    convert_to_usd
)
from helpers.youtube_helpers import (
    get_video_title,
    get_video_name_fromID,
    get_direct_url,
    fetch_channel_name
)
from helpers.time_helpers import (
    format_time
)
from helpers.file_helpers import (
    get_app_folder,
    ensure_file_exists,
    ensure_json_valid,
    show_folder
)
from helpers.update_helpers import (
    run_installer,
    download_installer_worker,
    check_for_updates
)
from helpers.version_helpers import (
    fetch_latest_release_details,
)
from helpers.theme_helpers import (
    init_theme_system,
    unload_all_themes,
    load_all_themes,
    create_default_theme_files,
    apply_theme,
    get_theme_dropdown_items,
    get_theme_name_from_display,
    get_available_themes,
    get_current_theme,
    set_current_theme,
)

# =============================================================================
# APPLICATION INITIALIZATION & GLOBAL CONSTANTS
# =============================================================================


# Currency conversion is handled by helpers.currency_helpers.convert_to_usd

# =============================================================================
# GLOBAL CONSTANTS & PATHS
# =============================================================================

# Application paths
APP_FOLDER = get_app_folder()
LOG_FOLDER = os.path.join(APP_FOLDER, 'logs')
os.makedirs(LOG_FOLDER, exist_ok=True)

# Configuration file paths
CONFIG_PATH = os.path.join(APP_FOLDER, 'config.json')
BANNED_IDS_PATH = os.path.join(APP_FOLDER, 'banned_IDs.json')
BANNED_USERS_PATH = os.path.join(APP_FOLDER, 'banned_users.json')
WHITELISTED_IDS_PATH = os.path.join(APP_FOLDER, 'whitelisted_IDs.json')
WHITELISTED_USERS_PATH = os.path.join(APP_FOLDER, 'whitelisted_users.json')

# Themes directory
THEMES_FOLDER = os.path.join(APP_FOLDER, 'themes')
init_theme_system(THEMES_FOLDER)

# close gui
closeGui = False

# =============================================================================
# LOGGING SETUP
# =============================================================================

# Create timestamped log file
log_filename = os.path.join(LOG_FOLDER, f"app_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log")

# Configure logging with both file and console output
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
file_handler = logging.FileHandler(log_filename)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
file_handler.setLevel(logging.INFO)
logging.getLogger().addHandler(file_handler)

# Suppress noisy third-party library logs
logging.getLogger("urllib3").setLevel(logging.ERROR)
logging.getLogger('httpx').setLevel(logging.ERROR)
logging.getLogger('httpcore').setLevel(logging.ERROR)
logging.getLogger('yt_dlp').setLevel(logging.ERROR)

# =============================================================================
# GLOBAL STATE VARIABLES
# =============================================================================

# GUI state variables
last_user_seek_time = 0

# Application control
should_exit = False

# =============================================================================
# CONFIGURATION MANAGEMENT
# =============================================================================

# Global data structures for banned/whitelisted users and videos
BANNED_USERS: list[dict] = []  # {"id": "UCxxxx", "name": "ChannelName"}
BANNED_IDS: list[dict] = []    # {"id": "xxxxxx", "name": "VideoName"}
WHITELISTED_USERS: list[dict] = []  # {"id": "UCxxxx", "name": "ChannelName"}
WHITELISTED_IDS: list[dict] = []    # {"id": "xxxxxx", "name": "VideoName"}

# Queue history - stores past queued songs (resets on app restart)
QUEUE_HISTORY: list[dict] = []  # [{"user_id": "UCxxxx", "username": "Name", "song_id": "xxxxxx", "song_title": "Title"}]

# Update detection state
UPDATE_AVAILABLE: bool = False
LATEST_RELEASE_DETAILS: dict = {}
LATEST_VERSION: str = ""
IGNORED_VERSION: str = ""

# Track user-initiated skips
user_initiated_skip = False

# GUI bridge and main window ref (set by gui.app when GUI starts)
GUI_BRIDGE = None
GUI_MAIN_WINDOW_REF = []


# =============================================================================
# DEFAULT CONFIGURATION
# =============================================================================

# Default configuration values for the application
default_config = {
    "YOUTUBE_VIDEO_ID": "LIVESTREAM_ID",      # YouTube livestream ID to monitor
    "RATE_LIMIT_SECONDS": 3000,               # Cooldown between user requests (seconds)
    "TOAST_NOTIFICATIONS": "True",            # Enable desktop notifications
    "PREFIX": "!",                            # Command prefix for chat messages
    "QUEUE_COMMAND": "queue",                 # Command name for queuing songs
    "VOLUME": 50,                             # Default volume level (0-100)
    "THEME": "dark_theme",                    # Theme name
    "ALLOW_URLS": "False",                    # Allow full YouTube URLs in requests
    "REQUIRE_MEMBERSHIP": "False",            # Require channel membership to request
    "REQUIRE_SUPERCHAT": "False",             # Require superchat to request
    "MINIMUM_SUPERCHAT": 3,                   # Minimum superchat value in USD
    "ENFORCE_ID_WHITELIST": "False",          # Only allow whitelisted video IDs
    "ENFORCE_USER_WHITELIST": "False",        # Only allow whitelisted users
    "AUTOREMOVE_SONGS": "True",               # Auto-remove finished songs from queue
    "AUTOBAN_USERS": "False",                 # Auto-ban users who request banned videos
    "SONG_FINISH_NOTIFICATIONS": "False",     # Notify when songs finish naturally (not skipped)
    "IGNORED_VERSION": ""                     # Version to ignore when checking for updates  
}

# =============================================================================
# CONFIGURATION INITIALIZATION
# =============================================================================

# Ensure all required files exist with default content
ensure_file_exists(CONFIG_PATH, default_config)
ensure_file_exists(BANNED_IDS_PATH, [])
ensure_file_exists(BANNED_USERS_PATH, [])
ensure_file_exists(WHITELISTED_IDS_PATH, [])
ensure_file_exists(WHITELISTED_USERS_PATH, [])

# Validate and clean configuration files
ensure_json_valid(CONFIG_PATH, default_config)

# Initialize Settings class with config path
Settings.set_path(CONFIG_PATH)
Settings.load()

# Set theme from Settings
set_current_theme(Settings.THEME)

# Load configuration data from files
with open(BANNED_IDS_PATH, 'r', encoding="utf-8") as f:
    BANNED_IDS = json.load(f)
with open(BANNED_USERS_PATH, "r", encoding="utf-8") as f:
    BANNED_USERS = json.load(f)
with open(WHITELISTED_IDS_PATH, 'r', encoding="utf-8") as f:
    WHITELISTED_IDS = json.load(f)
with open(WHITELISTED_USERS_PATH, "r", encoding="utf-8") as f:
    WHITELISTED_USERS = json.load(f)

# =============================================================================
# CONFIGURATION VARIABLES (deprecated - use Settings.field instead)
# =============================================================================
# These are kept for backward compatibility during migration
# Access settings via Settings.field (e.g., Settings.VOLUME, Settings.PREFIX)


# User rate limiting - tracks last command time per user
user_last_command = defaultdict(lambda: 0)
# =============================================================================
# VLC MEDIA PLAYER SETUP
# =============================================================================

def on_next_item(event) -> None:
    """
    Callback function triggered when VLC moves to the next item in the playlist.
    
    If auto-remove is enabled, this removes the finished song from the queue.
    Also handles notifications for the new song starting.
    
    Args:
        event: VLC event object (unused but required by VLC callback signature)
    """
    global user_initiated_skip, QUEUE_HISTORY
    
    # Check if this was a natural completion (not user-initiated skip)
    is_natural_completion = not user_initiated_skip
    
    # Reset the flag for next time
    user_initiated_skip = False
    
    # Show notification for the NEW song starting if it finished naturally and notifications are enabled
    if is_natural_completion and Settings.SONG_FINISH_NOTIFICATIONS:
        try:
            # Get the new song that's now playing
            media_player = player.get_media_player()
            if media_player:
                media = media_player.get_media()
                if media:
                    media.parse_with_options(vlc.MediaParseFlag.local, timeout=1000)
                    new_song_title = media.get_meta(vlc.Meta.Title)
                    
                    if new_song_title:
                        notification.notify(
                            title="Now Playing",
                            message=f"'{new_song_title}'",
                            timeout=5
                        )
        except Exception as e:
            logging.error(f"Error showing new song notification: {e}")
    
    if Settings.AUTOREMOVE_SONGS:
        try:
            # Always remove the first item (the one that just finished)
            if media_list.count() > 1:
                media_list.lock()
                media_list.remove_index(0)
                media_list.unlock()
                logging.info("Removed finished song from queue")
            if media_list.count() == 0:
                logging.info("Queue empty - stopping player")
                player.stop()
        except Exception as e:
            logging.error(f"Error removing finished song: {e}")

# Initialize VLC media player components
instance = vlc.Instance("--one-instance") # Prevent multiple VLC instances
player = instance.media_list_player_new()  # Create playlist player
media_list = instance.media_list_new()     # Create empty playlist
player.set_media_list(media_list)          # Assign playlist to player
player.play()                              # Start the player
player.get_media_player().audio_set_volume(Settings.VOLUME)  # Set initial volume

# Set up event handling for automatic song removal
event_manager = player.event_manager()
event_manager.event_attach(vlc.EventType.MediaListPlayerNextItemSet, on_next_item)
logging.info("Started VLC media player...")

# =============================================================================
# DATA MANAGEMENT FUNCTIONS
# =============================================================================

def load_banned_users_wrapper() -> None:
    """Load banned users list from file and update global variable."""
    global BANNED_USERS
    BANNED_USERS = load_banned_users(BANNED_USERS_PATH)

def load_banned_ids_wrapper() -> None:
    """Load banned video IDs list from file and update global variable."""
    global BANNED_IDS
    BANNED_IDS = load_banned_ids(BANNED_IDS_PATH)

def load_whitelisted_users_wrapper() -> None:
    """Load whitelisted users list from file and update global variable."""
    global WHITELISTED_USERS
    WHITELISTED_USERS = load_whitelisted_users(WHITELISTED_USERS_PATH)

def load_whitelisted_ids_wrapper() -> None:
    """Load whitelisted video IDs list from file and update global variable."""
    global WHITELISTED_IDS
    WHITELISTED_IDS = load_whitelisted_ids(WHITELISTED_IDS_PATH)

def load_settings_wrapper() -> None:
    """Load settings from config file and update global variables."""
    load_config()

def download_installer() -> None:
    """Start downloading the latest installer from GitHub in a background thread."""
    # Start download in background thread
    threading.Thread(target=download_installer_worker, args=(APP_FOLDER,), daemon=True).start()

def run_installer_wrapper() -> None:
    """Run the downloaded installer."""
    run_installer(APP_FOLDER)

def check_for_updates_wrapper() -> None:
    """Check for updates with current configuration."""
    global UPDATE_AVAILABLE, LATEST_RELEASE_DETAILS, LATEST_VERSION, IGNORED_VERSION
    Settings.load()
    IGNORED_VERSION = Settings.IGNORED_VERSION
    latest_version = check_for_updates(CURRENT_VERSION, IGNORED_VERSION, Settings.TOAST_NOTIFICATIONS)
    if latest_version:
        UPDATE_AVAILABLE = True
        LATEST_VERSION = latest_version
        try:
            LATEST_RELEASE_DETAILS = fetch_latest_release_details() or {}
        except Exception:
            LATEST_RELEASE_DETAILS = {}

        # If the GUI exists, surface UI immediately
        try:
            if GUI_BRIDGE:
                show_download_ui(latest_version)
        except Exception:
            pass

# =============================================================================
# TEMPORARY TEST FUNC FOR RELOADING THEMES
# =============================================================================
THEME_MENU_TAG = "theme_menu_root"
THEME_MENU_EMPTY_TAG = "theme_menu_empty"

def rebuild_theme_menu_items() -> None:
    """No-op for PySide6 - theme menu is built once in main window."""
    pass

def reload_themes() -> None:
    """Reload all themes from disk."""
    unload_all_themes()
    load_all_themes()
    apply_theme(get_current_theme())


def _reload_themes_with_menu_refresh() -> None:
    """Reload themes and rebuild theme menu (for file watcher / live reload)."""
    if GUI_MAIN_WINDOW_REF:
        try:
            GUI_MAIN_WINDOW_REF[0]._do_reload_themes()
        except (AttributeError, IndexError):
            reload_themes()
    else:
        reload_themes()

# =============================================================================
# THEME FILE WATCHER
# =============================================================================

class ThemeFileHandler(FileSystemEventHandler):
    """
    File system event handler for theme files.
    Uses QTimer.singleShot to run reload on GUI thread (thread-safe).
    """
    def __init__(self):
        super().__init__()
        self.last_reload_time = 0
        self.reload_debounce_seconds = 0.5  # Debounce rapid file changes

    def on_any_event(self, event):
        """
        Handle any file system event in the themes folder.
        
        Args:
            event: File system event object
        """
        # Only process events for JSON and QSS theme files
        if event.is_directory:
            return
        path = getattr(event, 'dest_path', None) or event.src_path
        if not (path.endswith('.json') or path.endswith('.qss')):
            return
        if path.endswith('.json.demo') or path.endswith('.qss.example'):
            return
        
        # Debounce rapid changes (editors may trigger multiple events; Windows can fire before write completes)
        current_time = time.time()
        if current_time - self.last_reload_time < self.reload_debounce_seconds:
            return
        
        # Schedule theme reload on GUI thread (thread-safe). 300ms delay helps Windows: file may not be fully written yet.
        if event.event_type in ('created', 'modified', 'deleted', 'moved'):
            self.last_reload_time = current_time
            try:
                from PySide6.QtCore import QTimer
                QTimer.singleShot(300, _reload_themes_with_menu_refresh)
                logging.info(f"Theme file change detected: {os.path.basename(path)} ({event.event_type}), reloading in 0.3s...")
            except Exception:
                if GUI_BRIDGE:
                    GUI_BRIDGE.request_theme_reload.emit()

# Global observer instance for theme file watching
theme_observer = None

def start_theme_file_watcher() -> None:
    """
    Start monitoring the themes folder for file changes.
    
    Runs in a background thread and automatically reloads themes when changes are detected.
    """
    global theme_observer
    
    if theme_observer is not None:
        return  # Already running (avoid duplicate observers)
    if not os.path.exists(THEMES_FOLDER):
        logging.warning(f"Themes folder does not exist: {THEMES_FOLDER}")
        return

    try:
        event_handler = ThemeFileHandler()
        theme_observer = Observer()
        theme_observer.schedule(event_handler, THEMES_FOLDER, recursive=False)
        theme_observer.start()
        logging.info(f"Started theme file watcher for: {THEMES_FOLDER}")
    except Exception as e:
        logging.error(f"Error starting theme file watcher: {e}")
        logging.error(traceback.format_exc())

def stop_theme_file_watcher() -> None:
    """Stop monitoring the themes folder for file changes."""
    global theme_observer
    
    if theme_observer:
        try:
            theme_observer.stop()
            theme_observer.join()
            theme_observer = None
            logging.info("Stopped theme file watcher")
        except Exception as e:
            logging.error(f"Error stopping theme file watcher: {e}")

# =============================================================================
# APPLICATION CONTROL FUNCTIONS
# =============================================================================

def on_close_attempt(sender, data) -> None:
    """
    Handle application close attempt.
    
    Args:
        sender: GUI element that triggered the close (unused)
        data: Additional data (unused)
    """
    print("Program closed - If this was you, please use 'Quit' button instead! (unless program is frozen)")

def initialize_chat() -> bool:
    """
    Initialize YouTube live chat connection.
    
    Returns:
        bool: True if chat connection successful, False otherwise
    """
    global chat
    try:
        # Clean up any existing chat object before creating a new one
        # This prevents issues when switching from a regular video to a live video
        try:
            if 'chat' in globals():
                old_chat = globals()['chat']
                if old_chat is not None:
                    try:
                        if hasattr(old_chat, 'terminate'):
                            old_chat.terminate()
                    except Exception:
                        pass
        except (KeyError, AttributeError):
            pass
        chat = pytchat.create(video_id=Settings.YOUTUBE_VIDEO_ID)
        return True
    except Exception as e:
        logging.critical(f"Invalid YouTube Video ID '{Settings.YOUTUBE_VIDEO_ID}'")
        logging.critical(f"Error {traceback.format_exc()}")
        return False

def load_config() -> None:
    """
    Load and parse all configuration files.
    
    Reloads all configuration data from JSON files and updates global variables.
    This function is called when configuration changes are made through the GUI.
    """
    global BANNED_IDS, BANNED_USERS, WHITELISTED_IDS, WHITELISTED_USERS

    # Reload Settings from file
    Settings.load()
    
    # Update theme if it changed
    set_current_theme(Settings.THEME)
    
    # Load moderation lists
    BANNED_IDS = load_banned_ids(BANNED_IDS_PATH)
    BANNED_USERS = load_banned_users(BANNED_USERS_PATH)
    WHITELISTED_IDS = load_whitelisted_ids(WHITELISTED_IDS_PATH)
    WHITELISTED_USERS = load_whitelisted_users(WHITELISTED_USERS_PATH)

def quit_program() -> None:
    """
    Gracefully shutdown the application.
    
    Stops all media playback, releases VLC resources, and closes the GUI.
    """
    global should_exit
    should_exit = True
    
    logging.info("Shutting down program")

    # Stop theme file watcher
    stop_theme_file_watcher()

    # Clean up VLC resources
    try:
        player.stop()
        media_player = player.get_media_player()
        if media_player:
            media_player.release()
        player.release()
        media_list.release()
        instance.release()
        logging.info("VLC stopped and resources released.")
    except Exception as e:
        logging.error(f"Error releasing VLC resources: {e}")

    # Close GUI (PySide6)
    try:
        from PySide6.QtWidgets import QApplication
        app = QApplication.instance()
        if app:
            app.quit()
    except Exception:
        pass
    logging.info("GUI closed")

# =============================================================================
# MEDIA PLAYER UTILITY FUNCTIONS
# =============================================================================

def get_curr_songtime() -> float:
    """
    Get current playback position of the current song.
    
    Returns:
        float: Current time in seconds, or None if no media is playing
    """
    media_player = player.get_media_player()
    if media_player is None:
        logging.warning("No media player found.")
        return None

    current_time_ms = media_player.get_time()

    if current_time_ms < 0:
        return None
    
    current_time_sec = current_time_ms / 1000
    return current_time_sec

def get_song_length() -> float:
    """
    Get the total length of the current song.
    
    Returns:
        float: Song length in seconds, or None if no media is loaded
    """
    media_player = player.get_media_player()
    if media_player is None:
        logging.warning("No media player found.")
        return None
    length_ms = media_player.get_length()
    
    if length_ms <= 0:
        return None
    
    length_sec = length_ms / 1000
    return length_sec

def set_user_initiated_skip() -> None:
    """Mark that the next song change is user-initiated (skip)."""
    global user_initiated_skip
    user_initiated_skip = True

def on_song_slider_change(sender, app_data, user_data) -> None:
    """
    Handle song progress slider changes.
    
    Args:
        sender: GUI element that triggered the callback (unused)
        app_data: New slider value (0.0 to 1.0)
        user_data: Additional user data (unused)
    """
    global last_user_seek_time
    length = get_song_length()
    if length:
        new_time_ms = int(app_data * length * 1000)
        player.get_media_player().set_time(new_time_ms)
        last_user_seek_time = current_time()

def on_volume_change(sender, app_data, user_data) -> None:
    """
    Handle volume slider changes.
    
    Args:
        sender: GUI element that triggered the callback (unused)
        app_data: New volume value (0.0 to 100.0)
        user_data: Additional user data (unused)
    """
    Settings.VOLUME = int(app_data)  # VLC expects volume 0–100
    player.get_media_player().audio_set_volume(Settings.VOLUME)
    save_config_to_file()

# =============================================================================
# NOTIFICATION FUNCTIONS
# =============================================================================

def show_toast(video_id: str, username: str) -> None:
    """
    Show desktop notification when a song is queued.
    
    Args:
        video_id: YouTube video ID
        username: Username who requested the song
    """
    if Settings.TOAST_NOTIFICATIONS:
        notification.notify(
            title="Requested by: " + username,
            message="Adding '" + get_video_name_fromID(video_id) + "' to queue",
            timeout=5
        )

# =============================================================================
# SONG QUEUE MANAGEMENT
# =============================================================================

def queue_song(video_id: str, requester: str, requesterUUID: str) -> None:
    """
    Add a song to the VLC playlist queue.
    
    Args:
        video_id: YouTube video ID
        requester: Username who requested the song
        requesterUUID: Unique identifier for the requester
    """
    global QUEUE_HISTORY
    youtube_url = "https://music.youtube.com/watch?v=" + video_id
    try:
        # Get direct audio stream URL
        direct_url = get_direct_url(youtube_url)
        media = instance.media_new(direct_url)
        title = get_video_title(youtube_url)
        media.set_meta(vlc.Meta.Title, title)
        media_list.add_media(media)
        
        # Add to queue history
        QUEUE_HISTORY.append({
            "user_id": requesterUUID,
            "username": requester,
            "song_id": video_id,
            "song_title": title
        })
        
        logging.info(f"Queued: {youtube_url} as {title}. Requested by {requester}, UUID: {requesterUUID}")

        # Start playback if player is stopped
        state = player.get_state()
        if state in (vlc.State.Stopped, vlc.State.Ended, vlc.State.NothingSpecial):
            player.play()
        
        # Show notification
        show_toast(video_id, requester)
        
        # Refresh queue history window if open
        refresh_queue_history_list()

    except Exception as e:
        logging.warning(f"Error queuing song {youtube_url}: {e}")

# =============================================================================
# CHAT MESSAGE PROCESSING
# =============================================================================

def on_chat_message(chat_message) -> None:
    """
    Process incoming YouTube live chat messages.
    
    Handles song queue requests from chat users, applying all validation rules
    including rate limiting, banned lists, whitelists, and permission requirements.
    
    Args:
        chat_message: Chat message object from pytchat
    """
    global BANNED_USERS, BANNED_IDS, WHITELISTED_IDS, WHITELISTED_USERS
    message = chat_message.message

    # Only process messages that start with the command prefix
    if message.startswith(f"{Settings.PREFIX}{Settings.QUEUE_COMMAND}"):
        try:
            # Extract user information
            username = chat_message.author.name
            channelid = chat_message.author.channelId
            userismember = chat_message.author.isChatSponsor
            issuperchat = chat_message.type == "superChat"
            superchatvalue = 0

            # Convert superchat value to USD if applicable
            if issuperchat:
                superchatvalue = convert_to_usd(chat_message.amountValue, chat_message.currency)

            current_time = time.time()

            # Parse command - should be "!queue VIDEO_ID"
            parts = message.split()
            if not len(parts) == 2:
                return
            video_id = parts[1]

            # Check rate limiting
            if current_time - user_last_command[username] < Settings.RATE_LIMIT_SECONDS:
                return

            # Check if video is banned
            if any(video_id == x["id"] for x in BANNED_IDS):
                
                logging.info(f"Blocked user {username} ({channelid}) from queuing song '{get_video_name_fromID(video_id)}' (video is banned)")

                if Settings.AUTOBAN_USERS:
                    BANNED_USERS.append({"id": channelid, "name": username})
                    save_banned_users(BANNED_USERS, BANNED_USERS_PATH)
                    refresh_banned_users_list()
                    logging.info(f"Auto-banned user {username} ({channelid}) for requesting banned video")

                return

            # Check if user is banned
            if any(channelid == x["id"] for x in BANNED_USERS):
                logging.info(f"Blocked user {username} ({channelid}) from queuing song '{get_video_name_fromID(video_id)}' (user is banned)")
                return
            
            # Check user whitelist if enforced
            if (Settings.ENFORCE_USER_WHITELIST and not any(channelid == x["id"] for x in WHITELISTED_USERS)):
                logging.info(f"Blocked user {username} ({channelid}) from queuing song '{get_video_name_fromID(video_id)}' (user is not whitelisted)")
                return
            
            # Check video whitelist if enforced
            if (Settings.ENFORCE_ID_WHITELIST and not any(video_id == x["id"] for x in WHITELISTED_IDS)):
                logging.info(f"Blocked user {username} ({channelid}) from queuing song '{get_video_name_fromID(video_id)}' (video is not whitelisted)")
                return
            
            # Handle full YouTube URLs if allowed
            if 'watch?v=' in video_id:
                if Settings.ALLOW_URLS:
                    video_id = video_id.split('watch?v=', 1)[1]
                else:
                    logging.warning(f"user {username} attempted to queue a URL but URL queuing is disabled! (url: {video_id})")
                    return
                
            # Check membership requirement
            if Settings.REQUIRE_MEMBERSHIP and not userismember:
                logging.warning(f"user {username} attempted to queue a song but they are not a member and 'REQUIRE_MEMBERSHIP' is enabled!")
                return

            # Check superchat requirement
            if Settings.REQUIRE_SUPERCHAT and (not issuperchat or superchatvalue < Settings.MINIMUM_SUPERCHAT):
                logging.warning(f"user {username} attempted to queue a song but their message was not a Superchat or had too low of a value!")
                return


            if not is_on_youtube_music(video_id):
                logging.warning(f"user {username} attempted to queue a song that is not available on YouTube Music! (video ID: {video_id})")
                return

            # All checks passed - queue the song
            queue_song(video_id, username, channelid)
            update_now_playing()
            user_last_command[username] = current_time
            
        except Exception as e:
            logging.error("Chat message error: %s", e)
    
# =============================================================================
# GUI UPDATE FUNCTIONS
# =============================================================================

def update_now_playing() -> None:
    """
    Update the 'Now Playing' display in the GUI.
    Uses GUI_BRIDGE when available (PySide6).
    """
    media = player.get_media_player().get_media()
    if media:
        media.parse_with_options(vlc.MediaParseFlag.local, timeout=1000)
        name = media.get_meta(vlc.Meta.Title)
        if not name:
            youtube_url = media.get_mrl()
            name = get_video_title(youtube_url)
        text = f"Now Playing: {name}"
    else:
        text = "Now Playing: Nothing"
    if GUI_BRIDGE:
        GUI_BRIDGE.update_now_playing.emit(text)

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def save_config_to_file() -> None:
    """Save current configuration to config file."""
    # Update theme in Settings before saving
    Settings.THEME = get_current_theme()
    Settings.save()

def extract_id_from_listbox_item(item: str) -> str:
    """
    Extract ID from listbox item in "Name (ID)" format.
    
    Args:
        item: Listbox item string in format "Name (ID)"
        
    Returns:
        str: Extracted ID
    """
    return item.split("(")[-1].strip(")")

def is_on_youtube_music(video_id: str) -> bool:
    return True  # Will add once i find out a way to check properly, I can't find any reliable method as of now

def is_youtube_live(video_id):
    url = f"https://www.youtube.com/watch?v={video_id}"
    headers = {"User-Agent":"Mozilla/5.0"}
    resp = requests.get(url, headers=headers, timeout=10)
    html = resp.text

    # try find JSON
    m = re.search(r"ytInitialPlayerResponse\s*=\s*(\{.+?\});", html)
    if m:
        try:
            data = json.loads(m.group(1))
            if data.get("videoDetails", {}).get("isLive") == True:
                return True
            # or check data.get("playabilityStatus", {}).get("liveStreamability")
        except json.JSONDecodeError:
            pass

    # fallback thumbnail trick
    if "_live.jpg" in html:
        return True

    # fallback badge text
    if "LIVE NOW" in html.upper():
        return True

    return False

def show_download_ui(latest_version: str) -> None:
    """Show download UI elements in the main window."""
    if GUI_BRIDGE:
        GUI_BRIDGE.show_download_ui.emit(latest_version)


def ignore_update_action() -> None:
    """Ignore the current update and hide related UI."""
    global UPDATE_AVAILABLE, IGNORED_VERSION, LATEST_VERSION
    UPDATE_AVAILABLE = False
    IGNORED_VERSION = LATEST_VERSION
    Settings.IGNORED_VERSION = IGNORED_VERSION
    save_config_to_file()
    if GUI_BRIDGE:
        GUI_BRIDGE.hide_update_ui.emit()


def show_update_details_window() -> None:
    """Populate and display the Update Details window (handled by main window menu)."""
    pass


# =============================================================================
# GUI LIST MANAGEMENT FUNCTIONS
# =============================================================================

def refresh_banned_users_list() -> None:
    """Update the banned users list in the GUI."""
    if GUI_BRIDGE:
        GUI_BRIDGE.refresh_list.emit("banned_users_list", [f"{u['name']} ({u['id']})" for u in BANNED_USERS])

def refresh_banned_ids_list() -> None:
    """Update the banned video IDs list in the GUI."""
    if GUI_BRIDGE:
        GUI_BRIDGE.refresh_list.emit("banned_ids_list", [f"{u['name']} ({u['id']})" for u in BANNED_IDS])
    
def refresh_whitelisted_users_list() -> None:
    """Update the whitelisted users list in the GUI."""
    if GUI_BRIDGE:
        GUI_BRIDGE.refresh_list.emit("whitelisted_users_list", [f"{u['name']} ({u['id']})" for u in WHITELISTED_USERS])

def refresh_whitelisted_ids_list() -> None:
    """Update the whitelisted video IDs list in the GUI."""
    if GUI_BRIDGE:
        GUI_BRIDGE.refresh_list.emit("whitelisted_ids_list", [f"{u['name']} ({u['id']})" for u in WHITELISTED_IDS])

def refresh_queue_history_list() -> None:
    """Update the queue history list in the GUI."""
    items = [f"{item['song_title']} - Requested by {item['username']} ({item['user_id']}) [{item['song_id']}]"
             for item in QUEUE_HISTORY]
    if GUI_BRIDGE:
        GUI_BRIDGE.refresh_list.emit("queue_history_list", items)

# =============================================================================
# BAN/UNBAN CALLBACK FUNCTIONS
# =============================================================================

def ban_user_callback() -> None:
    """Legacy DPG callback - use gui.moderation_windows.BannedUsersWindow."""
    pass

def ban_id_callback() -> None:
    """Legacy DPG callback - use gui.moderation_windows.BannedVideosWindow."""
    pass

def whitelist_user_callback() -> None:
    """Legacy DPG callback - use gui.moderation_windows.WhitelistedUsersWindow."""
    pass

def whitelist_id_callback() -> None:
    """Legacy DPG callback - use gui.moderation_windows.WhitelistedVideosWindow."""
    pass

def unban_user_callback() -> None:
    """Legacy DPG callback - use gui.moderation_windows.BannedUsersWindow."""
    pass

def unban_id_callback() -> None:
    """Legacy DPG callback - use gui.moderation_windows.BannedVideosWindow."""
    pass

def unwhitelist_user_callback() -> None:
    """Legacy DPG callback - use gui.moderation_windows.WhitelistedUsersWindow."""
    pass

def unwhitelist_id_callback() -> None:
    """Legacy DPG callback - use gui.moderation_windows.WhitelistedVideosWindow."""
    pass

def extract_queue_item_info(item: str) -> dict:
    """
    Extract information from queue history listbox item.
    
    Format: "Song Title - Requested by Username (User ID) [Song ID]"
    
    Args:
        item: Listbox item string
        
    Returns:
        dict: Dictionary with user_id, username, song_id, song_title
    """
    try:
        # Extract song ID from [Song ID]
        song_id_start = item.rfind('[')
        song_id_end = item.rfind(']')
        if song_id_start != -1 and song_id_end != -1:
            song_id = item[song_id_start + 1:song_id_end]
        else:
            return None
        
        # Extract user ID from (User ID)
        user_id_start = item.rfind('(')
        user_id_end = item.rfind(')')
        if user_id_start != -1 and user_id_end != -1:
            user_id = item[user_id_start + 1:user_id_end]
        else:
            return None
        
        # Extract username and song title
        # Format: "Song Title - Requested by Username (User ID) [Song ID]"
        parts = item.split(" - Requested by ")
        if len(parts) == 2:
            song_title = parts[0]
            username_part = parts[1].split(" (")[0]
            username = username_part
        else:
            return None
        
        return {
            "user_id": user_id,
            "username": username,
            "song_id": song_id,
            "song_title": song_title
        }
    except Exception as e:
        logging.error(f"Error extracting queue item info: {e}")
        return None

def ban_song_from_queue() -> None:
    """Legacy DPG callback - use gui.moderation_windows.QueueHistoryWindow."""
    pass

def ban_user_from_queue() -> None:
    """Legacy DPG callback - use gui.moderation_windows.QueueHistoryWindow."""
    pass
# =============================================================================
# GUI INITIALIZATION & THEMES
# =============================================================================

# GUI state variables
now_playing_text = None
song_slider_tag = "song_slider"
ignore_slider_callback = False

# =============================================================================
# THEME MANAGEMENT FUNCTIONS
# =============================================================================

def select_theme_by_name(theme_name: str) -> None:
    """
    Select a theme by its name.
    
    Args:
        theme_name: Name of the theme to select
    """
    if theme_name is None:
        logging.warning("select_theme_by_name called with None theme_name - this should not happen")
        import traceback
        logging.debug(f"Traceback: {traceback.format_exc()}")
        return
    
    if not isinstance(theme_name, str) or not theme_name.strip():
        logging.warning(f"select_theme_by_name called with invalid theme_name: {theme_name!r}")
        return

    themes = get_available_themes()
    
    if theme_name not in themes:
        logging.warning(f"Theme {theme_name!r} not found. Available themes: {list(themes.keys())}")
        return
    
    set_current_theme(theme_name)
    apply_theme(theme_name)
    
    # Save theme preference to config
    save_theme_to_config()

def select_theme(sender, app_data, user_data) -> None:
    """
    Handle theme selection from dropdown (for combo boxes).
    
    Args:
        sender: GUI element that triggered the callback (unused)
        app_data: Selected theme display name
        user_data: Additional user data (unused)
    """
    if not app_data:
        return
    
    theme_name = get_theme_name_from_display(app_data)
    select_theme_by_name(theme_name)

def update_theme_menu_checks() -> None:
    """Update checkmarks on theme menu items (no-op for PySide6 - main window handles it)."""
    pass

def save_theme_to_config() -> None:
    """Save current theme to config file."""
    save_config_to_file()

def open_url(url: str) -> None:
    """Open a URL in the user's default web browser."""
    try:
        webbrowser.open(url)
    except Exception:
        pass

# =============================================================================
# BACKGROUND THREADING FUNCTIONS
# =============================================================================

def poll_chat() -> None:
    """
    Poll YouTube live chat for new messages.
    
    Runs in a background thread to continuously check for new chat messages
    and process song queue requests.
    """
    while not should_exit:
        if chat.is_alive():
            for message in chat.get().sync_items():
                on_chat_message(message)
        time.sleep(1)

def vlc_loop() -> None:
    """
    Monitor VLC player state and handle automatic playback.
    
    Runs in a background thread to ensure continuous playback when songs end
    and there are more songs in the queue.
    """
    while not should_exit:
        if player.get_state() == vlc.State.Ended and media_list.count() > 0:
            player.play()
        time.sleep(1)

def update_slider_thread() -> None:
    """
    Update the song progress slider in real-time.
    Uses GUI_BRIDGE when available (PySide6).
    """
    while not GUI_BRIDGE and not should_exit:
        time.sleep(0.1)

    while not should_exit:
        time.sleep(0.1)
        media_player = player.get_media_player()
        if not media_player or not GUI_BRIDGE:
            continue

        curr = get_curr_songtime()
        total = get_song_length()
        if curr is None or total is None or total <= 0:
            continue

        time_text = f"{format_time(curr)} / {format_time(total)}"
        GUI_BRIDGE.update_time_text.emit(time_text)

        if current_time() - last_user_seek_time > 1.0:
            progress = curr / total
            GUI_BRIDGE.update_slider.emit(progress)

def update_now_playing_thread() -> None:
    """
    Update the 'Now Playing' display periodically.
    
    Runs in a background thread to keep the current song information
    displayed in the GUI up to date.
    """
    while not should_exit:
        update_now_playing()
        time.sleep(1)


def enable_update_menu_thread() -> None:
    """Enable the update details menu and show download UI when an update is detected."""
    while not should_exit:
        try:
            if UPDATE_AVAILABLE and LATEST_VERSION and GUI_BRIDGE:
                show_download_ui(LATEST_VERSION)
            time.sleep(1)
        except Exception:
            time.sleep(2)

def start_theme_watcher_thread() -> None:
    """Start the theme file watcher after the GUI is ready."""
    while not GUI_BRIDGE and not should_exit:
        time.sleep(0.1)
    if not should_exit:
        start_theme_file_watcher()


# =============================================================================
# APPLICATION STARTUP
# =============================================================================

from gui.config_window import show_config_dialog
from gui.app import run_gui

# Show configuration editor first (blocks until user saves or quits)
invalid_id = False
not_live = False
while not should_exit:
    if not show_config_dialog(invalid_id=invalid_id, not_live=not_live):
        break  # User clicked Quit

    load_config()
    current_video_id = Settings.YOUTUBE_VIDEO_ID
    if initialize_chat():
        if current_video_id == Settings.YOUTUBE_VIDEO_ID and is_youtube_live(Settings.YOUTUBE_VIDEO_ID):
            break
        logging.warning("Video is not a Live. Reloading config window.")
        invalid_id = False
        not_live = True
    else:
        logging.warning("Chat init failed. Reloading config window.")
        invalid_id = True
        not_live = False

if should_exit:
    import sys
    sys.exit(0)

# Load final configuration
load_config()

# Check for updates in background
threading.Thread(target=check_for_updates_wrapper, daemon=True).start()
threading.Thread(target=enable_update_menu_thread, daemon=True).start()

# Start background threads
threading.Thread(target=vlc_loop, daemon=True).start()
threading.Thread(target=poll_chat, daemon=True).start()
threading.Thread(target=update_slider_thread, daemon=True).start()
threading.Thread(target=update_now_playing_thread, daemon=True).start()
threading.Thread(target=start_theme_watcher_thread, daemon=True).start()

# Run GUI (blocks until quit)
import sys
run_gui(sys.modules['__main__'])
