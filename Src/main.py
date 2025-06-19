import time
import json
import os
import logging
import sys
import re
import threading
from collections import defaultdict
from datetime import datetime
from time import time as current_time
import pytchat
import yt_dlp
import requests
from plyer import notification
import vlc  # Using python-vlc
from dearpygui.dearpygui import *

# ---------------------- App Initialization ----------------------

def get_app_folder():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

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

CONFIG_PATH = os.path.join(APP_FOLDER, 'config.json')
BANNED_IDS_PATH = os.path.join(APP_FOLDER, 'banned_IDs.json')
BANNED_USERS_PATH = os.path.join(APP_FOLDER, 'banned_users.json')

default_config = {
    "YOUTUBE_VIDEO_ID": "LIVESTREAM_ID",
    "RATE_LIMIT_SECONDS": 240,
    "TOAST_NOTIFICATIONS": "True",
    "PREFIX": "!",
    "QUEUE_COMMAND": "queue"
}

ensure_file_exists(CONFIG_PATH, default_config)
ensure_file_exists(BANNED_IDS_PATH, [])
ensure_file_exists(BANNED_USERS_PATH, [])

with open(CONFIG_PATH, 'r', encoding="utf-8") as f:
    config = json.load(f)
with open(BANNED_IDS_PATH, 'r', encoding="utf-8") as f:
    bannedIDs = json.load(f)
with open(BANNED_USERS_PATH, 'r', encoding="utf-8") as f:
    bannedUsers = json.load(f)

YOUTUBE_VIDEO_ID = config.get("YOUTUBE_VIDEO_ID", "")
RATE_LIMIT_SECONDS = config.get('RATE_LIMIT_SECONDS', 10)
TOAST_NOTIFICATIONS = config.get('TOAST_NOTIFICATIONS', "True").lower() == "true"
PREFIX = config.get('PREFIX', "!")
QUEUE_COMMAND = config.get('QUEUE_COMMAND', "queue")
BANNED_IDS = bannedIDs
BANNED_USERS = bannedUsers
user_last_command = defaultdict(lambda: 0)

# ---------------------- VLC Setup ----------------------

instance = vlc.Instance("--one-instance")
player = instance.media_list_player_new()
media_list = instance.media_list_new()
player.set_media_list(media_list)
player.play()
logging.info("Started VLC...")

try:
    chat = pytchat.create(video_id=YOUTUBE_VIDEO_ID)
except Exception as e:
    logging.critical("Error while listening to livestream chat: %s", e)
    sys.exit(1)

# ---------------------- Functions ----------------------

def quit_program():
    global should_exit
    should_exit = True
    
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
    sys.exit(0)

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
    volume = int(app_data)  # VLC expects volume 0–100
    player.get_media_player().audio_set_volume(volume)

def show_toast(video_id, username):
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
        logging.error(f"Error queuing song {youtube_url}: {e}")

def on_chat_message(chat_message):
    try:
        username = chat_message.author.name
        message = chat_message.message
        current_time = time.time()
        if message.startswith(f"{PREFIX}{QUEUE_COMMAND}"):
            parts = message.split()
            if len(parts) < 2:
                return
            video_id = parts[1]
            if current_time - user_last_command[username] < RATE_LIMIT_SECONDS:
                return
            if video_id in BANNED_IDS or username in BANNED_USERS:
                return
            queue_song("https://www.youtube.com/watch?v=" + video_id, username)
            update_now_playing()
            user_last_command[username] = current_time
            if TOAST_NOTIFICATIONS:
                show_toast(video_id, username)
    except Exception as e:
        logging.error("Chat message error: %s", e)

# ---------------------- GUI ----------------------

create_context()
now_playing_text = None

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

song_slider_tag = "song_slider"
ignore_slider_callback = False

def build_gui():
    global now_playing_text
    with window(label="YTLM Control Panel", tag="MainWindow", width=500, height=300):
        now_playing_text = add_text("Now Playing: Nothing")
        add_spacer(height=20)

        # Group buttons horizontally
        with group(horizontal=True):
            add_button(label="Play / Pause", callback=lambda: player.pause())
            add_button(label="Previous", callback=lambda: [player.previous(), update_now_playing()])
            add_button(label="Next", callback=lambda: [player.next(), update_now_playing()])
            add_button(label="Refresh", callback=update_now_playing)
            add_slider_float(label="Volume", default_value=player.get_media_player().audio_get_volume() / 100, min_value=0.0, max_value=100, width=300, callback=on_volume_change, format="%.0f")
      
        add_spacer(height=20)
        with group(horizontal=True):
            add_slider_float(tag=song_slider_tag, default_value=0.0, min_value=0.0, max_value=1.0, width=400, callback=on_song_slider_change, format="")
            add_text("00:00 / 00:00", tag="song_time_text")

        add_spacer(height=20)
        add_button(label="Quit", callback=lambda: quit_program())

    create_viewport(title='LYTE Control Panel', width=670, height=100)

    setup_dearpygui()
    show_viewport()
    set_primary_window("MainWindow", True)
    start_dearpygui()
    destroy_context()

def run_gui_thread():
    threading.Thread(target=build_gui, daemon=True).start()

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

run_gui_thread()
threading.Thread(target=vlc_loop, daemon=True).start()
threading.Thread(target=poll_chat, daemon=True).start()
threading.Thread(target=update_slider_thread, daemon=True).start()

while True:
    time.sleep(1)
