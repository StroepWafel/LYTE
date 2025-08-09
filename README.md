![LYTE](https://socialify.git.ci/NIDNHU/YTLM/image?description=1&font=Source+Code+Pro&forks=1&issues=1&language=1&name=1&owner=1&pattern=Solid&pulls=1&stargazers=1&theme=Dark)
# LYTE
Live YouTube Entertainment (LYTE) is a program that allows viewers of a live stream to use commands to queue music

# Donating
If you make money from the use of or find this program helpful and interesting, you can support me on [GitHub Sponsors](https://github.com/sponsors/StroepWafel). Your support is completely optional, but it helps me keep building tools like this — and maybe one day, turn it into my full-time job!

# Contents:

- [Commands](#commands)
  - [!queue](#queue)
- [Setup](#setup)
  - [Quick Installer](#quick-installer)
- [Config Documentation](#config-documentation)
  - [YOUTUBE_VIDEO_ID](#youtube_video_id)
  - [RATE_LIMIT_SECONDS](#rate_limit_seconds)  
  - [TOAST_NOTIFICATIONS](#toast_notifications)
  - [PREFIX](#prefix)  
  - [QUEUE_COMMAND](#queue_command)
  - [DARK_MODE](#dark_mode)
  - [ALLOW_URLS](#allow_urls)
  - [REQUIRE_MEMBERSHIP](#require_membership)
  - [REQUIRE_SUPERCHAT](#require_superchat)
  - [MINIMUM_SUPERCHAT](#minimum_superchat)
  - [banned_IDs.json](#banned_idsjson)
  - [banned_users.json](#banned_usersjson)
- [Gallery](#gallery)
- [Notes](#notes)
- [Stars](#stars)
 
## Commands

### !queue

The default command to queue a song is `!queue <VIDEO_ID>`, where `<VIDEO_ID>` is the ID for the YouTube music video (everything after `?v=`). The command listener (default `!`) and command (default `queue`) can be changed in the [config](#config-documentation) if desired.

> [!IMPORTANT]
>By default, this command only works with IDs of videos that are on YouTube Music; regular videos will not play. This is because YouTube blocks links in livestream chats<!-- if the streamer has `Block links` enabled -->.

> [!WARNING]
> This Program is known to not work on linux, I am working on this, but it is not my main priority. if you have gotten it to work on linux without removing any functionality, you can create a PR, and I will review it.

## Setup

### Quick Installer:
1. Download [LYTE_INSTALLER](https://github.com/StroepWafel/LYTE-NSIS-Installer/releases/latest/download/LYTE_Installer.zip) and extract the folder (Installer source files can be found [here](https://github.com/StroepWafel/LYTE-NSIS-Installer))
2. Run LYTE_Installer.exe and follow the prompts
3. The program can also be uninstalled easily through this method

### EXE installation:
1. Download and extract the [latest release](https://github.com/NIDNHU/YTLM/releases/tag/release)'s .exe file to any folder on your computer (this is because the .exe will create files upon execution)
2. If not installed already, install [Python](https://www.python.org/downloads/). During installation, please make sure the box at the bottom labelled "add Python.exe to PATH" is ticked
3. Check whether pip was added to Path correctly by running `pip install --upgrade pip` in the terminal; this will both make sure pip is correctly installed and that it is up-to-date
4. Install [VLC](https://www.videolan.org/vlc/) for your computer appropiately. **MAKE SURE TO USE THE SAME ARCHITECTURE AS YOUR PYTHON INSTALL**
> [!IMPORTANT]
> VLC's architecture MUST be the same as python (often x64), to install x64 VLC, on the downloads page click the arrow on the right of `Download VLC` and select `Windows 64bit`
5. Run the `LYTE.exe` file located in whatever folder you saved the release to.
> [!IMPORTANT]  
> If you are using Windows, a pop-up may appear stating that "Windows Protected Your PC." If you trust this program, click "More info" then "Run anyway"
5. In the window that opened, change `LIVESTREAM_ID` to the ID of your live stream (Ie, the characters at the end of the URL, after the `?v=`)
6. *OPTIONAL*: Change the other configs. Documentation can be found in [Config Documentation](#config-documentation)
7. Press "Save and Start"
8. A separate window will open, here you can play/pause, skip the song or go back, refresh the UI, change the volume, or scrub through the music. You can also open the settings tab to edit the settings while the program is running, and you can toggle the light or dark mode.
9. If you want to quit the program, please use the `Quit` button; otherwise, the program may not close correctly, and you will have to close the terminal manually.


### Python file installation:
1. Download and extract the source to any folder on your computer (clone repo or download [latest release](https://github.com/NIDNHU/YTLM/releases/tag/release) source code)
2. If not installed already, install [Python](https://www.python.org/downloads/). During installation, please make sure the box at the bottom labelled "add Python.exe to PATH" is ticked
3. Check whether pip was added to Path correctly by running `pip install --upgrade pip`; this will both make sure pip is correctly installed and that it is up-to-date
4. Install the required Python libraries (found in Src/requirements.txt) using pip (normally included in Python)
5. Install [VLC](https://www.videolan.org/vlc/) for your computer appropiately.
> [!IMPORTANT]
> VLC's architecture MUST be the same as python (often x64), to install x64 VLC, on the downloads page click the arrow on the right of `Download VLC` and select `Windows 64bit`
6. Run main.py in the src folder:\
For Windows:
    - Press Win+r to open the run dialogue
    - Type "cmd" and hit Enter to open the command prompt
    - Using the command prompt, navigate to where you downloaded the files (using `cd <path to folder>`)
    - Navigate to the src folder: `cd YTLM-main/src`
    - Type `python main.py` and hit enter
7. In the window that opened, change `LIVESTREAM_ID` to the ID of your live stream (Ie, the characters at the end of the URL, after the `?v=`)
8. *OPTIONAL*: Change the other configs. Documentation can be found in [Config Documentation](#config-documentation)
9. Press "Save and Start"
10. A separate window will open, here you can play/pause, skip the song or go back, refresh the UI, change the volume, or scrub through the song. You can also open the settings tab to edit the settings while the program is running and you can toggle the light or dark mode.
11. If you want to quit the program, please use the `Quit` button; otherwise, the program may not close correctly,y and you will have to close the terminal manually.



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
This configuration option determines whether the UI will use dark or light mode

### ALLOW_URLS
This configuration option determines whether users can request songs with full URLs

### REQUIRE_MEMBERSHIP
This configuration option determines whether users need to be a member of the channel to request a song

### REQUIRE_SUPERCHAT
This configuration option determines whether users need to send a superchat to request a song

### MINIMUM_SUPERCHAT
This configuration option is supplementary to [REQUIRE_SUPERCHAT](#require_superchat) and determines the minimum value of the superchat (in USD) that the user must spend to request a song.

### banned_IDs.json
This file is used to store all banned YouTube video IDs. For the time being, you will have to add them manually to the file. Each video ID should be in quotation marks and separated by commas, for example:
```JSON
["Video ID 1", "Video ID 2", "Video ID 3"]
```

### banned_users.json
This file is used to store all banned YouTube user Ids. For the time being, you will have to add them manually to the file, each Id should be in quotation marks and separated by commas, for example:
```JSON
["name 1", "name 2", "name 3"]
```
To find a channel's ID you can use [this site](https://www.tunepocket.com/youtube-channel-id-finder/) or look in the logs

# Gallery

Settings UI:  
<img width="676" height="407" alt="Settings UI" src="https://github.com/user-attachments/assets/a707cf1d-2b41-4979-af96-5202d3aa583e" />  
Control Panel:  
<img width="681" height="407" alt="Control Panel" src="https://github.com/user-attachments/assets/1c4701aa-4d4a-4bf5-be86-15b2e75d0be2" />  


# Notes

- This program can be run on any Windows PC with no API key or cookie required
- If used, please credit the repository in the description or somewhere in the video

## Stars

[![Star History Chart](https://api.star-history.com/svg?repos=StroepWafel/LYTE&type=Date)](https://www.star-history.com/#StroepWafel/LYTE&Date)
