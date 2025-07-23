import time
import json
import os
import logging
import sys
import re
import threading
import traceback
from collections import defaultdict
from datetime import datetime
from time import time as current_time
import pytchat
import yt_dlp
import requests
from plyer import notification
import vlc  # Using python-vlc
from dearpygui.dearpygui import *
import forex_python.converter

# ---------------------- App Initialization ----------------------

def get_app_folder():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

converter = forex_python.converter.CurrencyRates()

APP_FOLDER = get_app_folder()
LOG_FOLDER = os.path.join(APP_FOLDER, 'logs')
os.makedirs(LOG_FOLDER, exist_ok=True)

log_filename = os.path.join(LOG_FOLDER, f"app_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log")
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
file_handler = logging.FileHandler(log_filename)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
file_handler.setLevel(logging.INFO)
logging.getLogger().addHandler(file_handler)
logging.getLogger("urllib3").setLevel(logging.ERROR)
logging.getLogger('httpx').setLevel(logging.ERROR)
logging.getLogger('httpcore').setLevel(logging.ERROR)

is_user_dragging_slider = False
last_slider_value = 0.0

last_user_seek_time = 0
last_gui_update_time = 0

should_exit = False

# ---------------------- Setup/Import Configuration ----------------------

def ensure_file_exists(filepath, default_content):
    if not os.path.isfile(filepath):
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(default_content, f, indent=4)
        logging.info(f"Created missing file: {filepath}")

def ensure_json_valid(filepath, default_content):
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
            # Create a backup manually
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = f"{filepath}.backup_{timestamp}.json"
            with open(backup_path, 'w', encoding='utf-8') as backup_file:
                json.dump(data, backup_file, indent=4)
            logging.info(f"Backed up original file to {backup_path}")

            # Write cleaned data
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(cleaned_data, f, indent=4)
            logging.info(f"Cleaned and updated {filepath}")

    except Exception as e:
        logging.error(f"Error validating JSON file {filepath}: {e}")


CONFIG_PATH = os.path.join(APP_FOLDER, 'config.json')
BANNED_IDS_PATH = os.path.join(APP_FOLDER, 'banned_IDs.json')
BANNED_USERS_PATH = os.path.join(APP_FOLDER, 'banned_users.json')

default_config = {
    "YOUTUBE_VIDEO_ID": "LIVESTREAM_ID",
    "RATE_LIMIT_SECONDS": 3000,
    "TOAST_NOTIFICATIONS": "True",
    "PREFIX": "!",
    "QUEUE_COMMAND": "queue",
    "VOLUME": 25,
    "DARK_MODE": "True",
    "ALLOW_URLS": "False",
    "REQUIRE_MEMBERSHIP": "False",
    "REQUIRE_SUPERCHAT": "False",
    "MINIMUM_SUPERCHAT": 3
}

ensure_file_exists(CONFIG_PATH, default_config)
ensure_file_exists(BANNED_IDS_PATH, [])
ensure_file_exists(BANNED_USERS_PATH, [])

ensure_json_valid(CONFIG_PATH, default_config)

with open(CONFIG_PATH, 'r', encoding="utf-8") as f:
    config = json.load(f)
with open(BANNED_IDS_PATH, 'r', encoding="utf-8") as f:
    bannedIDs = json.load(f)
with open(BANNED_USERS_PATH, 'r', encoding="utf-8") as f:
    bannedUsers = json.load(f)

YOUTUBE_VIDEO_ID = config.get("YOUTUBE_VIDEO_ID", "")
RATE_LIMIT_SECONDS = config.get('RATE_LIMIT_SECONDS', 3000)
TOAST_NOTIFICATIONS = config.get('TOAST_NOTIFICATIONS', "True").lower() == "true"
PREFIX = config.get('PREFIX', "!")
QUEUE_COMMAND = config.get('QUEUE_COMMAND', "queue")
VOLUME = config.get('VOLUME', 25)
DARK_MODE = config.get('DARK_MODE', "True").lower() == "true"
ALLOW_URLS = config.get('ALLOW_URLS', "True").lower() == "true"
REQUIRE_MEMBERSHIP = config.get('REQUIRE_MEMBERSHIP', "False").lower() == "true"
REQUIRE_SUPERCHAT = config.get('REQUIRE_SUPERCHAT', "False").lower() == "true"
MINIMUM_SUPERCHAT = config.get('MINIMUM_SUPERCHAT', 3)
BANNED_IDS = bannedIDs
BANNED_USERS = bannedUsers
user_last_command = defaultdict(lambda: 0)
config_success = False
# ---------------------- VLC Setup ----------------------

instance = vlc.Instance("--one-instance")
player = instance.media_list_player_new()
media_list = instance.media_list_new()
player.set_media_list(media_list)
player.play()
player.get_media_player().audio_set_volume(player.get_media_player().audio_get_volume())
logging.info("Started VLC...")

# ---------------------- Functions ----------------------
def on_close_attempt(sender, data):
    print("Program closed - If this was you, please use 'Quit' button instead! (unless program is frozen)")

def initialize_chat():
    global chat
    try:
        chat = pytchat.create(video_id=YOUTUBE_VIDEO_ID)
        return True
    except Exception as e:
        logging.critical(f"Invalid YouTube Video ID '{YOUTUBE_VIDEO_ID}'")
        logging.critical(f"Error {traceback.format_exc()}")
        return False

def load_config():
    global config, YOUTUBE_VIDEO_ID, RATE_LIMIT_SECONDS, TOAST_NOTIFICATIONS, PREFIX, QUEUE_COMMAND, ALLOW_URLS, VOLUME, REQUIRE_MEMBERSHIP, REQUIRE_SUPERCHAT, MINIMUM_SUPERCHAT
    with open(CONFIG_PATH, 'r', encoding="utf-8") as f:
        config = json.load(f)
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


def quit_program():
    global should_exit
    should_exit = True
    
    logging.info("Shutting down program")

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

    stop_dearpygui()
    logging.info("GUI closed")

def format_time(seconds):
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes:02d}:{seconds:02d}"

def get_curr_songtime():
    media_player = player.get_media_player()
    if media_player is None:
        logging.warning("No media player found.")
        return

    current_time_ms = media_player.get_time()

    if current_time_ms < 0:
        return
    
    current_time_sec = current_time_ms / 1000
    return current_time_sec

def on_song_slider_change(sender, app_data, user_data):
    global last_user_seek_time
    length = get_song_length()
    if length:
        new_time_ms = int(app_data * length * 1000)
        player.get_media_player().set_time(new_time_ms)
        last_user_seek_time = current_time()

def get_song_length():
    media_player = player.get_media_player()
    if media_player is None:
        logging.warning("No media player found.")
        return
    length_ms = media_player.get_length()
    
    if length_ms <= 0:
        return
    
    length_sec = length_ms / 1000
    return length_sec

def on_volume_change(sender, app_data, user_data):
    global VOLUME
    VOLUME = int(app_data)  # VLC expects volume 0–100
    player.get_media_player().audio_set_volume(VOLUME)

    updated_config = {
        "YOUTUBE_VIDEO_ID": YOUTUBE_VIDEO_ID,
        "RATE_LIMIT_SECONDS": RATE_LIMIT_SECONDS,
        "TOAST_NOTIFICATIONS": str(TOAST_NOTIFICATIONS),
        "PREFIX": PREFIX,
        "QUEUE_COMMAND": QUEUE_COMMAND,
        "VOLUME": VOLUME,
        "DARK_MODE": str(DARK_MODE),
        "ALLOW_URLS": str(ALLOW_URLS),
        "REQUIRE_MEMBERSHIP": str(REQUIRE_MEMBERSHIP),
        "REQUIRE_SUPERCHAT": str(REQUIRE_SUPERCHAT),
        "MINIMUM_SUPERCHAT": MINIMUM_SUPERCHAT
    }

    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(updated_config, f, indent=4)
    


def show_toast(video_id, username):
    if TOAST_NOTIFICATIONS:
        notification.notify(
            title="Requested by: " + username,
            message="Adding '" + get_video_name(video_id) + "' to queue",
            timeout=5
        )

def get_video_title(youtube_url):
    ydl_opts = { 'quiet': True, 'extract_flat': True }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(youtube_url, download=False)
        return info['title']

def get_video_name(video_id):
    url = f"https://www.youtube.com/watch?v={video_id}"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    match = re.search(r'<title>(.*?)</title>', response.text)
    if match:
        return match.group(1).replace(" - YouTube", "").strip()

def get_direct_url(youtube_url):
    ydl_opts = {'format': 'bestaudio'}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(youtube_url, download=False)
        return info['url']

def queue_song(youtube_url, requester):
    try:
        direct_url = get_direct_url(youtube_url)
        media = instance.media_new(direct_url)
        title = get_video_title(youtube_url)
        media.set_meta(vlc.Meta.Title, title)
        media_list.add_media(media)
        logging.info(f"Queued: {youtube_url} as {title}. Requested by {requester}")
        if player.get_state() != vlc.State.Playing:
            player.play()
    except Exception as e:
        logging.warning(f"Error queuing song {youtube_url}: {e}")

def on_chat_message(chat_message):
    try:
        username = chat_message.author.name
        channelid = chat_message.author.channelId
        userismember = chat_message.author.isChatSponsor
        issuperchat = chat_message.type == "superChat"
        superchatvalue = 0

        if issuperchat:
            superchatvalue = convert_to_usd(chat_message.amountValue, chat_message.currency) 

        message = chat_message.message
        current_time = time.time()

        if message.startswith(f"{PREFIX}{QUEUE_COMMAND}"):
            parts = message.split()
            if not len(parts) == 2:
                return
            video_id = parts[1]
            if current_time - user_last_command[username] < RATE_LIMIT_SECONDS:
                return
            if video_id in BANNED_IDS or channelid in BANNED_USERS:
                return
            if 'watch?v=' in video_id:
                if ALLOW_URLS:
                    video_id = video_id.split('watch?v=', 1)[1]
                else:
                    logging.warning(f"user {username} attempted to queue a URL but URL queuing is disabled! (url: {video_id})")
                    return
                
            if REQUIRE_MEMBERSHIP and not userismember:
                logging.warning(f"user {username} attempted to queue a song but they are not a member and 'REQUIRE_MEMBERSHIP' is enabled!")
                return

            if REQUIRE_SUPERCHAT and (not issuperchat or superchatvalue < MINIMUM_SUPERCHAT):
                logging.warning(f"user {username} attempted to queue a song but their message was not a Superchat or had too low of a value!")
                return

            queue_song("https://www.youtube.com/watch?v=" + video_id, username)
            show_toast(video_id, username)
            update_now_playing()
            user_last_command[username] = current_time
    except Exception as e:
        logging.error("Chat message error: %s", e)
    
def update_now_playing():
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


def convert_to_usd(value = 1, currency_name = "USD"):
    usd_value = converter.convert(currency_name, 'USD', value)
    return usd_value

# ---------------------- GUI ----------------------
create_context()
now_playing_text = None
song_slider_tag = "song_slider"
ignore_slider_callback = False

dark_theme = None
light_theme = None

def create_dark_theme():
    with theme(tag="dark_theme"):
        with theme_component(mvAll):
            add_theme_color(mvThemeCol_WindowBg, (30, 30, 30, 255))
            add_theme_color(mvThemeCol_FrameBg, (50, 50, 50, 255))
            add_theme_color(mvThemeCol_Button, (70, 70, 70, 255))
            add_theme_color(mvThemeCol_ButtonHovered, (100, 100, 100, 255))
            add_theme_color(mvThemeCol_ButtonActive, (120, 120, 120, 255))
            add_theme_color(mvThemeCol_Text, (220, 220, 220, 255))
            add_theme_color(mvThemeCol_SliderGrab, (100, 100, 255, 255))
            add_theme_color(mvThemeCol_Header, (70, 70, 70, 255))

def create_light_theme():
    with theme(tag="light_theme"):
        with theme_component(mvAll):
            add_theme_color(mvThemeCol_WindowBg, (240, 240, 240, 255))
            add_theme_color(mvThemeCol_FrameBg, (220, 220, 220, 255))
            add_theme_color(mvThemeCol_Button, (200, 200, 200, 255))
            add_theme_color(mvThemeCol_ButtonHovered, (180, 180, 180, 255))
            add_theme_color(mvThemeCol_ButtonActive, (150, 150, 150, 255))
            add_theme_color(mvThemeCol_Text, (20, 20, 20, 255))
            add_theme_color(mvThemeCol_SliderGrab, (100, 100, 255, 255))
            add_theme_color(mvThemeCol_Header, (200, 200, 200, 255))

def apply_theme(theme_tag):
    bind_theme(theme_tag)


def toggle_theme(sender, app_data, user_data):
    global DARK_MODE
    DARK_MODE = not DARK_MODE
    apply_theme("dark_theme" if DARK_MODE else "light_theme")

    updated_config = {
        "YOUTUBE_VIDEO_ID": YOUTUBE_VIDEO_ID,
        "RATE_LIMIT_SECONDS": RATE_LIMIT_SECONDS,
        "TOAST_NOTIFICATIONS": str(TOAST_NOTIFICATIONS),
        "PREFIX": PREFIX,
        "QUEUE_COMMAND": QUEUE_COMMAND,
        "VOLUME": VOLUME,
        "DARK_MODE": str(DARK_MODE),
        "ALLOW_URLS": str(ALLOW_URLS),
        "REQUIRE_MEMBERSHIP": str(REQUIRE_MEMBERSHIP),
        "REQUIRE_SUPERCHAT": str(REQUIRE_SUPERCHAT),
        "MINIMUM_SUPERCHAT": MINIMUM_SUPERCHAT
    }
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(updated_config, f, indent=4)

def set_theme(dark_mode):
    global DARK_MODE
    DARK_MODE = dark_mode
    apply_theme("dark_theme" if DARK_MODE else "light_theme")

    updated_config = {
        "YOUTUBE_VIDEO_ID": YOUTUBE_VIDEO_ID,
        "RATE_LIMIT_SECONDS": RATE_LIMIT_SECONDS,
        "TOAST_NOTIFICATIONS": str(TOAST_NOTIFICATIONS),
        "PREFIX": PREFIX,
        "QUEUE_COMMAND": QUEUE_COMMAND,
        "VOLUME": VOLUME,
        "DARK_MODE": str(DARK_MODE),
        "ALLOW_URLS": str(ALLOW_URLS),
        "REQUIRE_MEMBERSHIP": str(REQUIRE_MEMBERSHIP),
        "REQUIRE_SUPERCHAT": str(REQUIRE_SUPERCHAT),
        "MINIMUM_SUPERCHAT": MINIMUM_SUPERCHAT
    }
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(updated_config, f, indent=4)

def build_gui():
    create_context()
    global now_playing_text

    def update_settings_from_menu():
        global YOUTUBE_VIDEO_ID, RATE_LIMIT_SECONDS, TOAST_NOTIFICATIONS, PREFIX, QUEUE_COMMAND, ALLOW_URLS, REQUIRE_MEMBERSHIP, REQUIRE_SUPERCHAT, MINIMUM_SUPERCHAT
        
        RATE_LIMIT_SECONDS = int(get_value("rate_limit_input"))
        TOAST_NOTIFICATIONS = str(get_value("toast_checkbox"))
        PREFIX = get_value("prefix_input")
        QUEUE_COMMAND = get_value("queue_input")
        ALLOW_URLS = get_value("allowURLs_checkbox")
        REQUIRE_MEMBERSHIP = get_value("require_membership_checkbox")
        REQUIRE_SUPERCHAT = get_value("require_superchat_checkbox")
        MINIMUM_SUPERCHAT = get_value("minimum_superchat_input")

        updated_config = {
            "YOUTUBE_VIDEO_ID": YOUTUBE_VIDEO_ID,
            "RATE_LIMIT_SECONDS": RATE_LIMIT_SECONDS,
            "TOAST_NOTIFICATIONS": str(TOAST_NOTIFICATIONS),
            "PREFIX": PREFIX,
            "QUEUE_COMMAND": QUEUE_COMMAND,
            "VOLUME": VOLUME,
            "DARK_MODE": str(DARK_MODE),
            "ALLOW_URLS": str(ALLOW_URLS),
            "REQUIRE_MEMBERSHIP": str(REQUIRE_MEMBERSHIP),
            "REQUIRE_SUPERCHAT": str(REQUIRE_SUPERCHAT),
            "MINIMUM_SUPERCHAT": MINIMUM_SUPERCHAT
        }
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(updated_config, f, indent=4)

    with window(label="YTLM Control Panel", tag="MainWindow", width=670, height=350, pos=(100, 100)):
        set_primary_window("MainWindow", True)

        add_spacer(height=10)

        # Now Playing Text
        now_playing_text = add_text("Now Playing: Nothing", wrap=600)
        add_separator()
        add_spacer(height=10)

        # Playback Buttons
        with group(horizontal=True):
            add_button(label="Play / Pause", callback=lambda: player.pause(), width=120)
            add_button(label="Previous", callback=lambda: [player.previous(), update_now_playing()], width=100)
            add_button(label="Next", callback=lambda: [player.next(), update_now_playing()], width=100)
            add_button(label="Refresh", callback=update_now_playing, width=100)

        add_spacer(height=15)

        # Volume Control
        add_text("Volume")
        add_slider_float(label="", default_value=config["VOLUME"], min_value=0.0, max_value=100.0, width=400, callback=on_volume_change, format="%.0f")

        add_spacer(height=15)

        # Song Progress
        add_text("Song Progress")
        with group(horizontal=True):
            add_slider_float(tag=song_slider_tag, default_value=0.0, min_value=0.0, max_value=1.0,
                             width=400, callback=on_song_slider_change, format="")
            add_text("00:00 / 00:00", tag="song_time_text")

        with collapsing_header(label="Settings"):
            add_input_text(label="Command Prefix", default_value=config["PREFIX"], tag="prefix_input")
            add_input_text(label="Queue Command", default_value=config["QUEUE_COMMAND"], tag="queue_input")
            add_input_int(label="Rate Limit (seconds)", default_value=config["RATE_LIMIT_SECONDS"], tag="rate_limit_input")
            add_checkbox(label="Enable Toast Notifications", default_value=config["TOAST_NOTIFICATIONS"].lower() == "true", tag="toast_checkbox")
            add_checkbox(label="Allow URL Requests", default_value=config["ALLOW_URLS"].lower() == "true", tag="allowURLs_checkbox")
            add_checkbox(label="Require Membership to request", default_value=config["REQUIRE_MEMBERSHIP"].lower() == "true", tag="require_membership_checkbox")
            add_checkbox(label="Require Superchat to request", default_value=config["REQUIRE_SUPERCHAT"].lower() == "true", tag="require_superchat_checkbox")
            add_input_int(label="Minimum Superchat cost (USD)", default_value=config["MINIMUM_SUPERCHAT"], tag="minimum_superchat_input")

            add_spacer(height=10)
            add_button(label="Update Settings", callback=update_settings_from_menu)


                
        add_spacer(height=20)

        add_button(label="Toggle Light/Dark Mode", callback=toggle_theme, width=200)

        add_spacer(height=20)

        # Quit Button
        add_button(label="Quit", callback=lambda: quit_program(), width=100)

    create_dark_theme()
    create_light_theme()
    create_viewport(title='LYTE Control Panel', width=700, height=450)
    apply_theme("dark_theme" if DARK_MODE else "light_theme")
    setup_dearpygui()
    show_viewport()
    set_exit_callback(on_close_attempt)
    configure_viewport(0, resizable=False)
    start_dearpygui()
    destroy_context()

def show_config_menu(invalid_id=False):
    create_context()
    def save_and_start_callback():
        global YOUTUBE_VIDEO_ID, RATE_LIMIT_SECONDS, TOAST_NOTIFICATIONS, PREFIX, QUEUE_COMMAND, DARK_MODE, ALLOW_URLS, VOLUME, REQUIRE_MEMBERSHIP, REQUIRE_SUPERCHAT, MINIMUM_SUPERCHAT

        # Update in-memory config from GUI values
        YOUTUBE_VIDEO_ID = get_value("id_input")
        RATE_LIMIT_SECONDS = int(get_value("rate_limit_input"))
        TOAST_NOTIFICATIONS = str(get_value("toast_checkbox")).lower() == "true"
        PREFIX = get_value("prefix_input")
        QUEUE_COMMAND = get_value("queue_input")
        DARK_MODE = get_value("dark_mode_checkbox")
        ALLOW_URLS = get_value("allowURLs_checkbox")
        REQUIRE_SUPERCHAT = get_value("require_superchat_checkbox")
        MINIMUM_SUPERCHAT = get_value("minimum_superchat_input")

        # Save config to file
        updated_config = {
            "YOUTUBE_VIDEO_ID": get_value("id_input"),
            "RATE_LIMIT_SECONDS": int(get_value("rate_limit_input")),
            "TOAST_NOTIFICATIONS": str(get_value("toast_checkbox")),
            "PREFIX": get_value("prefix_input"),
            "QUEUE_COMMAND": get_value("queue_input"),
            "VOLUME": VOLUME,
            "DARK_MODE": str(get_value("dark_mode_checkbox")),
            "ALLOW_URLS": str(get_value("allowURLs_checkbox")),
            "REQUIRE_MEMBERSHIP": str(REQUIRE_MEMBERSHIP),
            "REQUIRE_SUPERCHAT": str(REQUIRE_SUPERCHAT),
            "MINIMUM_SUPERCHAT": MINIMUM_SUPERCHAT
        }

        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(updated_config, f, indent=4)

        set_theme(DARK_MODE)
        stop_dearpygui()

    with window(label="Configure LYTE Settings", tag="ConfigWindow", width=0, height=0):
        set_primary_window("ConfigWindow", True)

        add_input_text(label="YouTube Livestream ID", default_value=config["YOUTUBE_VIDEO_ID"], tag="id_input")

        if invalid_id:
            add_text("Invalid or inaccessible livestream ID.", color=(255, 100, 100), tag="invalid_id_warning")

        add_input_text(label="Command Prefix", default_value=config["PREFIX"], tag="prefix_input")
        add_input_text(label="Queue Command", default_value=config["QUEUE_COMMAND"], tag="queue_input")
        add_input_int(label="Rate Limit (seconds)", default_value=config["RATE_LIMIT_SECONDS"], tag="rate_limit_input")
        add_checkbox(label="Enable Toast Notifications", default_value=config["TOAST_NOTIFICATIONS"].lower() == "true", tag="toast_checkbox")
        add_checkbox(label="Allow URL Requests", default_value=config["ALLOW_URLS"].lower() == "true", tag="allowURLs_checkbox")
        add_checkbox(label="Require Membership to request", default_value=config["REQUIRE_MEMBERSHIP"].lower() == "true", tag="require_membership_checkbox")
        add_checkbox(label="Require Superchat to request", default_value=config["REQUIRE_SUPERCHAT"].lower() == "true", tag="require_superchat_checkbox")
        add_input_int(label="Minimum Superchat cost (USD)", default_value=config["MINIMUM_SUPERCHAT"], tag="minimum_superchat_input")

        add_checkbox(label="Enable Dark Mode", default_value=config["DARK_MODE"].lower() == "true", tag="dark_mode_checkbox")
        
        add_spacer(height=10)
        add_button(label="Save and Start", callback=save_and_start_callback)
        
        add_spacer(height=20)

        # Quit Button
        add_button(label="Quit", callback=lambda: quit_program(), width=100)
    create_dark_theme()
    create_light_theme()
    create_viewport(title='Configure LYTE', width=535, height=400)
    apply_theme("dark_theme" if DARK_MODE else "light_theme")
    setup_dearpygui()
    show_viewport()
    set_exit_callback(on_close_attempt)
    configure_viewport(0, resizable=False)
    start_dearpygui()
    destroy_context()


# ---------------------- Threads ----------------------

def poll_chat():
    while not should_exit:
        if chat.is_alive():
            for message in chat.get().sync_items():
                on_chat_message(message)
        time.sleep(1)

def vlc_loop():
    while not should_exit:
        if player.get_state() == vlc.State.Ended and media_list.count() > 0:
            player.play()
        time.sleep(1)

def update_slider_thread():
    global ignore_slider_callback, last_gui_update_time

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

def update_now_playing_thread():
    while not should_exit:
        update_now_playing()
        time.sleep(1)


# ---------------------- Startup ----------------------

# Show configuration editor first
show_config_menu()

while not config_success and not should_exit:
    load_config()
    if initialize_chat():
        break  # valid ID, continue
    logging.warning("Chat init failed. Reloading config window.")
    show_config_menu(invalid_id=True)

load_config()

threading.Thread(target=build_gui, daemon=True).start()
threading.Thread(target=vlc_loop, daemon=True).start()
threading.Thread(target=poll_chat, daemon=True).start()
threading.Thread(target=update_slider_thread, daemon=True).start()
threading.Thread(target=update_now_playing_thread, daemon=True).start()

while not should_exit:
    time.sleep(1)
