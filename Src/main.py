"""
YTLM uses pytchat to fetch the chat of a youtube livestream so that the
viewers can use commands to queue music on the streamer's PC
"""

import time
import json
import os
import logging
import sys
import re
import tkinter as tk
from tkinter import Button, PhotoImage
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
    """ Get the absolute path to the resource, works for dev and bundled versions """
    try:
        # PyInstaller creates a temporary folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

APP_FOLDER = get_app_folder()

# Specify the folder to store logs
LOG_FOLDER = os.path.join(APP_FOLDER, 'logs')
os.makedirs(LOG_FOLDER, exist_ok=True)

# Set up logging system
log_filename = os.path.join(LOG_FOLDER, f"app_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log")
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
file_handler = logging.FileHandler(log_filename)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
file_handler.setLevel(logging.INFO)
logging.getLogger().addHandler(file_handler)

# disable annoying post request logs
logging.getLogger("urllib3").setLevel(logging.ERROR)
logging.getLogger('httpx').setLevel(logging.ERROR)
logging.getLogger('httpcore').setLevel(logging.ERROR)

default_config = {
    "YOUTUBE_VIDEO_ID": "LIVESTREAM_ID",
    "RATE_LIMIT_SECONDS": 240,
    "TOAST_NOTIFICATIONS": "True",
    "PREFIX": "!",
    "QUEUE_COMMAND": "queue"
}
default_banned_IDs = []
default_banned_users = []

wasMissingAConfig = False

def ensure_file_exists(filepath, default_content):
    global wasMissingAConfig
    if not os.path.isfile(filepath):
        wasMissingAConfig = True
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(default_content, f, indent=4)
        logging.info(f"Created missing file: {filepath}")


# Full paths to config files
CONFIG_PATH = os.path.join(APP_FOLDER, 'config.json')
BANNED_IDS_PATH = os.path.join(APP_FOLDER, 'banned_IDs.json')
BANNED_USERS_PATH = os.path.join(APP_FOLDER, 'banned_users.json')

try:
    ensure_file_exists(CONFIG_PATH, default_config)
    ensure_file_exists(BANNED_IDS_PATH, default_banned_IDs)
    ensure_file_exists(BANNED_USERS_PATH, default_banned_users)

    if wasMissingAConfig:
        logging.critical("One or more config files were created, please make any necessary changes to the file and restart")
        sys.exit(1)

    with open(CONFIG_PATH, 'r', encoding="utf-8") as f:
        config = json.load(f)
    with open(BANNED_IDS_PATH, 'r', encoding="utf-8") as f:
        bannedIDs = json.load(f)
    with open(BANNED_USERS_PATH, 'r', encoding="utf-8") as f:
        bannedUsers = json.load(f)
except Exception as e:
    logging.critical("Error while loading files: %s", e)
    sys.exit(1)

YOUTUBE_VIDEO_ID = config.get("YOUTUBE_VIDEO_ID", "")
RATE_LIMIT_SECONDS = config.get('RATE_LIMIT_SECONDS', 10)
TOAST_NOTIFICATIONS = config.get('TOAST_NOTIFICATIONS', "True").lower() == "true"
PREFIX = config.get('PREFIX', "!")
QUEUE_COMMAND = config.get('QUEUE_COMMAND', "queue")
BANNED_IDS = bannedIDs
BANNED_USERS = bannedUsers

user_last_command = defaultdict(lambda: 0)

# Initialize VLC
instance = vlc.Instance("--one-instance")
player = instance.media_list_player_new()
media_list = instance.media_list_new()
player.set_media_list(media_list)
player.play()
logging.info("Started VLC...")

# Set up chat listener
try:
    chat = pytchat.create(video_id=YOUTUBE_VIDEO_ID)
except Exception as e:
    logging.critical("Error while listening to livestream chat: %s, Please fix the issue and try again", e)
    sys.exit(1)

# Gui Setup
root = tk.Tk()
root.title("YTLM Control Panel")

now_playing_label = tk.Label(root, text="Now Playing: Nothing", font=("Arial", 14))
now_playing_label.pack(pady=10)

# Button Functions
def update_now_playing():
    media = player.get_media_player().get_media()
    if media:
        media.parse_with_options(vlc.MediaParseFlag.local, timeout=1000)
        
        # Fetch the title metadata directly from VLC
        name = media.get_meta(vlc.Meta.Title)

        # Fallback to the YouTube title if VLC's title metadata isn't available
        if not name:
            youtube_url = media.get_mrl()  # Get the MRL (Media Resource Locator) URL (YouTube URL)
            name = get_video_title(youtube_url)  # Fetch title from YouTube if VLC fails

        now_playing_label.config(text=f"Now Playing: {name}")
    else:
        now_playing_label.config(text="Now Playing: Nothing")

def play_pause():
    player.pause()  # note: toggles pause/play

def next_song():
    player.next()
    update_now_playing()

def previous_song():
    player.previous()
    update_now_playing()

def refresh_song():
    update_now_playing()
    
### In progress:
"""def refresh_configs():
    try:
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
    except Exception as e:
        logging.critical("Error while refreshing files: %s", e)"""


# end button functions

# --- Buttons ---
control_frame = tk.Frame(root)
control_frame.pack(pady=20)

play_icon = PhotoImage(file=resource_path("icons/play.png")).subsample(20, 20)
next_icon = PhotoImage(file=resource_path("icons/next.png")).subsample(20, 20)
prev_icon = PhotoImage(file=resource_path("icons/back.png")).subsample(20, 20)
refresh_icon = PhotoImage(file=resource_path("icons/refresh.png")).subsample(20, 20)

buttons_images = [play_icon, next_icon, prev_icon, refresh_icon]

Button(control_frame, 
       text="Play/Pause", 
       image=play_icon, 
       compound="left", 
       command=play_pause, 
       activebackground="lightblue", 
       activeforeground="black").grid(row=0, column=0, padx=5)
Button(control_frame, 
       text="Previous", 
       image=prev_icon, 
       compound="left", 
       command=previous_song, 
       activebackground="lightblue", 
       activeforeground="black").grid(row=0, column=2, padx=5)
Button(control_frame, 
       text="Next", 
       image=next_icon, 
       compound="left", 
       command=next_song, 
       activebackground="lightblue", 
       activeforeground="black").grid(row=0, column=1, padx=5)
Button(control_frame, 
       text="Refresh Song", 
       image=refresh_icon, 
       compound="left", 
       command=refresh_song, 
       activebackground="lightblue", 
       activeforeground="black").grid(row=0, column=3, padx=5)

### In progress:
"""Button(control_frame, 
       text="Refresh Config", 
       image=refresh_icon, 
       compound="left", 
       command=refresh_configs, 
       activebackground="lightblue", 
       activeforeground="black").grid(row=0, column=4, padx=5)"""


def show_toast(video_id, username):
    notification.notify(
        title="Requested by: " + username,
        message="Adding '" + get_video_name(video_id) + "' to queue",
        timeout=5  # Notification disappears after 5 seconds
    )
    
def get_video_title(youtube_url):
    ydl_opts = {
        'quiet': True,  # Suppress output
        'extract_flat': True,  # Only fetch metadata
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(youtube_url, download=False)
        return info['title']

def get_video_name(video_id):
    url = f"https://www.youtube.com/watch?v={video_id}"
    headers = {"User-Agent": "Mozilla/5.0"}  # Mimic browser
    response = requests.get(url, headers=headers)

    match = re.search(r'<title>(.*?)</title>', response.text)
    if match:
        title = match.group(1).replace(" - YouTube", "").strip()
        return title

def get_direct_url(youtube_url):
    ydl_opts = {'format': 'bestaudio'}  # Best audio or video stream
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(youtube_url, download=False)
        return info['url']  # Get the direct playable URL
    
def queue_song(youtube_url):
    try:
        direct_url = get_direct_url(youtube_url)  # Fetch the playable URL
        media = instance.media_new(direct_url)
        
        # Fetch the YouTube video title
        title = get_video_title(youtube_url)  # Use yt_dlp to get title
        media.set_meta(vlc.Meta.Title, title)  # Set VLC's title metadata

        media_list.add_media(media)
        logging.info(f"Queued: {youtube_url} as {title}")
        
        # Make sure VLC starts playing the media immediately after queuing
        if player.get_state() != vlc.State.Playing:
            logging.warning("player started, was not running")
            player.play()  # Start playing if not already playing
        else:
            logging.info("Player is already playing.")
    except Exception as e:
        logging.error(f"Error getting URL for {youtube_url}: {e}")


def on_chat_message(chat):
    """Handles incoming chat messages."""
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
    root.after(1000, poll_chat)  # poll every 1s


def vlc_loop():
    # Keep script running while VLC plays, even after playback ends
    while True:
        # Check if VLC player has ended but prevent script from closing
        if player.get_state() == vlc.State.Ended:
            logging.info("Playback finished. Waiting for new songs...")
            if media_list.count() > 0:
                # Ensure the player continues to play the next song
                player.play()
            # If there are no more songs, keep waiting for input
            time.sleep(1)

threading.Thread(target=vlc_loop, daemon=True).start()

poll_chat()
root.mainloop()

