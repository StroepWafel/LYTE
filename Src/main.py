import time
import json
import os
import logging
import subprocess
import sys
from collections import defaultdict
import platform
from datetime import datetime
import pytchat
import yt_dlp

# Specify the folder to store logs
LOG_FOLDER = 'logs'

# Ensure the log and audio folders exist
os.makedirs(LOG_FOLDER, exist_ok=True)
os.makedirs("audio", exist_ok=True)

# Set up logging system
log_filename = os.path.join(LOG_FOLDER, f"app_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log")
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Set up file handler to log to a file with the generated log filename
file_handler = logging.FileHandler(log_filename)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
file_handler.setLevel(logging.INFO)

# Add the file handler to the logger
logging.getLogger().addHandler(file_handler)

try:
    # Load configuration from config.json
    with open('config.json', 'r', encoding="utf-8") as f:
        config = json.load(f)
    with open("banned_IDs.json", "r", encoding="utf-8") as f:
        bannedIDs = json.load(f)
except FileNotFoundError as e:
    logging.critical("File not found: %s", e)
    sys.exit(1)
except KeyError as e:
    logging.critical("Missing key: %s", e)
    sys.exit(1)
except json.JSONDecodeError as e:
    logging.critical("Error parsing JSON: %s", e)
    sys.exit(1)
except Exception as e:
    logging.error("An unexpected error occurred while loading files: %s", e)
    sys.exit(1)

YOUTUBE_VIDEO_ID = config.get("YOUTUBE_VIDEO_ID", "")
RATE_LIMIT_SECONDS = config.get('RATE_LIMIT_SECONDS', 10)
VLC_PATH = config.get('VLC_PATH', "vlc")
FFMPEG_PATH = config.get('FFMPEG_PATH', "ffmpeg")
if FFMPEG_PATH == "PATH_TO_FFMPEG_HERE" and "Linux" in platform.platform():
    FFMPEG_PATH = "/usr/bin/ffmpeg"
if FFMPEG_PATH == "PATH_TO_FFMPEG_HERE" and "Windows" in platform.platform():
    FFMPEG_PATH = "ffmpeg\\ffmpeg.exe"
PREFIX = config.get('PREFIX', "!")
QUEUE_COMMAND = config.get('QUEUE_COMMAND', "queue")
BANNED_IDS = bannedIDs

user_last_command = defaultdict(lambda: 0)

# Video queue
video_queue = []

VLC_STARTCOMMAND = f'"{VLC_PATH}" --one-instance'
try:
    vlc_process = subprocess.Popen(VLC_STARTCOMMAND, shell=True)  # pylint: disable=consider-using-with
except Exception as e:
    logging.critical("Failed to start VLC: %s", e)
    sys.exit(1)

def play_next_video():
    """Plays the next video in the queue."""
    try:
        if video_queue:
            next_video_id = video_queue.pop(0)
            logging.info("Now downloading and adding to VLC queue: %s", next_video_id)

            audio_file = download_audio(next_video_id)
            add_to_vlc_queue(audio_file)
        else:
            logging.info("Queue is empty. Waiting for new videos...")
    except Exception as e:
        logging.error("Error in play_next_video: %s", e)

def download_audio(video_id):
    """Downloads audio for the given YouTube Music video ID."""
    try:
        video_url = f"https://music.youtube.com/watch?v={video_id}"
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join("audio", f"{video_id}.%(ext)s"),  
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'noplaylist': True,
            'quiet': True,
            'ffmpeg_location': config["FFMPEG_PATH"]
        }

        if f'{video_id}.mp3' in os.listdir("audio"):
            logging.info("File already exists, adding to queue!")
            return os.path.join("audio", f"{video_id}.mp3")
        
        logging.info("File not downloaded, downloading...")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
            return os.path.join("audio", f"{video_id}.mp3")
    except yt_dlp.DownloadError as e:
        logging.error("Download error: %s", e)
        return ""
    except Exception as e:
        logging.error("Error downloading audio: %s", e)
        return ""

def add_to_vlc_queue(audio_file):
    """Adds the downloaded audio file to VLC's playlist queue."""
    try:
        if not audio_file:
            logging.warning("No audio file provided to add_to_vlc_queue.")
            return
        vlc_command = f'"{VLC_PATH}" --one-instance --playlist-enqueue "{audio_file}"'
        with subprocess.Popen(vlc_command, shell=True):
            pass
        logging.info("Added %s to VLC queue.", audio_file)
    except subprocess.SubprocessError as e:
        logging.error("Error adding video to VLC queue: %s", e)

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
            
            video_queue.append(video_id)
            user_last_command[username] = current_time
            logging.info("%s added to queue: %s", username, video_id)
            
            if len(video_queue) == 1:
                play_next_video()
    except Exception as e:
        logging.error("Error processing chat message: %s", e)

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
        logging.critical("An error occurred: %s", e)
        sys.exit(1)

start_chat_listener()
