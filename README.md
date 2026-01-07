![LYTE](https://socialify.git.ci/StroepWafel/LYTE/image?description=1&font=Source+Code+Pro&forks=1&issues=1&language=1&name=1&owner=1&pattern=Solid&pulls=1&stargazers=1&theme=Dark)
# LYTE
Live YouTube Entertainment (LYTE) is a program that allows viewers of a live stream to use commands to queue music.

**Current Version: 1.9.0**

Documentation is also available at [https://stroepwafel.au/LYTE/documentation](https://stroepwafel.au/LYTE/documentation)

# Licensing
LYTE is licensed under the AGPL-3.0.

If you want to use LYTE in a commercial, proprietary, or hosted product without releasing your source code, a commercial license is available.

Contact: contact@stroepwafel.au

# Donating
If you make money from the use of or find this program helpful and interesting, you can support me on [GitHub Sponsors](https://github.com/sponsors/StroepWafel). Your support is completely optional, but it helps me keep building tools like this — and maybe one day, turn it into my full-time job!

# Contents:

- [Commands](#commands)
  - [!queue](#queue)
- [Setup](#setup)
  - [Quick Installer](#quick-installer)
  - [EXE Installation](#exe-installation)
  - [Python file Installation](#python-file-installation)
- [Temporarily Disabling real-time protection](#temporarily-disabling-real-time-protection)
- [Config Documentation](#config-documentation)
  - [YOUTUBE_VIDEO_ID](#youtube_video_id)
  - [RATE_LIMIT_SECONDS](#rate_limit_seconds)  
  - [TOAST_NOTIFICATIONS](#toast_notifications)
  - [PREFIX](#prefix)  
  - [QUEUE_COMMAND](#queue_command)
  - [VOLUME](#volume)
  - [THEME](#theme)
  - [ALLOW_URLS](#allow_urls)
  - [REQUIRE_MEMBERSHIP](#require_membership)
  - [REQUIRE_SUPERCHAT](#require_superchat)
  - [MINIMUM_SUPERCHAT](#minimum_superchat)
  - [ENFORCE_ID_WHITELIST](#enforce_id_whitelist)
  - [ENFORCE_USER_WHITELIST](#enforce_user_whitelist)
  - [AUTOREMOVE_SONGS](#autoremove_songs)
  - [AUTOBAN_USERS](#autoban_users)
  - [SONG_FINISH_NOTIFICATIONS](#song_finish_notifications)
  - [banned_IDs.json](#banned_idsjson)
  - [banned_users.json](#banned_usersjson)
  - [whitelisted_IDs.json](#whitelisted_idsjson)
  - [whitelisted_users.json](#whitelisted_usersjson)
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
1. Download [LYTE_Installer](https://github.com/StroepWafel/LYTE-NSIS-Installer/releases/download/latest/LYTE_Installer.exe) and extract the folder (Installer source files can be found [here](https://github.com/StroepWafel/LYTE-NSIS-Installer), you can even download from the action if you dont trust the release)
> [!IMPORTANT]  
> Windows sometimes takes offense to this file for some reason, so you may have to [temporarily disable Real-time protection](#temporarily-disabling-real-time-protection) for the time being.
2. Run LYTE_Installer.exe and follow the prompts
3. The program can also be uninstalled easily through this method

### EXE Installation:
1. Download and extract the [latest release](https://github.com/StroepWafel/LYTE/releases/latest)'s .exe file to any folder on your computer (this is because the .exe will create files upon execution)
2. If not installed already, install [Python](https://www.python.org/downloads/). During installation, please make sure the box at the bottom labelled "add Python.exe to PATH" is ticked
3. Check whether pip was added to Path correctly by running `pip install --upgrade pip` in the terminal; this will both make sure pip is correctly installed and that it is up-to-date
4. Install [VLC](https://www.videolan.org/vlc/) for your computer appropiately. **MAKE SURE TO USE THE SAME ARCHITECTURE AS YOUR PYTHON INSTALL**
> [!WARNING]
> VLC's architecture MUST be the same as python (often x64), to install x64 VLC, on the downloads page click the arrow on the right of `Download VLC` and select `Windows 64bit`
5. Run the `LYTE.exe` file located in whatever folder you saved the release to.
> [!IMPORTANT]  
> If you are using Windows, a pop-up may appear stating that "Windows Protected Your PC." If you trust this program, click "More info" then "Run anyway"
5. In the window that opened, change `YOUTUBE_VIDEO_ID` to the ID of your live stream (i.e., the characters at the end of the URL, after the `?v=`)
6. *OPTIONAL*: Change the other configs. Documentation can be found in [Config Documentation](#config-documentation)
7. Press "Save and Start"
8. A separate window will open, here you can play/pause, skip the song or go back, refresh the UI, change the volume, or scrub through the music. You can also open the settings tab to edit the settings while the program is running, and you can change themes from the View menu.
9. If you want to quit the program, please use the `Quit` button; otherwise, the program may not close correctly, and you will have to close the terminal manually.


### Python file Installation:
1. Download and extract the source to any folder on your computer (clone repo or download [latest release](https://github.com/StroepWafel/LYTE/releases/latest) source code)
2. If not installed already, install [Python](https://www.python.org/downloads/). During installation, please make sure the box at the bottom labelled "add Python.exe to PATH" is ticked
3. Check whether pip was added to Path correctly by running `pip install --upgrade pip`; this will both make sure pip is correctly installed and that it is up-to-date
4. Install the required Python libraries (found in Src/requirements.txt) using pip (normally included in Python)
5. Install [VLC](https://www.videolan.org/vlc/) for your computer appropiately.
> [!WARNING]
> VLC's architecture MUST be the same as python (often x64), to install x64 VLC, on the downloads page click the arrow on the right of `Download VLC` and select `Windows 64bit`
6. Run main.py in the Src folder:\
For Windows:
    - Press Win+r to open the run dialogue
    - Type "cmd" and hit Enter to open the command prompt
    - Using the command prompt, navigate to where you downloaded the files (using `cd <path to folder>`)
    - Navigate to the Src folder: `cd Src`
    - Type `python main.py` and hit enter
7. In the window that opened, change `YOUTUBE_VIDEO_ID` to the ID of your live stream (i.e., the characters at the end of the URL, after the `?v=`)
8. *OPTIONAL*: Change the other configs. Documentation can be found in [Config Documentation](#config-documentation)
9. Press "Save and Start"
10. A separate window will open, here you can play/pause, skip the song or go back, refresh the UI, change the volume, or scrub through the song. You can also open the settings tab to edit the settings while the program is running and you can change themes from the View menu.
11. If you want to quit the program, please use the `Quit` button; otherwise, the program may not close correctly, and you will have to close the terminal manually.

## Temporarily Disabling real-time protection
### For Windows 10:
1. Press Windows + S to open Search, type Windows Security in the text field, and click on the relevant result.
2. Click on Virus & threat protection.
3. Click on Manage settings under Virus & threat protection settings.
4. Disable the toggle under Real-time protection.
5. Confirm the action if prompted by User Account Control (UAC).
6. Re-enable the toggle under Real-time protection once you have finished installing.

### For Windows 11:
1. Press Windows + I to open Settings.
2. Go to Privacy & Security > Windows Security.
3. Click on Virus & threat protection.
4. Under Virus & threat protection settings, click Manage settings.
5. Toggle Real-time protection to Off.
6. Confirm the action if prompted by User Account Control (UAC).
7. Re-enable the toggle under Real-time protection once you have finished installing.

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

### VOLUME
This configuration option sets the default volume level (0-100) for audio playback.

### THEME
This configuration option determines which theme the UI will use. Available themes include `dark_theme` and `light_theme` by default. Custom themes can be added to the themes folder.

### ALLOW_URLS
This configuration option determines whether users can request songs with full URLs

### REQUIRE_MEMBERSHIP
This configuration option determines whether users need to be a member of the channel to request a song

### REQUIRE_SUPERCHAT
This configuration option determines whether users need to send a superchat to request a song

### MINIMUM_SUPERCHAT
This configuration option is supplementary to [REQUIRE_SUPERCHAT](#require_superchat) and determines the minimum value of the superchat (in USD) that the user must spend to request a song.

### ENFORCE_ID_WHITELIST
This configuration option determines whether only whitelisted video IDs can be requested. When enabled, only videos in the whitelisted_IDs.json file can be queued.

### ENFORCE_USER_WHITELIST
This configuration option determines whether only whitelisted users can request songs. When enabled, only users in the whitelisted_users.json file can queue songs.

### AUTOREMOVE_SONGS
This configuration option determines whether finished or skipped songs are automatically removed from the queue.

### AUTOBAN_USERS
This configuration option determines whether users who attempt to request banned videos are automatically banned.

### SONG_FINISH_NOTIFICATIONS
This configuration option determines whether desktop notifications are shown when a new song starts playing (only when songs finish naturally, not when skipped).

### banned_IDs.json
This file is used to store all banned YouTube video IDs. Each entry should be a JSON object with "id" and "name" fields, for example:
```JSON
[
  {"id": "dQw4w9WgXcQ", "name": "Video Name 1"},
  {"id": "jNQXAC9IVRw", "name": "Video Name 2"}
]
```

### banned_users.json
This file is used to store all banned YouTube user IDs. Each entry should be a JSON object with "id" and "name" fields, for example:
```JSON
[
  {"id": "UCxxxxxxxxxxxxxxxxxxxxx", "name": "Channel Name 1"},
  {"id": "UCyyyyyyyyyyyyyyyyyyyyy", "name": "Channel Name 2"}
]
```
To find a channel's ID you can use [this site](https://www.tunepocket.com/youtube-channel-id-finder/) or look in the logs.

### whitelisted_IDs.json
This file is used to store all whitelisted YouTube video IDs. Each entry should be a JSON object with "id" and "name" fields, for example:
```JSON
[
  {"id": "dQw4w9WgXcQ", "name": "Video Name 1"},
  {"id": "jNQXAC9IVRw", "name": "Video Name 2"}
]
```

### whitelisted_users.json
This file is used to store all whitelisted YouTube user IDs. Each entry should be a JSON object with "id" and "name" fields, for example:
```JSON
[
  {"id": "UCxxxxxxxxxxxxxxxxxxxxx", "name": "Channel Name 1"},
  {"id": "UCyyyyyyyyyyyyyyyyyyyyy", "name": "Channel Name 2"}
]
```

# Gallery

Settings UI:  
<img width="731" height="443" alt="SettingsUI" src="https://github.com/user-attachments/assets/5ed48e4f-61a2-4693-b605-c2dd849a9ff8" />


Control Panel:  
<img width="1311" height="459" alt="MainUI" src="https://github.com/user-attachments/assets/26a1b860-15bd-478a-a615-6d2204a7fbb6" />


# Notes

- This program can be run on any Windows PC with no API key or cookie required
- If used, please credit the repository in the description or somewhere in the video
- The program includes built-in update checking and can download installers automatically
- Themes can be customized by editing JSON files in the themes folder
- Queue history is available through the Moderation menu to help manage song requests

## Stars

[![Star History Chart](https://api.star-history.com/svg?repos=StroepWafel/LYTE&type=Date)](https://www.star-history.com/#StroepWafel/LYTE&Date)

## Code signing policy


