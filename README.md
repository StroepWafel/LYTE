# YTLM
YouTube Live Music (YTLM) is a bot that allows viewers of a live stream to use commands to queue music

# Contents:

- [Commands](#commands)
  - [!queue](#queue)
- [Setup](#setup)
- [Config Documentation](#config-documentation)
  - [YOUTUBE_VIDEO_ID](#youtube_video_id)
  - [RATE_LIMIT_SECONDS](#rate_limit_seconds)  
  - [VLC_PATH](#vlc_path)  
  - [FFMPEG_PATH](#ffmpeg_path)
  - [TOAST_NOTIFICATIONS](#toast_notifications)
  - [PREFIX](#prefix)  
  - [QUEUE_COMMAND](#queue_command)
  - [banned_IDs.json](#banned_idsjson)
  - [banned_users.json](#banned_usersjson)
- [Notes](#notes)  
 
## Commands

### !queue

The default command to queue a song is "!queue \<VIDEO\_URL>" where \<VIDEO\_URL> is the Url for the youtube music video, however the command listener (exclamation mark) and command (the word queue) can be changed in the [config](#config-documentation) if desired.

> [!IMPORTANT]
>THIS COMMAND ONLY WORKS WITH URLs OF VIDEOS THAT ARE ON YOUTUBE MUSIC; REGULAR VIDEOS WILL NOT DOWNLOAD

## Setup

1. Download and extract the source to any folder on your computer (clone repo or download [latest release](https://github.com/NIDNHU/YTLM/releases/tag/release))
2. Install [Python](https://www.python.org/downloads/). During installation, please make sure the box at the bottom labelled "add Python.exe to PATH" is ticked
3. Check whether pip was added to Path correctly by running `pip install --upgrade pip`; this will both make sure pip is correctly installed and that it is up-to-date
4. Install the required python libraries (found in Src/requirements.txt) using pip (normally included in Python)
5. Install [VLC](https://www.videolan.org/vlc/) for your computer appropiately. **MAKE SURE TO USE THE SAME ARCHITECTURE AS YOUR PYTHON INSTALL**
6. Open the file config.json in your text editor of choice, I recommend [VSCode](https://code.visualstudio.com/download) or [Notepad++](https://notepad-plus-plus.org/downloads/v8.6.7/)
7. Change `LIVESTREAM\_ID` to the ID of your live stream (Ie, the characters at the end of the URL, after the `/live/`)
8. Change the value for `RATE\_LIMIT\_SECONDS`. This is how long users have to wait before they can request another song (in seconds)
9. Run main.py, and VLC will open.

## Config Documentation

### YOUTUBE_VIDEO_ID
This is where you enter the ID to your youtube video.

### RATE_LIMIT_SECONDS
How long a user has to wait before they can queue another song, in seconds.

### TOAST_NOTIFICATIONS
Setting this to ```True``` (default) will enable toast notifications that pop up with the song name and requester, setting it to any other value will disable these notifications

### PREFIX
This configuration option allows you to set any character as the listener prefix for commands. To do this, change the value in quotation marks to whatever you desire — it can even be multiple characters!

### QUEUE_COMMAND
This configuration option allows you to set any string as the command for queueing a song. Simply change the value in the quotation marks to the desired command.

### banned_IDs.json
this file is used to store all banned youtube video IDs, for the time being you will have to add them manually to the file, each video id should be in quotation marks and seperated by commas, for example:
```JSON
["<Video ID 1>", "<Video ID 2>", "<Video ID 3>"]
```

### banned_users.json
this file is used to store all banned youtube user handles, for the time being you will have to add them manually to the file, each handle should be in quotation marks and seperated by commas, for example:
```JSON
["<@Handle 1>", "<@Handle 2>", "<@Handle 3>"]
```
# Notes

- This program can be run on any PC with no API key or cookie required
- If used, please credit the repository in the description or somewhere in the video


## Star history

[![Star History Chart](https://api.star-history.com/svg?repos=NIDNHU/YTLM\&type=Date)](https://star-history.com/#NIDNHU/YTLM\&Date)
