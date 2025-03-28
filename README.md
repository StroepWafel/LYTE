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
6. Download the correct version for your OS, extract it and navigate to the bin folder
      - __Windows:__ [Windows FFmpeg](https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip)
      - __MacOS:__ [MacOS FFmpeg](https://evermeet.cx/ffmpeg/ffmpeg-7.1.1.zip"). Ignore the next step; put the default path into the JSON.
      - __Linux:__ Linux FFmpeg: Use your package manager (e.g. `sudo apt install ffmpeg` or `sudo pacman -S ffmpeg`). Ignore the next step; put the default path into the JSON.
8. __(Windows ONLY)__ Move everything from the bin folder to src/ffmpeg and then delete the placeholder file "DELETEME".
9. Locate the path of the VLC media player, generally found in `C:\Program Files\VideoLAN\VLC\vlc.exe` or `C:\Program Files (x86)\VideoLAN\VLC\vlc.exe` by right clicking the file and selecting "Copy as path"
10. Locate the path of the 
11. Open the file config.json in your text editor of choice, I recommend [VSCode](https://code.visualstudio.com/download) or [Notepad++](https://notepad-plus-plus.org/downloads/v8.6.7/)
12. Change `YOUR\_LIVESTREAM\_ID` to the ID of your live stream (Ie, the characters at the end of the URL, after the `/live/`)
13. Change the value for `RATE\_LIMIT\_SECONDS`. This is how long users have to wait before they can request another song (in seconds)
14. Replace `PATH\_TO\_VLC\_HERE` with the path to your VLC&#x20;
15. Run main.py, and VLC will open.

> [!CAUTION]
>__ON WINDOWS, USE DOUBLE BACKSLASHES INSTEAD OF SINGLE, `C:\Program Files\VideoLAN\VLC\vlc.exe` MUST BECOME `C:\\Program Files\\VideoLAN\\VLC\\vlc.exe` (do the same with the ffmpeg.exe location). Linux and MacOS users only need to use a single slash `/`__

> [!TIP]
>Please turn off loop mode in VLC; otherwise, if the song queue runs out, you will have to listen to the whole playlist again before you get to the new ones


## Config Documentation

### YOUTUBE_VIDEO_ID
This is where you enter the ID to your youtube video.

### RATE_LIMIT_SECONDS
How long a user has to wait before they can queue another song, in seconds.

### VLC_PATH
The path to your local VLC install (including the .exe name)

### FFMPEG_PATH
The path to your local ffmpeg install (including the .exe name)

### TOAST_NOTIFICATIONS
>[!CAUTION]
>The following setting is case sensitive, please make sure to use a capital "T" when writing "True"\

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

- This program can be run on any Windows PC with no API key or cookie required
- If used, please credit the repository in the description or somewhere in the video


## Star history

[![Star History Chart](https://api.star-history.com/svg?repos=NIDNHU/YTLM\&type=Date)](https://star-history.com/#NIDNHU/YTLM\&Date)
