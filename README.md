![LYTE](https://socialify.git.ci/NIDNHU/YTLM/image?description=1&font=Source+Code+Pro&forks=1&issues=1&language=1&name=1&owner=1&pattern=Solid&pulls=1&stargazers=1&theme=Dark)
# LYTE
Live YouTube Entertainment (LYTE) is a program that allows viewers of a live stream to use commands to queue music

# Contents:

- [Commands](#commands)
  - [!queue](#queue)
- [Setup](#setup)
- [Config Documentation](#config-documentation)
  - [YOUTUBE_VIDEO_ID](#youtube_video_id)
  - [RATE_LIMIT_SECONDS](#rate_limit_seconds)  
  - [TOAST_NOTIFICATIONS](#toast_notifications)
  - [PREFIX](#prefix)  
  - [QUEUE_COMMAND](#queue_command)
  - [DARK_MODE](#dark_mode)
  - [banned_IDs.json](#banned_idsjson)
  - [banned_users.json](#banned_usersjson)
- [Notes](#notes)  
 
## Commands

### !queue

The default command to queue a song is `!queue <VIDEO_ID>`, where `<VIDEO_ID>` is the ID for the youtube music video (everything after `?v=`). The command listener (default `!`) and command (default `queue`) can be changed in the [config](#config-documentation) if desired.

> [!IMPORTANT]
>By default, this command only works with IDs of videos that are on YouTube Music; regular videos will not download. This is because youtube likes to block links in comments and chat to prevent self-promotion, or something.

> [!WARNING]
> This Program is known to not work on linux, I am working on this but it is not my main priority, if you have gotten it to work on linux without removing any functionality you can create a PR and I will review it.

## Setup

### EXE installation:
1. Download and extract the [latest release](https://github.com/NIDNHU/YTLM/releases/tag/release)'s .exe file to any folder on your computer (this is because the .exe will create files upon execution)
2. If not installed already, install [Python](https://www.python.org/downloads/). During installation, please make sure the box at the bottom labelled "add Python.exe to PATH" is ticked
3. Check whether pip was added to Path correctly by running `pip install --upgrade pip` in terminal; this will both make sure pip is correctly installed and that it is up-to-date
4. Run the `LYTE.exe` file located in whatever folder you saved the release to.
> [!IMPORTANT]  
> If you are using windows, a popup may appear stating that "Windows Protected Your PC." if you trust this program, click "More info" then "Run anyway"
5. In the window that opened, change `LIVESTREAM_ID` to the ID of your live stream (Ie, the characters at the end of the URL, after the `?v=`)
6. *OPTIONAL*: change the other configs, documentation can be found in [Config Documentation](#config-documentation)
7. Press "Save and Start"
8. A seperate window will open, here you can play/pause, skip the song or go back, refresh the UI, change the volume, or scrub through the song. You can also open the settings tab to edit the settings while the program is running and you can toggle the light or dark mode.
9. If you want to quit the program, please use the `Quit` button, otherwise the program may not close correctly and you will have to close the terminal manually.


### Python file installation:
1. Download and extract the source to any folder on your computer (clone repo or download [latest release](https://github.com/NIDNHU/YTLM/releases/tag/release) source code)
2. If not installed already, install [Python](https://www.python.org/downloads/). During installation, please make sure the box at the bottom labelled "add Python.exe to PATH" is ticked
3. Check whether pip was added to Path correctly by running `pip install --upgrade pip`; this will both make sure pip is correctly installed and that it is up-to-date
4. Install the required python libraries (found in Src/requirements.txt) using pip (normally included in Python)
5. Install [VLC](https://www.videolan.org/vlc/) for your computer appropiately. **MAKE SURE TO USE THE SAME ARCHITECTURE AS YOUR PYTHON INSTALL**
6. Run main.py in the src folder:\
For windows:
    - Press Win+r to open the run dialogue
    - Type "cmd" and hit enter to open command prompt
    - Using command prompt, navigate to where you downloaded the files (using `cd <path to folder>`)
    - Navigate to the src folder: `cd YTLM-main/src`
    - Type `python main.py` and hit enter
7. In the window that opened, change `LIVESTREAM_ID` to the ID of your live stream (Ie, the characters at the end of the URL, after the `?v=`)
8. *OPTIONAL*: change the other configs, documentation can be found in [Config Documentation](#config-documentation)
9. Press "Save and Start"
10. A seperate window will open, here you can play/pause, skip the song or go back, refresh the UI, change the volume, or scrub through the song. You can also open the settings tab to edit the settings while the program is running and you can toggle the light or dark mode.
11. If you want to quit the program, please use the `Quit` button, otherwise the program may not close correctly and you will have to close the terminal manually.



## Config Documentation

### YOUTUBE_VIDEO_ID
This is where you enter the ID of your livestream.

### RATE_LIMIT_SECONDS
How long a user has to wait before they can queue another song, in seconds.

### TOAST_NOTIFICATIONS
Setting this to ```True``` (default) will enable toast notifications that pop up with the song name and requester, setting it to any other value will disable these notifications. This option is not case sensitive

### PREFIX
This configuration option allows you to set any character as the listener prefix for commands. To do this, change the value in quotation marks to whatever you desire — it can even be multiple characters!

### QUEUE_COMMAND
This configuration option allows you to set any string as the command for queueing a song. Simply change the value in the quotation marks to the desired command.

### DARK_MODE
this configuration option determines whether the UI will use dark or light mode

### banned_IDs.json
this file is used to store all banned youtube video IDs, for the time being you will have to add them manually to the file, each video id should be in quotation marks and seperated by commas, for example:
```JSON
["Video ID 1", "Video ID 2", "Video ID 3"]
```

### banned_users.json
this file is used to store all banned youtube usernames (at some point i will try to make this use handles), for the time being you will have to add them manually to the file, each name should be in quotation marks and seperated by commas, for example:
```JSON
["name 1", "name 2", "name 3"]
```
# Notes

- This program can be run on any windows PC with no API key or cookie required
- If used, please credit the repository in the description or somewhere in the video

## Stars

[![Star History Chart](https://api.star-history.com/svg?repos=NIDNHU/YTLM\&type=Date)](https://star-history.com/#NIDNHU/YTLM\&Date)
