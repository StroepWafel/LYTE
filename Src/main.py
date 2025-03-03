"""YouTube live chat bot for queueing and playing YouTube Music videos via VLC."""

import time
import json
import os
import subprocess
from collections import defaultdict
import pytchat
import yt_dlp

# Load configuration from config.json
config = json.load(open('config.json', 'r'))

YOUTUBE_VIDEO_ID = config["YOUTUBE_VIDEO_ID"]
RATE_LIMIT_SECONDS = config['RATE_LIMIT_SECONDS']
VLC_PATH = config['VLC_PATH']
PREFIX = config['PREFIX']
QUEUE_COMMAND = config['QUEUE_COMMAND']
user_last_command = defaultdict(lambda: 0)


# Video queue
video_queue = []


VLC_STARTCOMMAND = f'"{VLC_PATH}" --one-instance'
subprocess.Popen(VLC_STARTCOMMAND, shell=True)

def play_next_video():
    """Plays the next video in the queue."""
    if video_queue:
        next_video_id = video_queue.pop(0)
        print(f"Now downloading and adding to VLC queue: {next_video_id}")

        # Download the audio and get the file path
        audio_file = download_audio(next_video_id)
        add_to_vlc_queue(audio_file)  # Add the audio file to VLC queue
    else:
        print("Queue is empty. Waiting for new videos...")

def download_audio(video_id):
    global config
    """Downloads audio for the given YouTube Music video ID."""
    video_url = f"https://music.youtube.com/watch?v={video_id}"

    ydl_opts = {
        'format': 'bestaudio/best',
        #Download directory
        'outtmpl': os.path.join("audio", f"{video_id}.%(ext)s"),  
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'noplaylist': True,
        'quiet': True,
        'ffmpeg_location': config["FFMPEG_PATH"]  # Use the path from config
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])  # Download the audio
        # Return the path of the downloaded audio file
        return os.path.join("audio", f"{video_id}.mp3")

def add_to_vlc_queue(audio_file):
    """Adds the downloaded audio file to VLC's playlist queue."""
    try:
        # Ensure the VLC path is quoted
        vlc_command = f'"{VLC_PATH}" --one-instance --playlist-enqueue "{audio_file}"'
        with subprocess.Popen(vlc_command, shell=True):  # Execute command in shell
            pass
        print(f"Added {audio_file} to VLC queue.")
    except (subprocess.SubprocessError, OSError) as e:
        print(f"Error adding video to VLC queue: {e}")

def on_chat_message(chat):
    global PREFIX
    global QUEUE_COMMAND
    """Handles incoming chat messages."""
    username = chat.author.name
    message = chat.message
    current_time = time.time()

    # Check if the message starts with !queue
    if message.startswith(f"{PREFIX}{QUEUE_COMMAND}"):
        parts = message.split()
        if len(parts) < 2:
            return  # Ignore invalid command format

        video_id = parts[1]  # Expecting just the video ID

        # Enforce rate limit
        if current_time - user_last_command[username] < RATE_LIMIT_SECONDS:
            print(f"{username} is sending commands too fast! Ignored.")
            return

        # Add to queue and update rate limit
        video_queue.append(video_id)
        user_last_command[username] = current_time
        print(f"{username} added to queue: {video_id}")

        # If nothing is playing, start playback
        if len(video_queue) == 1:
            play_next_video()

def start_chat_listener():
    '''Start listening to YouTube chat'''
    print("Listening to YouTube Live Chat...")
    chat = pytchat.create(video_id=YOUTUBE_VIDEO_ID)
    while chat.is_alive():
        for message in chat.get().sync_items():
            on_chat_message(message)  # Handle chat messages for song queuing
        time.sleep(1)


start_chat_listener()
