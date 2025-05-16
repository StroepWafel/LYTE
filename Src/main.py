# Replaces the Tkinter GUI with NiceGUI
from nicegui import ui
import time
import json
import os
import logging
import sys
import re
import threading
from collections import defaultdict
from datetime import datetime
import pytchat
import yt_dlp
import requests
from plyer import notification
import vlc  # Using python-vlc

# Determine the base folder (works with PyInstaller onefile too)
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
latest_log_line = ui.label("Console: Starting up...").classes("text-sm p-2")

class UILogHandler(logging.Handler):
    def emit(self, record):
        msg = self.format(record)
        latest_log_line.text = f"Console: {msg}"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
file_handler = logging.FileHandler(log_filename)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
file_handler.setLevel(logging.INFO)
logging.getLogger().addHandler(file_handler)
logging.getLogger().addHandler(UILogHandler())
logging.getLogger("urllib3").setLevel(logging.ERROR)
logging.getLogger('httpx').setLevel(logging.ERROR)
logging.getLogger('httpcore').setLevel(logging.ERROR)

default_config = {
    "YOUTUBE_VIDEO_ID": "LIVESTREAM_ID",
    "RATE_LIMIT_SECONDS": 240,
    "TOAST_NOTIFICATIONS": "True",
    "PREFIX": "!",
    "QUEUE_COMMAND": "queue",
    "VOLUME": 50
}
default_banned_IDs = []
default_banned_users = []

CONFIG_PATH = os.path.join(APP_FOLDER, 'config.json')
BANNED_IDS_PATH = os.path.join(APP_FOLDER, 'banned_IDs.json')
BANNED_USERS_PATH = os.path.join(APP_FOLDER, 'banned_users.json')

config = default_config.copy()

if not os.path.exists(CONFIG_PATH):
    with ui.card().classes("p-4 m-4"):
        ui.label("Configuration Setup").classes("text-2xl")
        video_id_input = ui.input("YouTube Livestream ID", value=config['YOUTUBE_VIDEO_ID'])
        rate_limit_input = ui.input("Rate Limit Seconds", value=str(config['RATE_LIMIT_SECONDS']))
        notifications_checkbox = ui.checkbox("Enable Toast Notifications", value=config['TOAST_NOTIFICATIONS'].lower() == "true")
        prefix_input = ui.input("Command Prefix", value=config['PREFIX'])
        queue_command_input = ui.input("Queue Command", value=config['QUEUE_COMMAND'])
        volume_slider = ui.slider(min=0, max=100, value=config['VOLUME'], step=1).classes("w-64")
        ui.label().bind_text_from(volume_slider, 'value', lambda x: f"Volume: {x}%")

        def save_and_start():
            config['YOUTUBE_VIDEO_ID'] = video_id_input.value
            config['RATE_LIMIT_SECONDS'] = int(rate_limit_input.value)
            config['TOAST_NOTIFICATIONS'] = str(notifications_checkbox.value)
            config['PREFIX'] = prefix_input.value
            config['QUEUE_COMMAND'] = queue_command_input.value
            config['VOLUME'] = volume_slider.value

            with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4)

            logging.info("Config saved. Restarting program...")
            python = sys.executable
            os.execv(python, [python] + sys.argv)
            sys.exit()

        ui.button("Save & Start Program", on_click=save_and_start).classes("mt-4")
    

if os.path.exists(CONFIG_PATH):
    with open(CONFIG_PATH, 'r', encoding="utf-8") as f:
        config = json.load(f)

    with open(BANNED_IDS_PATH, 'w', encoding='utf-8') as f:
        json.dump(default_banned_IDs, f)
    with open(BANNED_USERS_PATH, 'w', encoding='utf-8') as f:
        json.dump(default_banned_users, f)

    YOUTUBE_VIDEO_ID = config.get("YOUTUBE_VIDEO_ID", "")
    RATE_LIMIT_SECONDS = config.get('RATE_LIMIT_SECONDS', 10)
    TOAST_NOTIFICATIONS = config.get('TOAST_NOTIFICATIONS', "True").lower() == "true"
    PREFIX = config.get('PREFIX', "!")
    QUEUE_COMMAND = config.get('QUEUE_COMMAND', "queue")
    VOLUME = config.get('VOLUME', 50)

    with open(BANNED_IDS_PATH, 'r', encoding="utf-8") as f:
        BANNED_IDS = json.load(f)
    with open(BANNED_USERS_PATH, 'r', encoding="utf-8") as f:
        BANNED_USERS = json.load(f)

    user_last_command = defaultdict(lambda: 0)

    instance = vlc.Instance("--one-instance")
    player = instance.media_list_player_new()
    media_list = instance.media_list_new()
    player.set_media_list(media_list)
    player.get_media_player().audio_set_volume(VOLUME)
    player.play()
    logging.info("Started VLC...")

    try:
        chat = pytchat.create(video_id=YOUTUBE_VIDEO_ID)
    except Exception as e:
        logging.critical("Error while listening to livestream chat: %s, Please fix the issue and try again", e)
        sys.exit(1)

    now_playing_label = ui.label("Now Playing: Nothing").classes("text-xl p-4")
    
    def reset_config():
        if os.path.exists(CONFIG_PATH):
            os.remove(CONFIG_PATH)
        logging.info("Config reset by user, restarting program...")
        python = sys.executable
        os.execv(python, [python] + sys.argv)
        sys.exit()

    with ui.row().classes("p-4 gap-4"):
        ui.button("Play/Pause", on_click=lambda: play_pause()).props("icon=play_arrow")
        ui.button("Previous", on_click=lambda: previous_song()).props("icon=skip_previous")
        ui.button("Next", on_click=lambda: next_song()).props("icon=skip_next")
        ui.button("Refresh Song", on_click=lambda: refresh_song()).props("icon=refresh")
        volume_control = ui.slider(min=0, max=100, value=VOLUME, step=1, on_change=lambda e: player.get_media_player().audio_set_volume(e.value)).classes("w-64")
        ui.label().bind_text_from(volume_control, 'value', lambda x: f"Volume: {x}%")

    ui.button("Reset Config (Delete & Restart)", on_click=reset_config).classes("mt-4").style("background-color: #f44336; color: white;")


    def update_now_playing():
        media = player.get_media_player().get_media()
        if media:
            media.parse_with_options(vlc.MediaParseFlag.local, timeout=1000)
            name = media.get_meta(vlc.Meta.Title)
            if not name:
                youtube_url = media.get_mrl()
                name = get_video_title(youtube_url)
            now_playing_label.text = f"Now Playing: {name}"
        else:
            now_playing_label.text = "Now Playing: Nothing"

    def play_pause():
        player.pause()

    def next_song():
        player.next()
        update_now_playing()

    def previous_song():
        player.previous()
        update_now_playing()

    def refresh_song():
        update_now_playing()

    def show_toast(video_id, username):
        notification.notify(
            title="Requested by: " + username,
            message="Adding '" + get_video_name(video_id) + "' to queue",
            timeout=5
        )

    def get_video_title(youtube_url):
        ydl_opts = {
            'quiet': True,
            'extract_flat': True,
        }
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

    def queue_song(youtube_url):
        try:
            direct_url = get_direct_url(youtube_url)
            media = instance.media_new(direct_url)
            title = get_video_title(youtube_url)
            media.set_meta(vlc.Meta.Title, title)
            media_list.add_media(media)
            logging.info(f"Queued: {youtube_url} as {title}")
            if player.get_state() != vlc.State.Playing:
                logging.warning("player started, was not running")
                player.play()
            else:
                logging.info("Player is already playing.")
        except Exception as e:
            logging.error(f"Error getting URL for {youtube_url}: {e}")

    def on_chat_message(chat):
        try:
            username = chat.author.name
            message = chat.message
            current_time = time.time()
            if message.startswith(f"{PREFIX}{QUEUE_COMMAND}"):
                parts = message.split()
                if len(parts) < 2:
                    return
                video_id = parts[1]
                if current_time - user_last_command[username] < RATE_LIMIT_SECONDS:
                    logging.warning("%s is sending commands too fast! Ignored.", username)
                    return
                if video_id in BANNED_IDS:
                    logging.warning("%s tried to add a banned song to the queue! Ignored.", username)
                    return
                if username in BANNED_USERS:
                    logging.warning("%s tried to queue a song but is banned! Ignored.", username)
                    return
                queue_song("https://www.youtube.com/watch?v=" + video_id)
                update_now_playing()
                user_last_command[username] = current_time
                logging.info("%s added to queue: %s", username, video_id)
                if TOAST_NOTIFICATIONS:
                    show_toast(video_id, username)
        except Exception as e:
            logging.error("Unexpected error processing chat message: %s", e)

    def poll_chat():
        if chat.is_alive():
            for message in chat.get().sync_items():
                on_chat_message(message)
        threading.Timer(1.0, poll_chat).start()

    def vlc_loop():
        while True:
            if player.get_state() == vlc.State.Ended:
                logging.info("Playback finished. Waiting for new songs...")
                if media_list.count() > 0:
                    player.play()
                time.sleep(1)

    threading.Thread(target=vlc_loop, daemon=True).start()
    poll_chat()

ui.run(title="YTLM Control Panel", reload=False)
