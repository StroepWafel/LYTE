# LYTE Code Documentation

Complete documentation for all functions, variables, and operations in the LYTE codebase.

## Table of Contents

- [Settings Management](#settings-management)
- [Global Variables](#global-variables)
- [Main Functions](#main-functions)
- [Helper Functions](#helper-functions)
- [How-To Guides](#how-to-guides)
- [Configuration Variables](#configuration-variables)

---

## Settings Management

### How to Save Settings

The app uses a `Settings` class to manage configuration. To save a setting:

1. Update the Settings class attribute
2. Call `Settings.save()` to write to the JSON file

**General Pattern For any setting:**
```python
# Update the setting:
Settings.SETTING_NAME = new_value
# Save to file
Settings.save()
```

### Settings Class Methods

#### `Settings.set_path(path: str) -> None`
Set the path to the config.json file. Must be called before loading or saving.

```python
Settings.set_path("path/to/config.json")
```

#### `Settings.load() -> None`
Load settings from the JSON file. Automatically handles type conversions for boolean fields.

```python
Settings.load()
```

#### `Settings.save() -> None`
Save current settings to the JSON file. Thread-safe operation.

```python
Settings.save()
```

#### `Settings.to_dict() -> dict`
Convert settings to dictionary format (for backward compatibility).

```python
settings_dict = Settings.to_dict()
```

### Available Settings Fields

All settings can be accessed and modified via `Settings.FIELD_NAME`:

- `YOUTUBE_VIDEO_ID` (str): YouTube livestream ID to monitor
- `RATE_LIMIT_SECONDS` (int): Cooldown between user requests (seconds)
- `TOAST_NOTIFICATIONS` (bool): Enable desktop notifications
- `PREFIX` (str): Command prefix for chat messages (default: "!")
- `QUEUE_COMMAND` (str): Command name for queuing songs (default: "queue")
- `VOLUME` (int): Default volume level (0-100)
- `THEME` (str): Theme name (default: "dark_theme")
- `ALLOW_URLS` (bool): Allow full YouTube URLs in requests
- `REQUIRE_MEMBERSHIP` (bool): Require channel membership to request
- `REQUIRE_SUPERCHAT` (bool): Require superchat to request
- `MINIMUM_SUPERCHAT` (int): Minimum superchat value in USD
- `ENFORCE_ID_WHITELIST` (bool): Only allow whitelisted video IDs
- `ENFORCE_USER_WHITELIST` (bool): Only allow whitelisted users
- `AUTOREMOVE_SONGS` (bool): Auto-remove finished songs from queue
- `AUTOBAN_USERS` (bool): Auto-ban users who request banned videos
- `SONG_FINISH_NOTIFICATIONS` (bool): Notify when songs finish naturally
- `IGNORED_VERSION` (str): Version to ignore when checking for updates

---

## Global Variables

### Application State

- `CURRENT_VERSION` (str): Current application version (e.g., "1.9.0")
- `should_exit` (bool): Application control flag for graceful shutdown
- `closeGui` (bool): Flag to close GUI
- `last_user_seek_time` (float): Timestamp of last user seek action

### Paths and Directories

- `APP_FOLDER` (str): Application folder path (determined by `get_app_folder()`)
- `LOG_FOLDER` (str): Path to logs directory
- `CONFIG_PATH` (str): Path to config.json file
- `BANNED_IDS_PATH` (str): Path to banned_IDs.json
- `BANNED_USERS_PATH` (str): Path to banned_users.json
- `WHITELISTED_IDS_PATH` (str): Path to whitelisted_IDs.json
- `WHITELISTED_USERS_PATH` (str): Path to whitelisted_users.json
- `THEMES_FOLDER` (str): Path to themes directory

### Data Structures

- `BANNED_USERS` (list[dict]): List of banned users `[{"id": "UCxxxx", "name": "ChannelName"}]`
- `BANNED_IDS` (list[dict]): List of banned video IDs `[{"id": "xxxxxx", "name": "VideoName"}]`
- `WHITELISTED_USERS` (list[dict]): List of whitelisted users
- `WHITELISTED_IDS` (list[dict]): List of whitelisted video IDs
- `QUEUE_HISTORY` (list[dict]): Past queued songs (resets on restart) `[{"user_id": "UCxxxx", "username": "Name", "song_id": "xxxxxx", "song_title": "Title"}]`
- `user_last_command` (defaultdict): Tracks last command time per user for rate limiting

### Update Detection

- `UPDATE_AVAILABLE` (bool): Whether an update is available
- `LATEST_RELEASE_DETAILS` (dict): Details of latest release
- `LATEST_VERSION` (str): Latest version string
- `IGNORED_VERSION` (str): Version to ignore

### Media Player

- `instance` (vlc.Instance): VLC instance
- `player` (vlc.MediaListPlayer): VLC playlist player
- `media_list` (vlc.MediaList): VLC playlist
- `user_initiated_skip` (bool): Track user-initiated skips

### GUI State

- `now_playing_text`: GUI text element for "Now Playing" display
- `song_slider_tag` (str): Tag for song progress slider
- `ignore_slider_callback` (bool): Flag to prevent slider callback conflicts

---

## Main Functions

### Application Control

#### `quit_program() -> None`
Gracefully shutdown the application. Stops media playback, releases VLC resources, stops theme file watcher, and closes GUI.

```python
quit_program()
```

#### `initialize_chat() -> bool`
Initialize YouTube live chat connection.

**Returns:** `True` if chat connection successful, `False` otherwise

```python
if initialize_chat():
    print("Chat initialized successfully")
```

#### `load_config() -> None`
Load and parse all configuration files. Reloads Settings, updates theme, and loads moderation lists.

```python
load_config()
```

### Media Player Functions

#### `get_curr_songtime() -> float`
Get current playback position of the current song.

**Returns:** Current time in seconds, or `None` if no media is playing

```python
current_time = get_curr_songtime()
```

#### `get_song_length() -> float`
Get the total length of the current song.

**Returns:** Song length in seconds, or `None` if no media is loaded

```python
song_length = get_song_length()
```

#### `set_user_initiated_skip() -> None`
Mark that the next song change is user-initiated (skip). Prevents natural completion notifications.

```python
set_user_initiated_skip()
```

#### `on_song_slider_change(sender, app_data, user_data) -> None`
Handle song progress slider changes. Updates playback position.

**Parameters:**
- `sender`: GUI element that triggered the callback
- `app_data`: New slider value (0.0 to 1.0)
- `user_data`: Additional user data

#### `on_volume_change(sender, app_data, user_data) -> None`
Handle volume slider changes. Updates Settings and VLC volume.

**Parameters:**
- `sender`: GUI element that triggered the callback
- `app_data`: New volume value (0.0 to 100.0)
- `user_data`: Additional user data

### Queue Management

#### `queue_song(video_id: str, requester: str, requesterUUID: str) -> None`
Add a song to the VLC playlist queue.

**Parameters:**
- `video_id`: YouTube video ID
- `requester`: Username who requested the song
- `requesterUUID`: Unique identifier for the requester

```python
queue_song("dQw4w9WgXcQ", "Username", "UCxxxx")
```

#### `on_chat_message(chat_message) -> None`
Process incoming YouTube live chat messages. Handles song queue requests with all validation rules.

**Parameters:**
- `chat_message`: Chat message object from pytchat

### Notification Functions

#### `show_toast(video_id: str, username: str) -> None`
Show desktop notification when a song is queued.

**Parameters:**
- `video_id`: YouTube video ID
- `username`: Username who requested the song

```python
show_toast("dQw4w9WgXcQ", "Username")
```

### GUI Update Functions

#### `update_now_playing() -> None`
Update the 'Now Playing' display in the GUI. Fetches current media title and updates GUI text element.

```python
update_now_playing()
```

#### `save_config_to_file() -> None`
Save current configuration to config file. Updates theme in Settings before saving.

```python
save_config_to_file()
```

### Utility Functions

#### `extract_id_from_listbox_item(item: str) -> str`
Extract ID from listbox item in "Name (ID)" format.

**Parameters:**
- `item`: Listbox item string in format "Name (ID)"

**Returns:** Extracted ID

```python
user_id = extract_id_from_listbox_item("Channel Name (UCxxxx)")
```

#### `is_on_youtube_music(video_id: str) -> bool`
Check if video is available on YouTube Music. Currently always returns `True` (placeholder).

**Parameters:**
- `video_id`: YouTube video ID

**Returns:** `True` (placeholder implementation)

#### `is_youtube_live(video_id: str) -> bool`
Check if a YouTube video is a livestream.

**Parameters:**
- `video_id`: YouTube video ID

**Returns:** `True` if video is live, `False` otherwise

```python
if is_youtube_live("dQw4w9WgXcQ"):
    print("Video is live")
```

### List Management Functions

#### `refresh_banned_users_list() -> None`
Update the banned users list in the GUI.

```python
refresh_banned_users_list()
```

#### `refresh_banned_ids_list() -> None`
Update the banned video IDs list in the GUI.

```python
refresh_banned_ids_list()
```

#### `refresh_whitelisted_users_list() -> None`
Update the whitelisted users list in the GUI.

```python
refresh_whitelisted_users_list()
```

#### `refresh_whitelisted_ids_list() -> None`
Update the whitelisted video IDs list in the GUI.

```python
refresh_whitelisted_ids_list()
```

#### `refresh_queue_history_list() -> None`
Update the queue history list in the GUI.

```python
refresh_queue_history_list()
```

### Ban/Unban Callback Functions

#### `ban_user_callback() -> None`
Handle banning a user from the GUI. Adds user to banned list with placeholder name, then fetches real channel name in background.

```python
ban_user_callback()
```

#### `ban_id_callback() -> None`
Handle banning a video ID from the GUI. Adds video to banned list with placeholder name, then fetches real video name in background.

```python
ban_id_callback()
```

#### `whitelist_user_callback() -> None`
Handle whitelisting a user from the GUI.

```python
whitelist_user_callback()
```

#### `whitelist_id_callback() -> None`
Handle whitelisting a video ID from the GUI.

```python
whitelist_id_callback()
```

#### `unban_user_callback() -> None`
Remove selected user from banned users list.

```python
unban_user_callback()
```

#### `unban_id_callback() -> None`
Remove selected video ID from banned video IDs list.

```python
unban_id_callback()
```

#### `unwhitelist_user_callback() -> None`
Remove selected user from whitelisted users list.

```python
unwhitelist_user_callback()
```

#### `unwhitelist_id_callback() -> None`
Remove selected video ID from whitelisted video IDs list.

```python
unwhitelist_id_callback()
```

#### `ban_song_from_queue() -> None`
Ban the song from the selected queue history entry.

```python
ban_song_from_queue()
```

#### `ban_user_from_queue() -> None`
Ban the user from the selected queue history entry.

```python
ban_user_from_queue()
```

### Theme Management Functions

#### `select_theme_by_name(theme_name: str) -> None`
Select a theme by its name. Updates menu checkmarks and saves theme preference.

**Parameters:**
- `theme_name`: Name of the theme to select

```python
select_theme_by_name("dark_theme")
```

#### `select_theme(sender, app_data, user_data) -> None`
Handle theme selection from dropdown (for combo boxes).

**Parameters:**
- `sender`: GUI element that triggered the callback
- `app_data`: Selected theme display name
- `user_data`: Additional user data

#### `update_theme_menu_checks() -> None`
Update checkmarks on theme menu items.

```python
update_theme_menu_checks()
```

#### `save_theme_to_config() -> None`
Save current theme to config file.

```python
save_theme_to_config()
```

#### `reload_themes() -> None`
Reload all themes from disk. Unloads all themes, loads them again, applies current theme, and rebuilds menu.

```python
reload_themes()
```

#### `rebuild_theme_menu_items() -> None`
Regenerate the Theme menu items based on currently available themes.

```python
rebuild_theme_menu_items()
```

### Theme File Watcher

#### `start_theme_file_watcher() -> None`
Start monitoring the themes folder for file changes. Automatically reloads themes when changes are detected.

```python
start_theme_file_watcher()
```

#### `stop_theme_file_watcher() -> None`
Stop monitoring the themes folder for file changes.

```python
stop_theme_file_watcher()
```

### Update Functions

#### `check_for_updates_wrapper() -> None`
Check for updates with current configuration. Updates global update state variables.

```python
check_for_updates_wrapper()
```

#### `download_installer() -> None`
Start downloading the latest installer from GitHub in a background thread.

```python
download_installer()
```

#### `run_installer_wrapper() -> None`
Run the downloaded installer.

```python
run_installer_wrapper()
```

#### `show_download_ui(latest_version: str) -> None`
Show download UI elements in the main window.

**Parameters:**
- `latest_version`: The latest version available

```python
show_download_ui("1.10.0")
```

#### `ignore_update_action() -> None`
Ignore the current update and hide related UI.

```python
ignore_update_action()
```

#### `show_update_details_window() -> None`
Populate and display the Update Details window.

```python
show_update_details_window()
```

### GUI Construction

#### `build_gui() -> None`
Build and display the main application GUI. Creates the main control panel window with all controls.

```python
build_gui()
```

#### `show_config_menu(invalid_id: bool = False, not_live: bool = False) -> None`
Display the initial configuration menu.

**Parameters:**
- `invalid_id`: Whether to show an invalid ID warning
- `not_live`: Whether to show a "not live" warning

```python
show_config_menu(invalid_id=True)
```

### Background Threading Functions

#### `poll_chat() -> None`
Poll YouTube live chat for new messages. Runs in a background thread continuously checking for new chat messages.

```python
# Typically run in a thread:
threading.Thread(target=poll_chat, daemon=True).start()
```

#### `vlc_loop() -> None`
Monitor VLC player state and handle automatic playback. Ensures continuous playback when songs end.

```python
# Typically run in a thread:
threading.Thread(target=vlc_loop, daemon=True).start()
```

#### `update_slider_thread() -> None`
Update the song progress slider in real-time. Continuously updates progress slider and time display.

```python
# Typically run in a thread:
threading.Thread(target=update_slider_thread, daemon=True).start()
```

#### `update_now_playing_thread() -> None`
Update the 'Now Playing' display periodically. Keeps current song information displayed in GUI up to date.

```python
# Typically run in a thread:
threading.Thread(target=update_now_playing_thread, daemon=True).start()
```

#### `enable_update_menu_thread() -> None`
Enable the update details menu and show download UI when an update is detected.

```python
# Typically run in a thread:
threading.Thread(target=enable_update_menu_thread, daemon=True).start()
```

#### `start_theme_watcher_thread() -> None`
Start the theme file watcher after the GUI is ready. Waits for main window to exist before starting.

```python
# Typically run in a thread:
threading.Thread(target=start_theme_watcher_thread, daemon=True).start()
```

### Wrapper Functions

#### `load_banned_users_wrapper() -> None`
Load banned users list from file and update global variable.

```python
load_banned_users_wrapper()
```

#### `load_banned_ids_wrapper() -> None`
Load banned video IDs list from file and update global variable.

```python
load_banned_ids_wrapper()
```

#### `load_whitelisted_users_wrapper() -> None`
Load whitelisted users list from file and update global variable.

```python
load_whitelisted_users_wrapper()
```

#### `load_whitelisted_ids_wrapper() -> None`
Load whitelisted video IDs list from file and update global variable.

```python
load_whitelisted_ids_wrapper()
```

#### `load_settings_wrapper() -> None`
Load settings from config file and update global variables.

```python
load_settings_wrapper()
```

---

## Helper Functions

### Moderation Helpers (`helpers/moderation_helpers.py`)

#### `load_banned_users(banned_users_path: str) -> list`
Load banned users list from file.

**Parameters:**
- `banned_users_path`: Path to the banned users JSON file

**Returns:** List of banned users

```python
banned_users = load_banned_users("path/to/banned_users.json")
```

#### `load_banned_ids(banned_ids_path: str) -> list`
Load banned video IDs list from file.

**Parameters:**
- `banned_ids_path`: Path to the banned IDs JSON file

**Returns:** List of banned video IDs

```python
banned_ids = load_banned_ids("path/to/banned_IDs.json")
```

#### `load_whitelisted_users(whitelisted_users_path: str) -> list`
Load whitelisted users list from file.

**Parameters:**
- `whitelisted_users_path`: Path to the whitelisted users JSON file

**Returns:** List of whitelisted users

```python
whitelisted_users = load_whitelisted_users("path/to/whitelisted_users.json")
```

#### `load_whitelisted_ids(whitelisted_ids_path: str) -> list`
Load whitelisted video IDs list from file.

**Parameters:**
- `whitelisted_ids_path`: Path to the whitelisted IDs JSON file

**Returns:** List of whitelisted video IDs

```python
whitelisted_ids = load_whitelisted_ids("path/to/whitelisted_IDs.json")
```

#### `save_banned_users(banned_users: list, banned_users_path: str) -> None`
Save banned users list to file.

**Parameters:**
- `banned_users`: List of banned users to save
- `banned_users_path`: Path to save the file

```python
save_banned_users([{"id": "UCxxxx", "name": "Channel"}], "path/to/banned_users.json")
```

#### `save_banned_ids(banned_ids: list, banned_ids_path: str) -> None`
Save banned video IDs list to file.

**Parameters:**
- `banned_ids`: List of banned video IDs to save
- `banned_ids_path`: Path to save the file

```python
save_banned_ids([{"id": "dQw4w9WgXcQ", "name": "Video"}], "path/to/banned_IDs.json")
```

#### `save_whitelisted_users(whitelisted_users: list, whitelisted_users_path: str) -> None`
Save whitelisted users list to file.

**Parameters:**
- `whitelisted_users`: List of whitelisted users to save
- `whitelisted_users_path`: Path to save the file

```python
save_whitelisted_users([{"id": "UCxxxx", "name": "Channel"}], "path/to/whitelisted_users.json")
```

#### `save_whitelisted_ids(whitelisted_ids: list, whitelisted_ids_path: str) -> None`
Save whitelisted video IDs list to file.

**Parameters:**
- `whitelisted_ids`: List of whitelisted video IDs to save
- `whitelisted_ids_path`: Path to save the file

```python
save_whitelisted_ids([{"id": "dQw4w9WgXcQ", "name": "Video"}], "path/to/whitelisted_IDs.json")
```

### Currency Helpers (`helpers/currency_helpers.py`)

#### `convert_to_usd(value: float = 1, currency_name: str = "USD") -> float`
Convert currency value to USD.

**Parameters:**
- `value`: Amount to convert
- `currency_name`: Source currency code (e.g., "EUR", "JPY")

**Returns:** Value in USD

```python
usd_value = convert_to_usd(5.0, "EUR")
```

### YouTube Helpers (`helpers/youtube_helpers.py`)

#### `get_video_title_fast(video_id: str) -> str`
Get video title using YouTube oEmbed API (much faster than yt_dlp). Uses caching.

**Parameters:**
- `video_id`: YouTube video ID

**Returns:** Video title or "Unknown Video" if not found

```python
title = get_video_title_fast("dQw4w9WgXcQ")
```

#### `get_channel_name_fast(channel_id: str) -> str`
Get channel name using lightweight web scraping (faster than yt_dlp). Uses caching.

**Parameters:**
- `channel_id`: YouTube channel ID

**Returns:** Channel name or "Unknown Channel" if not found

```python
channel_name = get_channel_name_fast("UCxxxx")
```

#### `get_video_title(youtube_url: str) -> str`
Extract video title from YouTube URL (legacy function).

**Parameters:**
- `youtube_url`: Full YouTube URL

**Returns:** Video title

```python
title = get_video_title("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
```

#### `get_video_name_fromID(video_id: str) -> str`
Get video title from YouTube video ID (uses fast method).

**Parameters:**
- `video_id`: YouTube video ID

**Returns:** Video title

```python
title = get_video_name_fromID("dQw4w9WgXcQ")
```

#### `get_direct_url(youtube_url: str) -> str`
Get direct audio stream URL from YouTube URL for VLC playback.

**Parameters:**
- `youtube_url`: Full YouTube URL

**Returns:** Direct audio stream URL

```python
audio_url = get_direct_url("https://music.youtube.com/watch?v=dQw4w9WgXcQ")
```

#### `fetch_channel_name(channel_id: str) -> str`
Fetch channel name from YouTube channel ID (uses fast method).

**Parameters:**
- `channel_id`: YouTube channel ID

**Returns:** Channel name or "Unknown Channel" if not found

```python
channel_name = fetch_channel_name("UCxxxx")
```

#### `fetch_video_name(video_id: str) -> str`
Fetch video name from YouTube video ID (uses fast method).

**Parameters:**
- `video_id`: YouTube video ID

**Returns:** Video title

```python
video_name = fetch_video_name("dQw4w9WgXcQ")
```

### Time Helpers (`helpers/time_helpers.py`)

#### `format_time(seconds: float) -> str`
Format time in seconds to MM:SS format.

**Parameters:**
- `seconds`: Time in seconds

**Returns:** Formatted time string (MM:SS)

```python
formatted = format_time(125.5)  # Returns "02:05"
```

### File Helpers (`helpers/file_helpers.py`)

#### `show_folder(folder_location: str) -> None`
Open the application folder in the system's file explorer.

**Parameters:**
- `folder_location`: Path to folder to open

```python
show_folder("C:/Users/username/AppData/Local/LYTE")
```

#### `get_app_folder() -> str`
Determine the application folder path. Uses user data directory if frozen (PyInstaller), script directory otherwise.

**Returns:** Path to the application directory

```python
app_folder = get_app_folder()
```

#### `ensure_file_exists(filepath: str, default_content) -> None`
Create a file with default content if it doesn't exist.

**Parameters:**
- `filepath`: Path to the file to create
- `default_content`: Default content to write to the file

```python
ensure_file_exists("config.json", {"key": "value"})
```

#### `ensure_json_valid(filepath: str, default_content: dict) -> None`
Validate and clean a JSON configuration file. Ensures JSON is valid and contains only expected keys.

**Parameters:**
- `filepath`: Path to the JSON file to validate
- `default_content`: Default configuration structure to validate against

```python
ensure_json_valid("config.json", {"key": "value"})
```

### Update Helpers (`helpers/update_helpers.py`)

#### `run_installer(app_folder: str) -> None`
Run the downloaded installer.

**Parameters:**
- `app_folder`: Path to the application folder

```python
run_installer("C:/Users/username/AppData/Local/LYTE")
```

#### `download_installer_worker(app_folder: str) -> None`
Worker function that downloads the installer in the background.

**Parameters:**
- `app_folder`: Path to the application folder

```python
# Typically run in a thread:
threading.Thread(target=download_installer_worker, args=(app_folder,), daemon=True).start()
```

#### `check_for_updates(current_version: str, ignored_version: str, toast_notifications: bool) -> str`
Check for available updates and notify the user if a new version is available.

**Parameters:**
- `current_version`: Current application version
- `ignored_version`: Version to ignore
- `toast_notifications`: Whether to show desktop notifications

**Returns:** Latest version if available, empty string otherwise

```python
latest = check_for_updates("1.9.0", "", True)
```

### Version Helpers (`helpers/version_helpers.py`)

#### `compare_versions(version1: str, version2: str) -> int`
Compare two version strings.

**Parameters:**
- `version1`: First version string (e.g., "1.5.0")
- `version2`: Second version string (e.g., "1.6.0")

**Returns:** -1 if version1 < version2, 0 if equal, 1 if version1 > version2

```python
result = compare_versions("1.5.0", "1.6.0")  # Returns -1
```

#### `fetch_latest_version() -> str`
Fetch the latest release version from GitHub API.

**Returns:** Latest version string, or empty string if failed

```python
latest = fetch_latest_version()
```

#### `fetch_latest_release_details() -> dict`
Fetch the latest release details from GitHub API.

**Returns:** Details including 'version', 'name', 'body', 'html_url'. Empty dict if failed.

```python
details = fetch_latest_release_details()
```

### Theme Helpers (`helpers/theme_helpers.py`)

#### `init_theme_system(themes_folder: str) -> None`
Initialize the theme system with the themes folder path.

**Parameters:**
- `themes_folder`: Path to the themes directory

```python
init_theme_system("path/to/themes")
```

#### `discover_themes() -> dict`
Scan the themes folder and discover all available theme files. Checks both PyInstaller bundle location and user app folder.

**Returns:** Dictionary mapping theme names to theme info

```python
themes = discover_themes()
```

#### `load_theme_from_file(theme_name: str) -> dict`
Load theme configuration from a JSON file. Checks user folder first, then PyInstaller bundle location.

**Parameters:**
- `theme_name`: Name of the theme file (without .json extension)

**Returns:** Theme configuration with 'colors' and 'styles' keys, or None if file doesn't exist

```python
theme_data = load_theme_from_file("dark_theme")
```

#### `apply_theme_from_data(theme_tag: str, theme_data: dict) -> None`
Apply theme data to create a DearPyGui theme.

**Parameters:**
- `theme_tag`: Tag identifier for the theme
- `theme_data`: Dictionary containing 'colors' and 'styles' keys

```python
apply_theme_from_data("dark_theme", theme_data)
```

#### `create_default_theme_files() -> None`
Create default theme JSON files if they don't exist. Creates dark_theme.json, light_theme.json, and demo_theme.json.demo.

```python
create_default_theme_files()
```

#### `load_all_themes() -> None`
Load all discovered themes into DearPyGui.

```python
load_all_themes()
```

#### `create_theme(theme_name: str) -> None`
Create and configure a theme for the GUI.

**Parameters:**
- `theme_name`: Name of the theme to create

```python
create_theme("dark_theme")
```

#### `apply_theme(theme_tag: str) -> None`
Apply the specified theme to the GUI.

**Parameters:**
- `theme_tag`: Theme identifier (theme name)

```python
apply_theme("dark_theme")
```

#### `get_theme_dropdown_items() -> list`
Get list of theme display names for dropdown.

**Returns:** List of theme display names

```python
items = get_theme_dropdown_items()
```

#### `get_theme_name_from_display(display_name: str) -> str`
Get theme name from display name.

**Parameters:**
- `display_name`: Display name of the theme

**Returns:** Theme name (file identifier)

```python
theme_name = get_theme_name_from_display("Dark Theme")
```

#### `get_available_themes() -> dict`
Get the dictionary of available themes.

**Returns:** Available themes dictionary

```python
themes = get_available_themes()
```

#### `get_current_theme() -> str`
Get the current theme name.

**Returns:** Current theme name

```python
current = get_current_theme()
```

#### `set_current_theme(theme_name: str) -> None`
Set the current theme name.

**Parameters:**
- `theme_name`: Name of the theme to set as current

```python
set_current_theme("dark_theme")
```

#### `unload_all_themes() -> None`
Unload all themes from DearPyGui and clear the internal registry.

```python
unload_all_themes()
```

---

## How-To Guides

### How to Change a Setting

1. Access the setting via `Settings.SETTING_NAME`
2. Modify the value
3. Save using `Settings.save()`

**Example:**
```python
# Change volume to 75
Settings.VOLUME = 75
Settings.save()
```

### How to Ban a User

**Method 1: Using the GUI callback**
```python
# Set the input value first (via GUI)
# Then call:
ban_user_callback()
```

**Method 2: Programmatically**
```python
from helpers.moderation_helpers import save_banned_users, load_banned_users

# Load current list
banned_users = load_banned_users(BANNED_USERS_PATH)

# Add new user
banned_users.append({"id": "UCxxxx", "name": "Channel Name"})

# Save
save_banned_users(banned_users, BANNED_USERS_PATH)

# Refresh GUI
refresh_banned_users_list()
```

### How to Ban a Video

**Method 1: Using the GUI callback**
```python
# Set the input value first (via GUI)
# Then call:
ban_id_callback()
```

**Method 2: Programmatically**
```python
from helpers.moderation_helpers import save_banned_ids, load_banned_ids

# Load current list
banned_ids = load_banned_ids(BANNED_IDS_PATH)

# Add new video
banned_ids.append({"id": "dQw4w9WgXcQ", "name": "Video Name"})

# Save
save_banned_ids(banned_ids, BANNED_IDS_PATH)

# Refresh GUI
refresh_banned_ids_list()
```

### How to Whitelist a User

**Method 1: Using the GUI callback**
```python
# Set the input value first (via GUI)
# Then call:
whitelist_user_callback()
```

**Method 2: Programmatically**
```python
from helpers.moderation_helpers import save_whitelisted_users, load_whitelisted_users

# Load current list
whitelisted_users = load_whitelisted_users(WHITELISTED_USERS_PATH)

# Add new user
whitelisted_users.append({"id": "UCxxxx", "name": "Channel Name"})

# Save
save_whitelisted_users(whitelisted_users, WHITELISTED_USERS_PATH)

# Refresh GUI
refresh_whitelisted_users_list()
```

### How to Whitelist a Video

**Method 1: Using the GUI callback**
```python
# Set the input value first (via GUI)
# Then call:
whitelist_id_callback()
```

**Method 2: Programmatically**
```python
from helpers.moderation_helpers import save_whitelisted_ids, load_whitelisted_ids

# Load current list
whitelisted_ids = load_whitelisted_ids(WHITELISTED_IDS_PATH)

# Add new video
whitelisted_ids.append({"id": "dQw4w9WgXcQ", "name": "Video Name"})

# Save
save_whitelisted_ids(whitelisted_ids, WHITELISTED_IDS_PATH)

# Refresh GUI
refresh_whitelisted_ids_list()
```

### How to Change Theme

**Method 1: Using the function**
```python
from helpers.theme_helpers import set_current_theme, apply_theme

set_current_theme("dark_theme")
apply_theme("dark_theme")
save_theme_to_config()
```

**Method 2: Using Settings**
```python
Settings.THEME = "dark_theme"
set_current_theme(Settings.THEME)
apply_theme(Settings.THEME)
Settings.save()
```

### How to Queue a Song Programmatically

```python
# Queue a song directly
queue_song("dQw4w9WgXcQ", "Username", "UCxxxx")

# Update the "Now Playing" display
update_now_playing()
```

### How to Get Video Information

```python
from helpers.youtube_helpers import get_video_name_fromID, get_video_title, get_direct_url

# Get video title from ID
title = get_video_name_fromID("dQw4w9WgXcQ")

# Get video title from URL
title = get_video_title("https://www.youtube.com/watch?v=dQw4w9WgXcQ")

# Get direct audio URL for VLC
audio_url = get_direct_url("https://music.youtube.com/watch?v=dQw4w9WgXcQ")
```

### How to Get Channel Information

```python
from helpers.youtube_helpers import fetch_channel_name

# Get channel name from channel ID
channel_name = fetch_channel_name("UCxxxx")
```

### How to Reload Configuration

```python
# Reload all configuration files
load_config()

# This will:
# - Reload Settings from file
# - Update theme if it changed
# - Load moderation lists (banned/whitelisted users and videos)
```

### How to Check for Updates

```python
# Check for updates
check_for_updates_wrapper()

# Or manually:
from helpers.update_helpers import check_for_updates

latest = check_for_updates(CURRENT_VERSION, IGNORED_VERSION, Settings.TOAST_NOTIFICATIONS)
if latest:
    print(f"Update available: {latest}")
```

### How to Format Time

```python
from helpers.time_helpers import format_time

# Format seconds to MM:SS
formatted = format_time(125.5)  # Returns "02:05"
```

### How to Convert Currency

```python
from helpers.currency_helpers import convert_to_usd

# Convert EUR to USD
usd_value = convert_to_usd(5.0, "EUR")
```

### How to Open Application Folder

```python
from helpers.file_helpers import show_folder, get_app_folder

# Get app folder path
app_folder = get_app_folder()

# Open folder in file explorer
show_folder(app_folder)
```

### How to Create a Custom Theme

1. Create a JSON file in the themes folder (e.g., `custom_theme.json`)
2. Use the following structure:

```json
{
  "name": "Custom Theme",
  "colors": {
    "WindowBg": [25, 25, 25, 255],
    "FrameBg": [35, 35, 35, 255],
    "Button": [60, 70, 60, 255],
    "ButtonHovered": [80, 120, 80, 255],
    "ButtonActive": [100, 150, 100, 255],
    "Text": [220, 220, 220, 255],
    "SliderGrab": [100, 150, 100, 255],
    "SliderGrabActive": [120, 180, 120, 255],
    "Header": [40, 40, 40, 255],
    "ScrollbarBg": [35, 35, 35, 128],
    "ScrollbarGrab": [60, 70, 60, 255],
    "ScrollbarGrabHovered": [80, 120, 80, 255],
    "ScrollbarGrabActive": [100, 150, 100, 255],
    "CheckMark": [100, 150, 100, 255],
    "HeaderHovered": [80, 120, 80, 255],
    "HeaderActive": [100, 150, 100, 255],
    "Tab": [60, 70, 60, 255],
    "TabHovered": [80, 120, 80, 255],
    "TabActive": [100, 150, 100, 255],
    "TitleBg": [25, 25, 25, 255],
    "TitleBgActive": [40, 50, 40, 255],
    "TitleBgCollapsed": [25, 25, 25, 128],
    "MenuBarBg": [30, 30, 30, 255],
    "Border": [70, 90, 70, 255],
    "Separator": [70, 90, 70, 255],
    "PopupBg": [35, 35, 35, 240],
    "TextSelectedBg": [80, 120, 80, 150]
  },
  "styles": {
    "FrameRounding": 8.0,
    "FrameBorderSize": 0.5,
    "WindowRounding": 12.0,
    "ScrollbarSize": 12.0,
    "ScrollbarRounding": 8.0,
    "TabRounding": 8.0,
    "GrabRounding": 8.0,
    "ChildRounding": 8.0,
    "PopupRounding": 8.0,
    "ItemSpacing": [8, 6],
    "ItemInnerSpacing": [6, 6]
  }
}
```

3. Reload themes:
```python
reload_themes()
```

### How to Access Queue History

```python
# Queue history is stored in global variable QUEUE_HISTORY
# Format: [{"user_id": "UCxxxx", "username": "Name", "song_id": "xxxxxx", "song_title": "Title"}]

# Access queue history
for item in QUEUE_HISTORY:
    print(f"{item['song_title']} - Requested by {item['username']}")

# Refresh GUI display
refresh_queue_history_list()
```

### How to Control Media Playback

```python
# Play/Pause
player.pause()

# Skip to next song
set_user_initiated_skip()
player.next()
update_now_playing()

# Skip to previous song
set_user_initiated_skip()
player.previous()
update_now_playing()

# Stop playback
player.stop()

# Set volume
Settings.VOLUME = 75
player.get_media_player().audio_set_volume(Settings.VOLUME)
Settings.save()

# Seek to position (in milliseconds)
player.get_media_player().set_time(60000)  # Seek to 1 minute
```

### How to Check Media Player State

```python
import vlc

# Get current state
state = player.get_state()

# Check if stopped
if state == vlc.State.Stopped:
    print("Player is stopped")

# Get current time
current_time = get_curr_songtime()

# Get song length
song_length = get_song_length()

# Get queue count
queue_count = media_list.count()
```

---

## Configuration Variables

### Default Configuration

The default configuration is defined in `default_config` dictionary in `main.py`:

```python
default_config = {
    "YOUTUBE_VIDEO_ID": "LIVESTREAM_ID",
    "RATE_LIMIT_SECONDS": 3000,
    "TOAST_NOTIFICATIONS": "True",
    "PREFIX": "!",
    "QUEUE_COMMAND": "queue",
    "VOLUME": 50,
    "THEME": "dark_theme",
    "ALLOW_URLS": "False",
    "REQUIRE_MEMBERSHIP": "False",
    "REQUIRE_SUPERCHAT": "False",
    "MINIMUM_SUPERCHAT": 3,
    "ENFORCE_ID_WHITELIST": "False",
    "ENFORCE_USER_WHITELIST": "False",
    "AUTOREMOVE_SONGS": "True",
    "AUTOBAN_USERS": "False",
    "SONG_FINISH_NOTIFICATIONS": "False",
    "IGNORED_VERSION": ""
}
```

### Configuration File Structure

The `config.json` file structure:

```json
{
    "YOUTUBE_VIDEO_ID": "LIVESTREAM_ID",
    "RATE_LIMIT_SECONDS": 3000,
    "TOAST_NOTIFICATIONS": "True",
    "PREFIX": "!",
    "QUEUE_COMMAND": "queue",
    "VOLUME": 50,
    "THEME": "dark_theme",
    "ALLOW_URLS": "False",
    "REQUIRE_MEMBERSHIP": "False",
    "REQUIRE_SUPERCHAT": "False",
    "MINIMUM_SUPERCHAT": 3,
    "ENFORCE_ID_WHITELIST": "False",
    "ENFORCE_USER_WHITELIST": "False",
    "AUTOREMOVE_SONGS": "True",
    "AUTOBAN_USERS": "False",
    "SONG_FINISH_NOTIFICATIONS": "False",
    "IGNORED_VERSION": ""
}
```

### Moderation File Structures

**banned_IDs.json:**
```json
[
    {"id": "dQw4w9WgXcQ", "name": "Video Name 1"},
    {"id": "jNQXAC9IVRw", "name": "Video Name 2"}
]
```

**banned_users.json:**
```json
[
    {"id": "UCxxxxxxxxxxxxxxxxxxxxx", "name": "Channel Name 1"},
    {"id": "UCyyyyyyyyyyyyyyyyyyyyy", "name": "Channel Name 2"}
]
```

**whitelisted_IDs.json:**
```json
[
    {"id": "dQw4w9WgXcQ", "name": "Video Name 1"},
    {"id": "jNQXAC9IVRw", "name": "Video Name 2"}
]
```

**whitelisted_users.json:**
```json
[
    {"id": "UCxxxxxxxxxxxxxxxxxxxxx", "name": "Channel Name 1"},
    {"id": "UCyyyyyyyyyyyyyyyyyyyyy", "name": "Channel Name 2"}
]
```

---

## VLC Event Callbacks

### `on_next_item(event) -> None`

Callback function triggered when VLC moves to the next item in the playlist. Handles:
- Auto-removal of finished songs (if enabled)
- Notifications for new song starting (if enabled)
- Natural completion detection

**Parameters:**
- `event`: VLC event object (unused but required by VLC callback signature)

---

## File System Event Handlers

### `ThemeFileHandler` Class

File system event handler for theme files. Automatically reloads themes when theme files are created, modified, or deleted.

**Methods:**
- `on_any_event(event)`: Handle any file system event in the themes folder

---

## Notes

- All file paths use UTF-8 encoding
- Thread-safe operations use locks where necessary
- Caching is used for YouTube API calls (1 hour duration)
- Theme files are automatically watched for changes
- Configuration files are validated and cleaned on load
- Backup files are created before modifying config files

---

## Version Information

- **Current Version:** 1.9.0
- **Documentation Version:** 1.0

