# YTLM
YouTube Live Music  (YTLM) is a stupid little bot I coded (with a little help from AI) that allows viewers of a live stream to use commands to queue music

# Contents:

- [Commands](#commands)  
  - [!queue](#queue)  
- [Setup](#setup)
- [Config Documentation](#config-documentation))
- [Notes](#notes)  
 
## Commands

### !queue

The command to queue a song is "!queue \<VIDEO\_URL>" where \<VIDEO\_URL> is the Url for the youtube music video (everything after the "v=")&#x20;

> [!IMPORTANT]
>THIS COMMAND ONLY WORKS WITH URLs OF VIDEOS THAT ARE ON YOUTUBE MUSIC; REGULAR VIDEOS WILL NOT DOWNLOAD

## Setup

1. Download and extract the source to any folder on your computer (clone repo or download [latest release](https://github.com/NIDNHU/YTLM/releases/tag/release))
2. Install [Python](https://www.python.org/downloads/). During installation, please make sure the box at the bottom labelled "add Python.exe to PATH" is ticked
3. Check whether pip was added to Path correctly by running `pip install --upgrade pip`; this will both make sure pip is correctly installed and that it is up-to-date
4. Install the required python libraries (found in Src/requirements.txt) using pip (normally included in Python)
5. Install [VLC](https://www.videolan.org/vlc/) for your computer appropiately.
6. Download the correct version for your OS, extract it and navigate to the bin folder
      - __Windows:__ [Windows FFmpeg](https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip)
      - __MacOS:__ [MacOS FFmpeg](https://evermeet.cx/ffmpeg/ffmpeg-7.1.1.zip"). Ignore the next step; put the default path into the JSON.
      - __Linux:__ Linux FFmpeg: Use your package manager (e.g. `sudo apt install ffmpeg` or `sudo pacman -S ffmpeg`). Ignore the next step; put the default path into the JSON.
8. __(Windows ONLY)__ Move everything from the bin folder to src/ffmpeg and then delete the placeholder file "DELETEME".
9. Locate the path of the VLC media player, generally found in "C:\Program Files\VideoLAN\VLC" or "C:\Program Files (x86)\VideoLAN\VLC"
10. Open the file "config.json" in your text editor of choice, I recommend [VSCode](https://code.visualstudio.com/download) or [Notepad++](https://notepad-plus-plus.org/downloads/v8.6.7/)
11. Change "YOUR\_LIVESTREAM\_ID" to the ID of your live stream (Ie, the characters at the end of the URL, after the "/live/")
12. Change the value for "RATE\_LIMIT\_SECONDS". This is how long users have to wait before they can request another song (in seconds)
13. Replace "PATH\_TO\_VLC\_HERE" with the path to your VLC&#x20;
14. Run main.py, and VLC will open.

> [!CAUTION]
>__ON WINDOWS, USE DOUBLE BACKSLASHES INSTEAD OF SINGLE, `C:\Program Files\VideoLAN\VLC` MUST BECOME `C:\\\Program Files\\\VideoLAN\\\VLC\\\vlc.exe`. Linux and MacOS users only need to use a single slash `/`__

> [!TIP]
>Please turn off loop mode in VLC; otherwise, if the song queue runs out, you will have to listen to the whole playlist again before you get to the new ones


## Config Documentation

#Todo

## Notes

- This program can be run on any Windows PC with no API key or cookie required
- If used, please credit the repository in the description or somewhere in the video
- This program has not been tested on any other OS, and it is unknown if it works

## Star history

[![Star History Chart](https://api.star-history.com/svg?repos=NIDNHU/YTLM\&type=Date)](https://star-history.com/#NIDNHU/YTLM\&Date)
