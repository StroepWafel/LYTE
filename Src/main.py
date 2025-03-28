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
from collections import defaultdict
from datetime import datetime
import pytchat
import yt_dlp
import requests
from plyer import notification
import vlc  # Using python-vlc

# Specify the folder to store logs
LOG_FOLDER = 'logs'

# Ensure the log folder exists
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

try:
    # Load configuration from config.json
    with open('config.json', 'r', encoding="utf-8") as f:
        config = json.load(f)
    with open("banned_IDs.json", "r", encoding="utf-8") as f:
        bannedIDs = json.load(f)
    with open("banned_users.json", "r", encoding="utf-8") as f:
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

def show_toast(video_id, username):
    notification.notify(
        title="Requested by: " + username,
        message="Adding '" + get_video_name(video_id) + "' to queue",
        timeout=5  # Notification disappears after 5 seconds
    )

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
        direct_url = get_direct_url(youtube_url)
        media = instance.media_new(direct_url)
        media_list.add_media(media)
        logging.info(f"Queued: {youtube_url}")
        
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

            user_last_command[username] = current_time
            logging.info("%s added to queue: %s", username, video_id)
            
            if TOAST_NOTIFICATIONS:
                show_toast(video_id, username)

                
    except Exception as e:
        logging.error("Unexpected error processing chat message: %s", e)

def start_chat_listener():
    """Start listening to YouTube chat."""
    try:
        logging.info("Listening to YouTube Live Chat...")
        chat = pytchat.create(video_id=YOUTUBE_VIDEO_ID)
        while chat.is_alive():
            for message in chat.get().sync_items():
                on_chat_message(message)
            time.sleep(1)
    except Exception as e:
        logging.critical("An unexpected error occurred in chat listener: %s", e)
        sys.exit(1)

start_chat_listener()

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