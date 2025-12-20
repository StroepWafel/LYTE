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
from dearpygui.dearpygui import *  # GUI framework
from watchdog.observers import Observer  # File system monitoring
from watchdog.events import FileSystemEventHandler  # File system event handling
# Currency conversion is handled by helpers.currency_helpers

# Local Imports
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

# Update detection state
UPDATE_AVAILABLE: bool = False
LATEST_RELEASE_DETAILS: dict = {}
LATEST_VERSION: str = ""


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
    "AUTOBAN_USERS": "False"                  # Auto-ban users who request banned videos
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

# Load configuration data from files
with open(CONFIG_PATH, 'r', encoding="utf-8") as f:
    config = json.load(f)
with open(BANNED_IDS_PATH, 'r', encoding="utf-8") as f:
    BANNED_IDS = json.load(f)
with open(BANNED_USERS_PATH, "r", encoding="utf-8") as f:
    BANNED_USERS = json.load(f)
with open(WHITELISTED_IDS_PATH, 'r', encoding="utf-8") as f:
    WHITELISTED_IDS = json.load(f)
with open(WHITELISTED_USERS_PATH, "r", encoding="utf-8") as f:
    WHITELISTED_USERS = json.load(f)

# =============================================================================
# CONFIGURATION VARIABLES
# =============================================================================

# Parse configuration values with defaults
YOUTUBE_VIDEO_ID = config.get("YOUTUBE_VIDEO_ID", "")
RATE_LIMIT_SECONDS = config.get('RATE_LIMIT_SECONDS', 3000)
TOAST_NOTIFICATIONS = config.get('TOAST_NOTIFICATIONS', "True").lower() == "true"
PREFIX = config.get('PREFIX', "!")
QUEUE_COMMAND = config.get('QUEUE_COMMAND', "queue")
VOLUME = config.get('VOLUME', 25)
# Handle migration from DARK_MODE to THEME
raw_theme = config.get("THEME") if "THEME" in config else None
if raw_theme is None and "DARK_MODE" in config:
    raw_theme = "dark_theme" if config.get("DARK_MODE", "True").lower() == "true" else "light_theme"
if not isinstance(raw_theme, str) or not raw_theme:
    raw_theme = "dark_theme"
set_current_theme(raw_theme)
ALLOW_URLS = config.get('ALLOW_URLS', "True").lower() == "true"
REQUIRE_MEMBERSHIP = config.get('REQUIRE_MEMBERSHIP', "False").lower() == "true"
REQUIRE_SUPERCHAT = config.get('REQUIRE_SUPERCHAT', "False").lower() == "true"
MINIMUM_SUPERCHAT = config.get('MINIMUM_SUPERCHAT', 3)
ENFORCE_ID_WHITELIST = config.get('ENFORCE_ID_WHITELIST', "False").lower() == "true"
ENFORCE_USER_WHITELIST = config.get('ENFORCE_USER_WHITELIST', "False").lower() == "true"
AUTOREMOVE_SONGS = config.get('AUTOREMOVE_SONGS', "False").lower() == "true"
AUTOBAN_USERS = config.get('AUTOBAN_USERS', "False").lower() == "true"


# User rate limiting - tracks last command time per user
user_last_command = defaultdict(lambda: 0)
# =============================================================================
# VLC MEDIA PLAYER SETUP
# =============================================================================

def on_next_item(event) -> None:
    """
    Callback function triggered when VLC moves to the next item in the playlist.
    
    If auto-remove is enabled, this removes the finished song from the queue.
    
    Args:
        event: VLC event object (unused but required by VLC callback signature)
    """
    if AUTOREMOVE_SONGS:
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
instance = vlc.Instance("--one-instance")  # Prevent multiple VLC instances
player = instance.media_list_player_new()  # Create playlist player
media_list = instance.media_list_new()     # Create empty playlist
player.set_media_list(media_list)          # Assign playlist to player
player.play()                              # Start the player
player.get_media_player().audio_set_volume(VOLUME)  # Set initial volume

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
    global UPDATE_AVAILABLE, LATEST_RELEASE_DETAILS, LATEST_VERSION
    latest_version = check_for_updates(CURRENT_VERSION, TOAST_NOTIFICATIONS)
    if latest_version:
        UPDATE_AVAILABLE = True
        LATEST_VERSION = latest_version
        try:
            LATEST_RELEASE_DETAILS = fetch_latest_release_details() or {}
        except Exception:
            LATEST_RELEASE_DETAILS = {}

        # If the GUI exists, surface UI immediately
        try:
            if does_item_exist("MainWindow"):
                show_download_ui(latest_version)
            if does_item_exist("update_details_menu"):
                configure_item("update_details_menu", enabled=True)
        except Exception:
            pass

# =============================================================================
# TEMPORARY TEST FUNC FOR RELOADING THEMES
# =============================================================================
THEME_MENU_TAG = "theme_menu_root"
THEME_MENU_EMPTY_TAG = "theme_menu_empty"

def rebuild_theme_menu_items() -> None:
    """
    Regenerate the Theme menu items based on the currently available themes.
    """
    parent_tag = THEME_MENU_TAG
    if not does_item_exist(parent_tag):
        logging.warning("Theme menu not found; cannot rebuild theme entries")
        return

    # Remove existing theme menu items we manage (by parent/child relationship)
    try:
        children = get_item_children(parent_tag, 1) or []
        for child_tag in list(children):
            try:
                if isinstance(child_tag, str) and (
                    child_tag.startswith("theme_menu_") or child_tag == THEME_MENU_EMPTY_TAG
                ):
                    delete_item(child_tag)
            except Exception as e:
                logging.error(f"Error removing theme menu item {child_tag}: {e}")
    except Exception as e:
        logging.error(f"Error while cleaning theme menu items: {e}")

    # Rebuild menu entries from available themes
    theme_items = get_theme_dropdown_items()
    if theme_items:
        for display_name in theme_items:
            if not display_name:
                logging.warning("Skipping empty display name in theme menu")
                continue
            theme_name = get_theme_name_from_display(display_name)
            if not theme_name:
                logging.warning(f"Skipping theme menu entry for display name {display_name!r} - got None theme name")
                continue
            is_current = theme_name == get_current_theme()

            # Ensure any stale item with this tag is removed before creating a new one
            menu_tag = f"theme_menu_{theme_name}"
            try:
                if does_item_exist(menu_tag):
                    delete_item(menu_tag)
            except Exception as e:
                logging.error(f"Error deleting existing theme menu item {menu_tag}: {e}")

            def make_theme_callback(tn):
                def callback(sender, app_data, user_data):
                    logging.debug(f"Theme menu callback triggered for theme: {tn!r}")
                    select_theme_by_name(tn)
                return callback

            add_menu_item(
                label=display_name,
                callback=make_theme_callback(theme_name),
                check=is_current,
                tag=menu_tag,
                parent=parent_tag,
            )
    else:
        # Clean up any previous "empty" marker before recreating it
        try:
            if does_item_exist(THEME_MENU_EMPTY_TAG):
                delete_item(THEME_MENU_EMPTY_TAG)
        except Exception as e:
            logging.error(f"Error deleting existing empty theme menu item {THEME_MENU_EMPTY_TAG}: {e}")
        add_menu_item(label="No themes available", enabled=False, tag=THEME_MENU_EMPTY_TAG, parent=parent_tag)

def reload_themes() -> None:
    """Reload all themes from disk."""
    unload_all_themes()
    load_all_themes()
    apply_theme(get_current_theme())
    rebuild_theme_menu_items()

# =============================================================================
# THEME FILE WATCHER
# =============================================================================

class ThemeFileHandler(FileSystemEventHandler):
    """
    File system event handler for theme files.
    
    Automatically reloads themes when theme files are created, modified, or deleted.
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
        # Only process events for JSON files (theme files)
        if event.is_directory:
            return
        
        if not event.src_path.endswith('.json'):
            return
        
        # Debounce rapid changes (e.g., when saving a file triggers multiple events)
        current_time = time.time()
        if current_time - self.last_reload_time < self.reload_debounce_seconds:
            return
        
        # Reload themes when files are created, modified, or deleted
        if event.event_type in ('created', 'modified', 'deleted'):
            self.last_reload_time = current_time
            try:
                logging.info(f"Theme file change detected ({event.event_type}): {os.path.basename(event.src_path)}")
                reload_themes()
                logging.info("Themes reloaded automatically")
            except Exception as e:
                logging.error(f"Error reloading themes after file change: {e}")
                logging.error(traceback.format_exc())

# Global observer instance for theme file watching
theme_observer = None

def start_theme_file_watcher() -> None:
    """
    Start monitoring the themes folder for file changes.
    
    Runs in a background thread and automatically reloads themes when changes are detected.
    """
    global theme_observer
    
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
        chat = pytchat.create(video_id=YOUTUBE_VIDEO_ID)
        return True
    except Exception as e:
        logging.critical(f"Invalid YouTube Video ID '{YOUTUBE_VIDEO_ID}'")
        logging.critical(f"Error {traceback.format_exc()}")
        return False

def load_config() -> None:
    """
    Load and parse all configuration files.
    
    Reloads all configuration data from JSON files and updates global variables.
    This function is called when configuration changes are made through the GUI.
    """
    global config, YOUTUBE_VIDEO_ID, RATE_LIMIT_SECONDS, TOAST_NOTIFICATIONS, PREFIX, QUEUE_COMMAND
    global ALLOW_URLS, VOLUME, REQUIRE_MEMBERSHIP, REQUIRE_SUPERCHAT, MINIMUM_SUPERCHAT
    global BANNED_IDS, BANNED_USERS, WHITELISTED_IDS, WHITELISTED_USERS
    global ENFORCE_USER_WHITELIST, ENFORCE_ID_WHITELIST, AUTOREMOVE_SONGS
    global AUTOBAN_USERS

    # Load all configuration files
    with open(CONFIG_PATH, 'r', encoding="utf-8") as f:
        config = json.load(f)
    BANNED_IDS = load_banned_ids(BANNED_IDS_PATH)
    BANNED_USERS = load_banned_users(BANNED_USERS_PATH)
    WHITELISTED_IDS = load_whitelisted_ids(WHITELISTED_IDS_PATH)
    WHITELISTED_USERS = load_whitelisted_users(WHITELISTED_USERS_PATH)

    # Parse configuration values with defaults
    YOUTUBE_VIDEO_ID = config.get("YOUTUBE_VIDEO_ID", "")
    RATE_LIMIT_SECONDS = config.get("RATE_LIMIT_SECONDS", 10)
    TOAST_NOTIFICATIONS = config.get("TOAST_NOTIFICATIONS", "True").lower() == "true"
    PREFIX = config.get("PREFIX", "!")
    QUEUE_COMMAND = config.get("QUEUE_COMMAND", "queue")
    VOLUME = config.get("VOLUME", 25)
    ALLOW_URLS = config.get("ALLOW_URLS", "True").lower() == "true"
    REQUIRE_MEMBERSHIP = config.get('REQUIRE_MEMBERSHIP', "False").lower() == "true"
    REQUIRE_SUPERCHAT = config.get('REQUIRE_SUPERCHAT', "False").lower() == "true"
    MINIMUM_SUPERCHAT = config.get('MINIMUM_SUPERCHAT', 3)
    ENFORCE_ID_WHITELIST = config.get('ENFORCE_ID_WHITELIST', "False").lower() == "true"
    ENFORCE_USER_WHITELIST = config.get('ENFORCE_USER_WHITELIST', "False").lower() == "true"
    AUTOREMOVE_SONGS = config.get('AUTOREMOVE_SONGS', "False").lower() == "true"
    AUTOBAN_USERS = config.get('AUTOBAN_USERS', "False").lower() == "true"

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

    # Close GUI
    stop_dearpygui()
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
    global VOLUME
    VOLUME = int(app_data)  # VLC expects volume 0–100
    player.get_media_player().audio_set_volume(VOLUME)
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
    if TOAST_NOTIFICATIONS:
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
    youtube_url = "https://music.youtube.com/watch?v=" + video_id
    try:
        # Get direct audio stream URL
        direct_url = get_direct_url(youtube_url)
        media = instance.media_new(direct_url)
        title = get_video_title(youtube_url)
        media.set_meta(vlc.Meta.Title, title)
        media_list.add_media(media)
        
        logging.info(f"Queued: {youtube_url} as {title}. Requested by {requester}, UUID: {requesterUUID}")

        # Start playback if player is stopped
        state = player.get_state()
        if state in (vlc.State.Stopped, vlc.State.Ended, vlc.State.NothingSpecial):
            player.play()
        
        # Show notification
        show_toast(video_id, requester)

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
    global ENFORCE_ID_WHITELIST, ENFORCE_USER_WHITELIST
    message = chat_message.message

    # Only process messages that start with the command prefix
    if message.startswith(f"{PREFIX}{QUEUE_COMMAND}"):
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
            if current_time - user_last_command[username] < RATE_LIMIT_SECONDS:
                return

            # Check if video is banned
            if any(video_id == x["id"] for x in BANNED_IDS):
                
                logging.info(f"Blocked user {username} ({channelid}) from queuing song '{get_video_name_fromID(video_id)}' (video is banned)")

                if AUTOBAN_USERS:
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
            if (ENFORCE_USER_WHITELIST and not any(channelid == x["id"] for x in WHITELISTED_USERS)):
                logging.info(f"Blocked user {username} ({channelid}) from queuing song '{get_video_name_fromID(video_id)}' (user is not whitelisted)")
                return
            
            # Check video whitelist if enforced
            if (ENFORCE_ID_WHITELIST and not any(video_id == x["id"] for x in WHITELISTED_IDS)):
                logging.info(f"Blocked user {username} ({channelid}) from queuing song '{get_video_name_fromID(video_id)}' (video is not whitelisted)")
                return
            
            # Handle full YouTube URLs if allowed
            if 'watch?v=' in video_id:
                if ALLOW_URLS:
                    video_id = video_id.split('watch?v=', 1)[1]
                else:
                    logging.warning(f"user {username} attempted to queue a URL but URL queuing is disabled! (url: {video_id})")
                    return
                
            # Check membership requirement
            if REQUIRE_MEMBERSHIP and not userismember:
                logging.warning(f"user {username} attempted to queue a song but they are not a member and 'REQUIRE_MEMBERSHIP' is enabled!")
                return

            # Check superchat requirement
            if REQUIRE_SUPERCHAT and (not issuperchat or superchatvalue < MINIMUM_SUPERCHAT):
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
    
    Fetches the current media title and updates the GUI text element.
    """
    media = player.get_media_player().get_media()
    if media:
        media.parse_with_options(vlc.MediaParseFlag.local, timeout=1000)
        name = media.get_meta(vlc.Meta.Title)
        if not name:
            youtube_url = media.get_mrl()
            name = get_video_title(youtube_url)
        set_value(now_playing_text, f"Now Playing: {name}")
    else:
        set_value(now_playing_text, "Now Playing: Nothing")

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def save_config_to_file() -> None:
    """Save current configuration to config file."""
    updated_config = {
        "YOUTUBE_VIDEO_ID": YOUTUBE_VIDEO_ID,
        "RATE_LIMIT_SECONDS": RATE_LIMIT_SECONDS,
        "TOAST_NOTIFICATIONS": str(TOAST_NOTIFICATIONS),
        "PREFIX": PREFIX,
        "QUEUE_COMMAND": QUEUE_COMMAND,
        "VOLUME": VOLUME,
        "THEME": get_current_theme(),
        "ALLOW_URLS": str(ALLOW_URLS),
        "REQUIRE_MEMBERSHIP": str(REQUIRE_MEMBERSHIP),
        "REQUIRE_SUPERCHAT": str(REQUIRE_SUPERCHAT),
        "MINIMUM_SUPERCHAT": MINIMUM_SUPERCHAT,
        "ENFORCE_ID_WHITELIST": str(ENFORCE_ID_WHITELIST),
        "ENFORCE_USER_WHITELIST": str(ENFORCE_USER_WHITELIST),
        "AUTOREMOVE_SONGS": str(AUTOREMOVE_SONGS),
        "AUTOBAN_USERS": str(AUTOBAN_USERS)
    }
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(updated_config, f, indent=4)

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
    """
    Show download UI elements in the main window.
    
    Args:
        latest_version: The latest version available
    """
    try:
        # Add update notification text
        if not does_item_exist("update_notification"):
            add_text(f"Update Available: v{latest_version} (Current: v{CURRENT_VERSION})", 
                    color=(255, 200, 100), tag="update_notification", parent="MainWindow")
        
        # Add download status text
        if not does_item_exist("download_status"):
            add_text("", tag="download_status", parent="MainWindow")
        
        # Note: Progress bar moved to Update Details window
            
    except Exception as e:
        logging.error(f"Error showing download UI: {e}")


def ignore_update_action() -> None:
    """Ignore the current update and hide related UI."""
    global UPDATE_AVAILABLE, LATEST_VERSION
    try:
        UPDATE_AVAILABLE = False
        LATEST_VERSION = ""
        if does_item_exist("update_details_menu"):
            configure_item("update_details_menu", enabled=False)
        # Hide download UI elements if present
        for tag in ("update_notification", "download_button", "download_status"):
            if does_item_exist(tag):
                try:
                    configure_item(tag, show=False)
                except Exception:
                    pass
        # Close details window if open
        if does_item_exist("UpdateDetailsWindow"):
            configure_item("UpdateDetailsWindow", show=False)
    except Exception as e:
        logging.error(f"Error ignoring update: {e}")


def show_update_details_window() -> None:
    """Populate and display the Update Details window."""
    try:
        name = LATEST_RELEASE_DETAILS.get("name", "Latest Release")
        version = LATEST_RELEASE_DETAILS.get("version", LATEST_VERSION or "")
        body = LATEST_RELEASE_DETAILS.get("body", "")
        set_value("update_release_title", f"Release: {name}")
        set_value("update_release_version", f"Version: v{version}" if version else "")
        set_value("update_release_body", body)
        configure_item("UpdateDetailsWindow", show=True)
    except Exception as e:
        logging.error(f"Error showing update details window: {e}")


# =============================================================================
# GUI LIST MANAGEMENT FUNCTIONS
# =============================================================================

def refresh_banned_users_list() -> None:
    """Update the banned users list in the GUI."""
    configure_item("banned_users_list",
                   items=[f"{u['name']} ({u['id']})" for u in BANNED_USERS])

def refresh_banned_ids_list() -> None:
    """Update the banned video IDs list in the GUI."""
    configure_item("banned_ids_list",
                   items=[f"{u['name']} ({u['id']})" for u in BANNED_IDS])
    
def refresh_whitelisted_users_list() -> None:
    """Update the whitelisted users list in the GUI."""
    configure_item("whitelisted_users_list",
                   items=[f"{u['name']} ({u['id']})" for u in WHITELISTED_USERS])

def refresh_whitelisted_ids_list() -> None:
    """Update the whitelisted video IDs list in the GUI."""
    configure_item("whitelisted_ids_list",
                   items=[f"{u['name']} ({u['id']})" for u in WHITELISTED_IDS])

# =============================================================================
# BAN/UNBAN CALLBACK FUNCTIONS
# =============================================================================

def _add_item_with_async_name_fetch(
    item_id: str,
    item_list: list,
    input_tag: str,
    save_func,
    refresh_func,
    fetch_name_func,
    item_type: str
) -> None:
    """
    Helper function to add an item to a list with placeholder name,
    then fetch the real name in a background thread.
    
    Args:
        item_id: ID of the item to add
        item_list: List to add the item to (will be modified)
        input_tag: GUI input tag to clear after adding
        save_func: Function to save the list to file
        refresh_func: Function to refresh the GUI list
        fetch_name_func: Function to fetch the real name (takes item_id)
        item_type: Type of item for error messages (e.g., "user", "video")
    """
    if item_id and all(u["id"] != item_id for u in item_list):
        # Add immediately with placeholder
        item_list.append({"id": item_id, "name": "Loading..."})
        save_func(item_list)
        refresh_func()
        set_value(input_tag, "")  # clear input

        # Fetch real name in background
        def fetch_and_update():
            try:
                real_name = fetch_name_func(item_id)
                # Update the entry in the list
                for u in item_list:
                    if u["id"] == item_id:
                        u["name"] = real_name
                        break
                save_func(item_list)
                # Update the listbox in the GUI thread
                refresh_func()
            except Exception as e:
                logging.error(f"Error fetching {item_type} name for {item_id}: {e}")

        threading.Thread(target=fetch_and_update, daemon=True).start()

def ban_user_callback() -> None:
    """
    Handle banning a user from the GUI.
    
    Adds user to banned list immediately with placeholder name,
    then fetches real channel name in background thread.
    """
    global BANNED_USERS
    user_to_ban = get_value("ban_user_input").strip()
    _add_item_with_async_name_fetch(
        user_to_ban,
        BANNED_USERS,
        "ban_user_input",
        lambda lst: save_banned_users(lst, BANNED_USERS_PATH),
        refresh_banned_users_list,
        fetch_channel_name,
        "channel"
    )

def ban_id_callback() -> None:
    """
    Handle banning a video ID from the GUI.
    
    Adds video to banned list immediately with placeholder name,
    then fetches real video name in background thread.
    """
    global BANNED_IDS
    id_to_ban = get_value("ban_id_input").strip()
    _add_item_with_async_name_fetch(
        id_to_ban,
        BANNED_IDS,
        "ban_id_input",
        lambda lst: save_banned_ids(lst, BANNED_IDS_PATH),
        refresh_banned_ids_list,
        get_video_name_fromID,
        "video"
    )

def whitelist_user_callback() -> None:
    """
    Handle whitelisting a user from the GUI.
    
    Adds user to whitelisted list immediately with placeholder name,
    then fetches real channel name in background thread.
    """
    global WHITELISTED_USERS
    user_to_whitelist = get_value("whitelist_user_input").strip()
    _add_item_with_async_name_fetch(
        user_to_whitelist,
        WHITELISTED_USERS,
        "whitelist_user_input",
        lambda lst: save_whitelisted_users(lst, WHITELISTED_USERS_PATH),
        refresh_whitelisted_users_list,
        fetch_channel_name,
        "channel"
    )

def whitelist_id_callback() -> None:
    """
    Handle whitelisting a video ID from the GUI.
    
    Adds video to whitelisted list immediately with placeholder name,
    then fetches real video name in background thread.
    """
    global WHITELISTED_IDS
    id_to_whitelist = get_value("whitelist_id_input").strip()
    _add_item_with_async_name_fetch(
        id_to_whitelist,
        WHITELISTED_IDS,
        "whitelist_id_input",
        lambda lst: save_whitelisted_ids(lst, WHITELISTED_IDS_PATH),
        refresh_whitelisted_ids_list,
        get_video_name_fromID,
        "video"
    )

def unban_user_callback() -> None:
    """Remove selected user from banned users list."""
    global BANNED_USERS
    selected = get_value("banned_users_list")
    if selected:
        selected_id = extract_id_from_listbox_item(selected)
        BANNED_USERS = [u for u in BANNED_USERS if u["id"] != selected_id]
        save_banned_users(BANNED_USERS, BANNED_USERS_PATH)
        refresh_banned_users_list()

def unban_id_callback() -> None:
    """Remove selected video ID from banned video IDs list."""
    global BANNED_IDS
    selected = get_value("banned_ids_list")
    if selected:
        selected_id = extract_id_from_listbox_item(selected)
        BANNED_IDS = [u for u in BANNED_IDS if u["id"] != selected_id]
        save_banned_ids(BANNED_IDS, BANNED_IDS_PATH)
        refresh_banned_ids_list()

def unwhitelist_user_callback() -> None:
    """Remove selected user from whitelisted users list."""
    global WHITELISTED_USERS
    selected = get_value("whitelisted_users_list")
    if selected:
        selected_id = extract_id_from_listbox_item(selected)
        WHITELISTED_USERS = [u for u in WHITELISTED_USERS if u["id"] != selected_id]
        save_whitelisted_users(WHITELISTED_USERS, WHITELISTED_USERS_PATH)
        refresh_whitelisted_users_list()

def unwhitelist_id_callback() -> None:
    """Remove selected video ID from whitelisted video IDs list."""
    global WHITELISTED_IDS
    selected = get_value("whitelisted_ids_list")
    if selected:
        selected_id = extract_id_from_listbox_item(selected)
        WHITELISTED_IDS = [u for u in WHITELISTED_IDS if u["id"] != selected_id]
        save_whitelisted_ids(WHITELISTED_IDS, WHITELISTED_IDS_PATH)
        refresh_whitelisted_ids_list()
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
    
    # Update menu checkmarks
    update_theme_menu_checks()
    
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
    """Update checkmarks on theme menu items."""
    themes = get_available_themes()
    if not themes:
        return
    
    current = get_current_theme()
    for theme_name in themes.keys():
        menu_tag = f"theme_menu_{theme_name}"
        if does_item_exist(menu_tag):
            configure_item(menu_tag, check=(theme_name == current))

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
# GUI CONSTRUCTION FUNCTIONS
# =============================================================================

def build_gui() -> None:

    
    """
    Build and display the main application GUI.
    
    Creates the main control panel window with all controls for managing
    the music queue, settings, and user/video management.
    """
    create_context()
    global now_playing_text

    def update_settings_from_menu() -> None:
        """Update configuration from GUI settings and save to file."""
        global YOUTUBE_VIDEO_ID, RATE_LIMIT_SECONDS, TOAST_NOTIFICATIONS, PREFIX, QUEUE_COMMAND
        global ALLOW_URLS, VOLUME, REQUIRE_MEMBERSHIP, REQUIRE_SUPERCHAT, MINIMUM_SUPERCHAT
        global ENFORCE_USER_WHITELIST, ENFORCE_ID_WHITELIST, AUTOREMOVE_SONGS
        global AUTOBAN_USERS
        
        # Update global variables from GUI inputs
        RATE_LIMIT_SECONDS = int(get_value("rate_limit_input"))
        TOAST_NOTIFICATIONS = str(get_value("toast_checkbox"))
        PREFIX = get_value("prefix_input")
        QUEUE_COMMAND = get_value("queue_input")
        ALLOW_URLS = get_value("allowURLs_checkbox")
        REQUIRE_MEMBERSHIP = get_value("require_membership_checkbox")
        REQUIRE_SUPERCHAT = get_value("require_superchat_checkbox")
        MINIMUM_SUPERCHAT = get_value("minimum_superchat_input")
        ENFORCE_USER_WHITELIST = get_value("enforce_user_whitelist_checkbox")
        ENFORCE_ID_WHITELIST = get_value("enforce_id_whitelist_checkbox")
        AUTOREMOVE_SONGS = get_value("autoremove_songs_checkbox")
        AUTOBAN_USERS = get_value("autoban_users_checkbox")

        # Save updated configuration to file
        save_config_to_file()

    # =============================================================================
    # MAIN WINDOW CONSTRUCTION
    # =============================================================================
    
    with window(label="LYTE Control Panel", tag="MainWindow", width=700, height=380, pos=(100, 100)):
        set_primary_window("MainWindow", True)

        add_spacer(height=15)

        with menu_bar() as _:
            with menu(label="File"):
                add_menu_item(label="Reload Config", callback=load_config, tag="reload_config_menu")
                add_menu_item(label="Quit", callback=lambda: quit_program(), tag="quit_menu")
                
                with tooltip("reload_config_menu"):
                    add_text("Reload configuration from file")
                with tooltip("quit_menu"):
                    add_text("Exit the application")
                    
            with menu(label="View"):
                with menu(label="Theme", tag=THEME_MENU_TAG):
                    rebuild_theme_menu_items()
                add_menu_item(label="Open Themes Folder", callback=lambda: show_folder(THEMES_FOLDER), tag="open_themes_folder_menu")
                add_menu_item(label="Reload themes", callback=lambda: reload_themes(), tag="reload_themes")

                with tooltip("open_themes_folder_menu"):
                    add_text("Open the folder where themes are stored")
                with tooltip("reload_themes"):
                    add_text("Reload themes from the themes folder")


            with menu(label="Moderation"):
                add_menu_item(label="Manage Banned Users", tag="banned_users_menu",
                            callback=lambda: (load_banned_users_wrapper(), refresh_banned_users_list(), configure_item("BannedUsersWindow", show=True)))
                add_menu_item(label="Manage Banned Videos", tag="banned_videos_menu",
                            callback=lambda: (load_banned_ids_wrapper(), refresh_banned_ids_list(), configure_item("BannedIDsWindow", show=True)))
                add_menu_item(label="Manage Whitelisted Users", tag="whitelist_users_menu",
                            callback=lambda: (load_whitelisted_users_wrapper(), refresh_whitelisted_users_list(), configure_item("WhitelistedUsersWindow", show=True)))
                add_menu_item(label="Manage Whitelisted Videos", tag="whitelist_videos_menu",
                            callback=lambda: (load_whitelisted_ids_wrapper(), refresh_whitelisted_ids_list(), configure_item("WhitelistedIDsWindow", show=True)))
                add_menu_item(label="Settings", tag="settings_menu",
                            callback=lambda: (load_config(), configure_item("SettingsWindow", show=True)))
                
                
                with tooltip("banned_users_menu"):
                    add_text("Manage users who are not allowed to request songs")
                with tooltip("banned_videos_menu"):
                    add_text("Manage videos that are not allowed to be requested")
                with tooltip("whitelist_users_menu"):
                    add_text("Manage users who are allowed to request songs when whitelist is enforced")
                with tooltip("whitelist_videos_menu"):
                    add_text("Manage videos that are allowed to be requested when whitelist is enforced")
                with tooltip("settings_menu"):
                    add_text("Manage general settings")


            with menu(label="Help"):
                add_menu_item(label=f"Version: {CURRENT_VERSION}", enabled=False, tag="version_menu")
                add_separator()
                add_menu_item(label="Check for Updates", callback=check_for_updates_wrapper, tag="check_updates_menu")
                add_menu_item(label="View Update Details...", callback=lambda: show_update_details_window(), tag="update_details_menu", enabled=False)
                add_menu_item(label="Open GitHub Issues", callback=lambda: open_url("https://github.com/StroepWafel/LYTE/issues"), tag="github_issues_menu")
                add_menu_item(label="Open General Documentation", callback=lambda: open_url("https://www.stroepwafel.au/LYTE/documentation"), tag="general_docs_menu")
                add_menu_item(label="Open Theme Documentation", callback=lambda: open_url("https://www.stroepwafel.au/LYTE/documentation/theme-documentation"), tag="theme_docs_menu")
                
                with tooltip("version_menu"):
                    add_text("Current version of LYTE")
                with tooltip("check_updates_menu"):
                    add_text("Check if a newer version is available")
                with tooltip("update_details_menu"):
                    add_text("View the latest release notes and actions")
                with tooltip("github_issues_menu"):
                    add_text("Open the GitHub issues page in your browser")
                with tooltip("general_docs_menu"):
                    add_text("Open the general documentation in your browser")
                with tooltip("theme_docs_menu"):
                    add_text("Open the theme documentation in your browser")
                    
        # =============================================================================
        # NOW PLAYING DISPLAY
        # =============================================================================
        
        now_playing_text = add_text("Now Playing: Nothing", wrap=600)
        add_separator()
        add_spacer(height=15)

        # =============================================================================
        # PLAYBACK CONTROLS
        # =============================================================================
        
        with group(horizontal=True):
            add_button(label="Play / Pause", callback=lambda: player.pause(), width=130, tag="play_button")
            add_spacer(width=10)
            add_button(label="Previous", callback=lambda: [player.previous(), update_now_playing()], width=110, tag="prev_button")
            add_spacer(width=10)
            add_button(label="Next", callback=lambda: [player.next(), update_now_playing()], width=110, tag="next_button")
            add_spacer(width=10)
            add_button(label="Refresh", callback=update_now_playing, width=110, tag="refresh_button")

            # Tooltips for playback controls
            with tooltip("play_button"):
                add_text("Play/Pause the current song")
            with tooltip("prev_button"):
                add_text("Skip to the previous song")
            with tooltip("next_button"):
                add_text("Skip to the next song")
            with tooltip("refresh_button"):
                add_text("Refresh the song info")

        add_spacer(height=5)

        # =============================================================================
        # VOLUME CONTROL
        # =============================================================================
        
        add_text("Volume")
        add_slider_float(label="", default_value=config["VOLUME"], min_value=0.0, max_value=100.0, 
                        width=400, callback=on_volume_change, format="%.0f", tag="volume_slider")
        
        with tooltip("volume_slider"):
            add_text("Adjust the playback volume")

        add_spacer(height=5)

        # =============================================================================
        # SONG PROGRESS CONTROL
        # =============================================================================
        
        add_text("Song Progress")
        with group(horizontal=True):
            add_slider_float(tag=song_slider_tag, default_value=0.0, min_value=0.0, max_value=1.0,
                            width=400, callback=on_song_slider_change, format="")
            add_text("00:00 / 00:00", tag="song_time_text")
            
        with tooltip(song_slider_tag):
            add_text("Drag to seek to a different position in the song")
        with tooltip("song_time_text"):
            add_text("Current position / Total duration")

        # =============================================================================
        # CONSOLE OUTPUT
        # =============================================================================
        
        add_input_text(label="", tag="console_text", multiline=True, readonly=True, height=200, width=1300)
        
        with tooltip("console_text"):
            add_text("Log messages and application status")
        
        # =============================================================================
        # GUI LOGGER CLASS
        # =============================================================================
        
        class GuiLogger(logging.Handler):
            """
            Custom logging handler that displays log messages in the GUI console.
            
            Keeps only the last 100 log lines to prevent memory issues.
            """
            def emit(self, record):
                try:
                    msg = self.format(record)
                    if does_item_exist("console_text"):
                        current_text = get_value("console_text")
                        # Keep last 100 lines max
                        lines = current_text.splitlines()
                        lines.append(msg)
                        if len(lines) > 100:
                            lines = lines[-100:]
                        set_value("console_text", "\n".join(lines))
                except Exception:
                    pass

        # Set up GUI logging
        gui_handler = GuiLogger()
        gui_handler.setLevel(logging.INFO)
        gui_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logging.getLogger().addHandler(gui_handler)

        # =============================================================================
        # SETTINGS WINDOW
        # =============================================================================

        with window(label="Settings", tag="SettingsWindow", show=False, width=750, height=410):
            add_text("Settings")
            add_separator()

            # Command configuration
            add_input_text(label="Command Prefix", default_value=config["PREFIX"], tag="prefix_input")
            add_input_text(label="Queue Command", default_value=config["QUEUE_COMMAND"], tag="queue_input")
            add_input_int(label="Rate Limit (seconds)", default_value=config["RATE_LIMIT_SECONDS"], tag="rate_limit_input")
            
            # Notification settings
            add_checkbox(label="Enable Toast Notifications", default_value=config["TOAST_NOTIFICATIONS"].lower() == "true", tag="toast_checkbox")
            
            # Request permissions
            add_checkbox(label="Allow URL Requests", default_value=config["ALLOW_URLS"].lower() == "true", tag="allowURLs_checkbox")
            add_checkbox(label="Require Membership to request", default_value=config["REQUIRE_MEMBERSHIP"].lower() == "true", tag="require_membership_checkbox")
            add_checkbox(label="Require Superchat to request", default_value=config["REQUIRE_SUPERCHAT"].lower() == "true", tag="require_superchat_checkbox")
            add_input_int(label="Minimum Superchat cost (USD)", default_value=config["MINIMUM_SUPERCHAT"], tag="minimum_superchat_input")
            
            # Whitelist enforcement
            add_checkbox(label="Enforce User Whitelist", default_value=config["ENFORCE_USER_WHITELIST"].lower() == "true", tag="enforce_user_whitelist_checkbox")
            add_checkbox(label="Enforce Song Whitelist", default_value=config["ENFORCE_ID_WHITELIST"].lower() == "true", tag="enforce_id_whitelist_checkbox")
            add_checkbox(label="Autoban users", default_value=config["AUTOBAN_USERS"].lower() == "true", tag="autoban_users_checkbox")
            
            # Queue management
            add_checkbox(label="Automatically remove songs", default_value=config["AUTOREMOVE_SONGS"].lower() == "true", tag="autoremove_songs_checkbox")

            add_spacer(height=10)
            add_button(label="Update Settings", callback=lambda: (update_settings_from_menu(), configure_item("SettingsWindow", show=False)))

            # =============================================================================
            # SETTINGS TOOLTIPS
            # =============================================================================
            
            with tooltip("prefix_input"):
                add_text("The prefix before a command, useful if you already have another chatbot")
                add_text("Can be any number of alphanumerical characters")
            with tooltip("queue_input"):
                add_text("The command users need to enter after the prefix to queue a song. Cannot contain spaces")
            with tooltip("rate_limit_input"):
                add_text("How long a user has to wait before they can queue another song, in seconds")
            with tooltip("toast_checkbox"):
                add_text("Whether or not to show desktop notifications when a song is queued")
            with tooltip("allowURLs_checkbox"):
                add_text("Whether or not users can request songs with full URLs (I.e; the full 'https://' link)")
            with tooltip("require_membership_checkbox"):
                add_text("Whether or not users need to be a member of the channel to request a song")
            with tooltip("require_superchat_checkbox"):
                add_text("Whether or not users need to send a superchat to request a song")
            with tooltip("minimum_superchat_input"):
                add_text("The minimum value superchat (in USD) that a user must spend to request a song")
                add_text("Supplementary to 'Require Superchat to request'")
            with tooltip("enforce_user_whitelist_checkbox"):
                add_text("Whether or not to enforce the user Whitelist")
            with tooltip("enforce_id_whitelist_checkbox"):
                add_text("Whether or not to enforce the song ID Whitelist")
            with tooltip("autoremove_songs_checkbox"):
                add_text("Whether or not to automatically remove finished/skipped songs from the queue (applies after restart)")
            with tooltip("autoban_users_checkbox"):
                add_text("Whether or not to automatically ban users who try to request banned songs")

        # =============================================================================
        # BANNED USERS MANAGEMENT WINDOW
        # =============================================================================
        
        with window(label="Banned Users", tag="BannedUsersWindow", show=False, width=400, height=400):
            add_text("Manage Banned Users")
            add_separator()

            # Display banned users list
            add_listbox(items=[f"{u['name']} ({u['id']})" for u in BANNED_USERS], 
                    tag="banned_users_list", width=350, num_items=8)
            add_spacer(height=10)

            # Add new banned user
            add_input_text(label="Add User ID", tag="ban_user_input", width=250)
            add_button(label="Ban User", callback=lambda: ban_user_callback(), tag="ban_user_button")

            add_spacer(height=10)

            # Remove selected user
            add_button(label="Unban Selected", callback=lambda: unban_user_callback(), tag="unban_user_button")
            
            with tooltip("ban_user_input"):
                add_text("Enter the YouTube user ID to ban")
            with tooltip("ban_user_button"):
                add_text("Add the user to the banned list")
            with tooltip("unban_user_button"):
                add_text("Remove the selected user from the banned list")

            add_spacer(height=20)
            add_button(label="Close", callback=lambda: configure_item("BannedUsersWindow", show=False))


        # =============================================================================
        # UPDATE DETAILS WINDOW
        # =============================================================================
        with window(label="Update Details", tag="UpdateDetailsWindow", show=False, width=600, height=550):
            add_text("Update Details")
            add_separator()
            add_text("", tag="update_release_title")
            add_text("", tag="update_release_version")
            add_spacer(height=10)
            add_text("Changelog:")
            add_input_text(label="", tag="update_release_body", multiline=True, readonly=True, width=560, height=330)
            add_spacer(height=10)
            with group(horizontal=True):
                add_button(label="Open Release Page", tag="open_release_button",
                        callback=lambda: open_url(LATEST_RELEASE_DETAILS.get("html_url", "https://github.com/StroepWafel/LYTE/releases/latest")))
                add_button(label="Download Installer", tag="update_download_button", callback=download_installer)
                add_button(label="Run Installer", tag="update_run_button", callback=run_installer_wrapper)
                add_button(label="Ignore This Update", tag="ignore_update_button", callback=lambda: ignore_update_action())
            with tooltip("open_release_button"):
                add_text("Open the release page in your browser")
            with tooltip("update_download_button"):
                add_text("Download the latest installer")
            with tooltip("update_run_button"):
                add_text("Run the downloaded installer")
            with tooltip("ignore_update_button"):
                add_text("Hide this update notification")

        # =============================================================================
        # BANNED VIDEOS MANAGEMENT WINDOW
        # =============================================================================
        
        with window(label="Banned Videos", tag="BannedIDsWindow", show=False, width=400, height=400):
            add_text("Manage Banned Videos")
            add_separator()

            # Display banned videos list
            add_listbox(items=[f"{u['name']} ({u['id']})" for u in BANNED_IDS], 
                    tag="banned_ids_list", width=350, num_items=8)
            add_spacer(height=10)

            # Add new banned video
            add_input_text(label="Add Video ID", tag="ban_id_input", width=250)
            add_button(label="Ban Video", callback=lambda: ban_id_callback(), tag="ban_video_button")

            add_spacer(height=10)

            # Remove selected video
            add_button(label="Unban Selected", callback=lambda: unban_id_callback(), tag="unban_video_button")
            
            with tooltip("ban_id_input"):
                add_text("Enter the YouTube video ID to ban")
            with tooltip("ban_video_button"):
                add_text("Add the video to the banned list")
            with tooltip("unban_video_button"):
                add_text("Remove the selected video from the banned list")

            add_spacer(height=20)
            add_button(label="Close", callback=lambda: configure_item("BannedIDsWindow", show=False))

        # =============================================================================
        # WHITELISTED USERS MANAGEMENT WINDOW
        # =============================================================================
        
        with window(label="Whitelisted Users", tag="WhitelistedUsersWindow", show=False, width=400, height=400):
            add_text("Manage Whitelisted Users")
            add_separator()

            # Display whitelisted users list
            add_listbox(items=[f"{u['name']} ({u['id']})" for u in WHITELISTED_USERS], 
                    tag="whitelisted_users_list", width=350, num_items=8)
            add_spacer(height=10)

            # Add new whitelisted user
            add_input_text(label="Add User ID", tag="whitelist_user_input", width=250)
            add_button(label="Whitelist User", callback=lambda: whitelist_user_callback(), tag="whitelist_user_button")

            add_spacer(height=10)

            # Remove selected user
            add_button(label="Un-Whitelist Selected", callback=lambda: unwhitelist_user_callback(), tag="unwhitelist_user_button")
            
            with tooltip("whitelist_user_input"):
                add_text("Enter the YouTube user ID to whitelist")
            with tooltip("whitelist_user_button"):
                add_text("Add the user to the whitelist")
            with tooltip("unwhitelist_user_button"):
                add_text("Remove the selected user from the whitelist")

            add_spacer(height=20)
            add_button(label="Close", callback=lambda: configure_item("WhitelistedUsersWindow", show=False))

        # =============================================================================
        # WHITELISTED VIDEOS MANAGEMENT WINDOW
        # =============================================================================
        
        with window(label="Whitelisted Videos", tag="WhitelistedIDsWindow", show=False, width=400, height=400):
            add_text("Manage Whitelisted Videos")
            add_separator()

            # Display whitelisted videos list
            add_listbox(items=[f"{u['name']} ({u['id']})" for u in WHITELISTED_IDS], 
                    tag="whitelisted_ids_list", width=350, num_items=8)
            add_spacer(height=10)

            # Add new whitelisted video
            add_input_text(label="Add Video ID", tag="whitelist_id_input", width=250)
            add_button(label="Whitelist Video", callback=lambda: whitelist_id_callback(), tag="whitelist_video_button")

            add_spacer(height=10)

            # Remove selected video
            add_button(label="Un-Whitelist Selected", callback=lambda: unwhitelist_id_callback(), tag="unwhitelist_video_button")
            
            with tooltip("whitelist_id_input"):
                add_text("Enter the YouTube video ID to whitelist")
            with tooltip("whitelist_video_button"):
                add_text("Add the video to the whitelist")
            with tooltip("unwhitelist_video_button"):
                add_text("Remove the selected video from the whitelist")

            add_spacer(height=20)
            add_button(label="Close", callback=lambda: configure_item("WhitelistedIDsWindow", show=False))
    
    # =============================================================================
    # GUI FINALIZATION
    # =============================================================================
    
    try:
        create_default_theme_files()
        load_all_themes()
        # Ensure current theme exists, fallback to first available or dark_theme
        themes = get_available_themes()
        current = get_current_theme()
        if current not in themes:
            if themes:
                set_current_theme(list(themes.keys())[0])
            else:
                set_current_theme("dark_theme")
        create_viewport(title='LYTE Control Panel', width=1330, height=500)
        apply_theme(get_current_theme())
        setup_dearpygui()
        show_viewport()
        set_exit_callback(on_close_attempt)
        configure_viewport(0, resizable=True, min_width=700, min_height=380)
        start_dearpygui()
    except Exception as e:
        logging.error(f"Error in build_gui: {e}")
        logging.error(traceback.format_exc())
        raise
    finally:
        destroy_context()  


def show_config_menu(invalid_id: bool = False, not_live: bool = False) -> None:
    """
    Display the initial configuration menu.
    
    Args:
        invalid_id: Whether to show an invalid ID warning
    """
    create_context()
    
    # Load themes before creating the window so dropdown can access them
    try:
        create_default_theme_files()
        load_all_themes()
    except Exception as theme_error:
        logging.error(f"Error loading themes: {theme_error}")
        logging.error(traceback.format_exc())
        # Continue anyway - we'll use default theme
    
    def save_and_start_callback() -> None:
        """Save configuration and start the application."""
        global YOUTUBE_VIDEO_ID, RATE_LIMIT_SECONDS, TOAST_NOTIFICATIONS, PREFIX, QUEUE_COMMAND
        global ALLOW_URLS, VOLUME, REQUIRE_MEMBERSHIP, REQUIRE_SUPERCHAT
        global MINIMUM_SUPERCHAT, ENFORCE_ID_WHITELIST, ENFORCE_USER_WHITELIST, AUTOREMOVE_SONGS
        global AUTOBAN_USERS

        # Update in-memory config from GUI values
        YOUTUBE_VIDEO_ID = get_value("id_input")
        RATE_LIMIT_SECONDS = int(get_value("rate_limit_input"))
        TOAST_NOTIFICATIONS = str(get_value("toast_checkbox")).lower() == "true"
        PREFIX = get_value("prefix_input")
        QUEUE_COMMAND = get_value("queue_input")
        # Get selected theme
        selected_theme_display = get_value("theme_dropdown_config")
        if selected_theme_display:
            theme_name = get_theme_name_from_display(selected_theme_display)
            if theme_name and theme_name is not None:
                set_current_theme(theme_name)
            else:
                logging.error(f"Failed to resolve theme name from display name {selected_theme_display!r}")
        
        ALLOW_URLS = get_value("allowURLs_checkbox")
        REQUIRE_SUPERCHAT = get_value("require_superchat_checkbox")
        MINIMUM_SUPERCHAT = get_value("minimum_superchat_input")
        ENFORCE_USER_WHITELIST = get_value("enforce_user_whitelist_checkbox")
        ENFORCE_ID_WHITELIST = get_value("enforce_id_whitelist_checkbox")
        AUTOREMOVE_SONGS = get_value("autoremove_songs_checkbox")
        REQUIRE_MEMBERSHIP = get_value("require_membership_checkbox")
        AUTOBAN_USERS = get_value("autoban_users_checkbox")

        # Save config to file
        save_config_to_file()

        apply_theme(get_current_theme())
        stop_dearpygui()

    with window(label="Configure LYTE Settings", tag="ConfigWindow", width=0, height=0):
        set_primary_window("ConfigWindow", True)

        add_input_text(label="YouTube Livestream ID", default_value=config["YOUTUBE_VIDEO_ID"], tag="id_input")

        if invalid_id:
            add_text("Invalid or inaccessible livestream ID", color=(255, 100, 100), tag="invalid_id_warning")

        if not_live:
           add_text("Video is not a livestream", color=(255, 100, 100), tag="invalid_id_warning") 

        add_input_text(label="Command Prefix", default_value=config["PREFIX"], tag="prefix_input")
        add_input_text(label="Queue Command", default_value=config["QUEUE_COMMAND"], tag="queue_input")
        add_input_int(label="Rate Limit (seconds)", default_value=config["RATE_LIMIT_SECONDS"], tag="rate_limit_input")
        add_checkbox(label="Enable Toast Notifications", default_value=config["TOAST_NOTIFICATIONS"].lower() == "true", tag="toast_checkbox")
        add_checkbox(label="Allow URL Requests", default_value=config["ALLOW_URLS"].lower() == "true", tag="allowURLs_checkbox")
        add_checkbox(label="Require Membership to request", default_value=config["REQUIRE_MEMBERSHIP"].lower() == "true", tag="require_membership_checkbox")
        add_checkbox(label="Require Superchat to request", default_value=config["REQUIRE_SUPERCHAT"].lower() == "true", tag="require_superchat_checkbox")
        add_input_int(label="Minimum Superchat cost (USD)", default_value=config["MINIMUM_SUPERCHAT"], tag="minimum_superchat_input")
        add_checkbox(label="Enforce User Whitelist", default_value=config["ENFORCE_USER_WHITELIST"].lower() == "true", tag="enforce_user_whitelist_checkbox")
        add_checkbox(label="Enforce Song Whitelist", default_value=config["ENFORCE_ID_WHITELIST"].lower() == "true", tag="enforce_id_whitelist_checkbox")
        add_checkbox(label="Automatically remove songs", default_value=config["AUTOREMOVE_SONGS"].lower() == "true", tag="autoremove_songs_checkbox")
        add_checkbox(label="Autoban users", default_value=config["AUTOBAN_USERS"].lower() == "true", tag="autoban_users_checkbox")


        # Theme selection dropdown
        theme_items = get_theme_dropdown_items()
        if theme_items:
            # Get current theme display name
            themes = get_available_themes()
            current = get_current_theme()
            current_display = themes.get(current, {}).get("display_name", theme_items[0] if theme_items else "")
            add_combo(label="Theme", items=theme_items, default_value=current_display, 
                     tag="theme_dropdown_config", width=200)
        else:
            add_text("No themes available", color=(255, 100, 100))
        
        add_spacer(height=10)
        add_button(label="Save and Start", callback=save_and_start_callback)        
        add_spacer(height=10)
        add_button(label="Quit", callback=quit_program)

        with tooltip("id_input"):
            add_text("The ID of your livestream (The 11 characters after 'watch?v=' in the URL)")
        with tooltip("prefix_input"):
            add_text("The prefix before a command, useful if you already have another chatbot")
            add_text("Can be any number of alphanumerical characters")
        with tooltip("queue_input"):
            add_text("The command users need to enter after the prefix to queue a song. Cannot contain spaces")
        with tooltip("rate_limit_input"):
            add_text("How long a user has to wait before they can queue another song, in seconds")
        with tooltip("toast_checkbox"):
            add_text("Whether or not to show desktop notifications when a song is queued")
        with tooltip("allowURLs_checkbox"):
            add_text("Whether or not users can request songs with full URLs (I.e; the full 'https://' link)")
        with tooltip("require_membership_checkbox"):
            add_text("Whether or not users need to be a member of the channel to request a song")
        with tooltip("require_superchat_checkbox"):
            add_text("Whether or not users need to send a superchat to request a song")
        with tooltip("minimum_superchat_input"):
            add_text("The minimum value superchat (in USD) that a user must spend to request a song")
            add_text("Supplementary to 'Require Superchat to request'")
        with tooltip("theme_dropdown_config"):
            add_text("Select a theme for the application")
        with tooltip("enforce_user_whitelist_checkbox"):
            add_text("Whether or not to enforce the user Whitelist")
        with tooltip("enforce_id_whitelist_checkbox"):
            add_text("Whether or not to enforce the song ID Whitelist")
        with tooltip("autoremove_songs_checkbox"):
            add_text("Whether or not to automatically remove finished/skipped songs from the queue (applies after restart)")
        with tooltip("autoban_users_checkbox"):
            add_text("Whether or not to automatically ban users who try to request banned songs")
            
        
    # Ensure current theme exists, fallback to first available or dark_theme
    themes = get_available_themes()
    current = get_current_theme()
    if not themes or current not in themes:
        if themes:
            set_current_theme(list(themes.keys())[0])
        else:
            # No themes loaded - create a basic dark theme as fallback
            set_current_theme("dark_theme")
            logging.warning("No themes available, using default dark theme")
    
    try:
        create_viewport(title='Configure LYTE', width=750, height=485)
        try:
            apply_theme(get_current_theme())
        except Exception as theme_apply_error:
            logging.error(f"Error applying theme: {theme_apply_error}")
            # Continue without theme
        setup_dearpygui()
        show_viewport()
        set_exit_callback(on_close_attempt)
        configure_viewport(0, resizable=False)
        start_dearpygui()
    except Exception as e:
        logging.error(f"Error in show_config_menu: {e}")
        logging.error(traceback.format_exc())
        # Re-raise to see the full error
        raise
    finally:
        destroy_context()


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
    
    Runs in a background thread to continuously update the progress slider
    and time display, respecting user input to prevent conflicts.
    """
    global ignore_slider_callback

    # Wait for GUI to be ready
    while not does_item_exist(song_slider_tag) and not should_exit:
        time.sleep(0.1)

    while not should_exit:
        time.sleep(0.1)
        media_player = player.get_media_player()
        if not media_player:
            continue

        curr = get_curr_songtime()
        total = get_song_length()
        if curr is None or total is None or total <= 0:
            continue

        # Only update slider if user hasn't just scrubbed
        if current_time() - last_user_seek_time > 1.0 and does_item_exist(song_slider_tag):
            progress = curr / total
            ignore_slider_callback = True
            set_value(song_slider_tag, progress)
            ignore_slider_callback = False

        # Update time text regardless
        set_value("song_time_text", f"{format_time(curr)} / {format_time(total)}")

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
            if UPDATE_AVAILABLE:
                if does_item_exist("update_details_menu"):
                    configure_item("update_details_menu", enabled=True)
                if LATEST_VERSION and does_item_exist("MainWindow"):
                    # Ensure download UI is visible
                    show_download_ui(LATEST_VERSION)
            time.sleep(1)
        except Exception:
            time.sleep(2)

def start_theme_watcher_thread() -> None:
    """
    Start the theme file watcher after the GUI is ready.
    
    Waits for the main window to exist before starting the file watcher
    to ensure the GUI is fully initialized.
    """
    # Wait for GUI to be ready
    while not does_item_exist("MainWindow") and not should_exit:
        time.sleep(0.1)
    
    if not should_exit:
        start_theme_file_watcher()


# =============================================================================
# APPLICATION STARTUP
# =============================================================================

# Show configuration editor first
show_config_menu()

# Wait for valid configuration
while not should_exit:
    not_live = False
    invalid_id = False
    load_config()
    # Ensure we're using the latest video ID from config
    current_video_id = YOUTUBE_VIDEO_ID
    if initialize_chat():
        # Double-check we're still validating the same video ID
        if current_video_id == YOUTUBE_VIDEO_ID and is_youtube_live(YOUTUBE_VIDEO_ID):
            break
        logging.warning("Video is not a Live. Reloading config window.")
        show_config_menu(not_live = True)
    else:
        logging.warning("Chat init failed. Reloading config window.")
        show_config_menu(invalid_id= True)

# Load final configuration
load_config()

# Check for updates in background
threading.Thread(target=check_for_updates_wrapper, daemon=True).start()
threading.Thread(target=enable_update_menu_thread, daemon=True).start()

# Start all background threads
threading.Thread(target=build_gui, daemon=True).start()
threading.Thread(target=vlc_loop, daemon=True).start()
threading.Thread(target=poll_chat, daemon=True).start()
threading.Thread(target=update_slider_thread, daemon=True).start()
threading.Thread(target=update_now_playing_thread, daemon=True).start()
threading.Thread(target=start_theme_watcher_thread, daemon=True).start()

# Main application loop
while not should_exit:
    time.sleep(1)
