# LYTE Program Flow Chart

This document contains Mermaid flowcharts that outline the flow of the entire LYTE application.

## Main Application Flow

```mermaid
flowchart TD
    Start([Application Start]) --> Init[Initialize Application]
    Init --> SetupPaths[Setup File Paths<br/>APP_FOLDER, LOG_FOLDER, etc.]
    SetupPaths --> SetupLogging[Configure Logging<br/>File + Console Handlers]
    SetupLogging --> InitVLC[Initialize VLC Media Player<br/>Instance, Player, MediaList]
    InitVLC --> SetupVLC[Setup VLC Event Handlers<br/>on_next_item callback]
    SetupVLC --> InitTheme[Initialize Theme System<br/>Load themes folder]
    InitTheme --> LoadFiles[Load Configuration Files<br/>config.json, banned lists, etc.]
    LoadFiles --> InitSettings[Initialize Settings Class<br/>Set path and load]
    InitSettings --> ShowConfig[Show Configuration Menu]
    
    ShowConfig --> WaitConfig{User Saves<br/>Configuration?}
    WaitConfig -->|No| ShowConfig
    WaitConfig -->|Yes| LoadConfig[Load Configuration<br/>from file]
    
    LoadConfig --> ValidateID[Validate YouTube<br/>Video ID]
    ValidateID --> InitChat[Initialize Chat Connection<br/>pytchat.create]
    
    InitChat --> ChatSuccess{Chat<br/>Initialized?}
    ChatSuccess -->|No| ShowError[Show Config Menu<br/>with Invalid ID Error]
    ShowError --> WaitConfig
    
    ChatSuccess -->|Yes| CheckLive[Check if Video<br/>is Live Stream]
    CheckLive --> IsLive{Is<br/>Live?}
    IsLive -->|No| ShowNotLive[Show Config Menu<br/>with Not Live Error]
    ShowNotLive --> WaitConfig
    
    IsLive -->|Yes| FinalLoad[Load Final Configuration]
    FinalLoad --> StartThreads[Start Background Threads]
    
    StartThreads --> Thread1[Thread: Check Updates]
    StartThreads --> Thread2[Thread: Enable Update Menu]
    StartThreads --> Thread3[Thread: Build GUI]
    StartThreads --> Thread4[Thread: VLC Loop]
    StartThreads --> Thread5[Thread: Poll Chat]
    StartThreads --> Thread6[Thread: Update Slider]
    StartThreads --> Thread7[Thread: Update Now Playing]
    StartThreads --> Thread8[Thread: Start Theme Watcher]
    
    Thread1 --> MainLoop[Main Application Loop]
    Thread2 --> MainLoop
    Thread3 --> MainLoop
    Thread4 --> MainLoop
    Thread5 --> MainLoop
    Thread6 --> MainLoop
    Thread7 --> MainLoop
    Thread8 --> MainLoop
    
    MainLoop --> CheckExit{should_exit<br/>flag set?}
    CheckExit -->|No| Sleep[Sleep 1 second]
    Sleep --> MainLoop
    CheckExit -->|Yes| Cleanup[Cleanup Resources]
    Cleanup --> StopVLC[Stop VLC Player<br/>Release Resources]
    StopVLC --> StopWatcher[Stop Theme File Watcher]
    StopWatcher --> CloseGUI[Close GUI]
    CloseGUI --> End([Application End])
```

## Chat Message Processing Flow

```mermaid
flowchart TD
    Start([Poll Chat Thread]) --> CheckExit{should_exit?}
    CheckExit -->|Yes| End([End Thread])
    CheckExit -->|No| CheckAlive{Chat<br/>is_alive?}
    CheckAlive -->|No| Sleep1[Sleep 1 second]
    Sleep1 --> CheckExit
    
    CheckAlive -->|Yes| GetMessages["Get Chat Messages<br/>chat.get sync_items"]
    GetMessages --> HasMessages{Has<br/>Messages?}
    HasMessages -->|No| Sleep1
    HasMessages -->|Yes| ProcessMsg[Process Each Message<br/>on_chat_message]
    
    ProcessMsg --> CheckPrefix{Message starts<br/>with PREFIX + QUEUE_COMMAND?}
    CheckPrefix -->|No| Sleep1
    CheckPrefix -->|Yes| ParseCmd[Parse Command<br/>Extract video_id]
    
    ParseCmd --> ExtractInfo[Extract User Info<br/>username, channelId,<br/>isMember, isSuperchat]
    ExtractInfo --> CheckRateLimit{User within<br/>rate limit?}
    CheckRateLimit -->|Yes| Sleep1
    CheckRateLimit -->|No| CheckBannedVideo{Video ID<br/>in BANNED_IDS?}
    
    CheckBannedVideo -->|Yes| LogBlocked1[Log: Blocked banned video]
    LogBlocked1 --> CheckAutoBan{AUTOBAN_USERS<br/>enabled?}
    CheckAutoBan -->|Yes| BanUser[Auto-ban User<br/>Add to BANNED_USERS]
    BanUser --> SaveBanned[Save BANNED_USERS<br/>to file]
    SaveBanned --> Sleep1
    CheckAutoBan -->|No| Sleep1
    
    CheckBannedVideo -->|No| CheckBannedUser{User ID<br/>in BANNED_USERS?}
    CheckBannedUser -->|Yes| LogBlocked2[Log: Blocked banned user]
    LogBlocked2 --> Sleep1
    
    CheckBannedUser -->|No| CheckUserWhitelist{ENFORCE_USER_WHITELIST<br/>enabled?}
    CheckUserWhitelist -->|Yes| CheckInWhitelist{User in<br/>WHITELISTED_USERS?}
    CheckInWhitelist -->|No| LogBlocked3[Log: User not whitelisted]
    LogBlocked3 --> Sleep1
    CheckInWhitelist -->|Yes| CheckVideoWhitelist
    CheckUserWhitelist -->|No| CheckVideoWhitelist
    
    CheckVideoWhitelist{ENFORCE_ID_WHITELIST<br/>enabled?} -->|Yes| CheckVideoInWhitelist{Video in<br/>WHITELISTED_IDS?}
    CheckVideoInWhitelist -->|No| LogBlocked4[Log: Video not whitelisted]
    LogBlocked4 --> Sleep1
    CheckVideoInWhitelist -->|Yes| CheckURL
    CheckVideoWhitelist -->|No| CheckURL
    
    CheckURL{Video ID contains<br/>watch?v=?} -->|Yes| CheckAllowURLs{ALLOW_URLS<br/>enabled?}
    CheckAllowURLs -->|No| LogBlocked5[Log: URLs not allowed]
    LogBlocked5 --> Sleep1
    CheckAllowURLs -->|Yes| ExtractID[Extract video_id<br/>from URL]
    ExtractID --> CheckMembership
    CheckURL -->|No| CheckMembership
    
    CheckMembership{REQUIRE_MEMBERSHIP<br/>enabled?} -->|Yes| IsMember{User is<br/>member?}
    IsMember -->|No| LogBlocked6[Log: Membership required]
    LogBlocked6 --> Sleep1
    IsMember -->|Yes| CheckSuperchat
    CheckMembership -->|No| CheckSuperchat
    
    CheckSuperchat{REQUIRE_SUPERCHAT<br/>enabled?} -->|Yes| IsSuperchat{Message is<br/>superchat?}
    IsSuperchat -->|No| LogBlocked7[Log: Superchat required]
    LogBlocked7 --> Sleep1
    IsSuperchat -->|Yes| CheckMinValue{Superchat value<br/>>= MINIMUM_SUPERCHAT?}
    CheckMinValue -->|No| LogBlocked8[Log: Superchat too low]
    LogBlocked8 --> Sleep1
    CheckMinValue -->|Yes| CheckYouTubeMusic
    CheckSuperchat -->|No| CheckYouTubeMusic
    
    CheckYouTubeMusic{Video on<br/>YouTube Music?} -->|No| LogBlocked9[Log: Not on YouTube Music]
    LogBlocked9 --> Sleep1
    CheckYouTubeMusic -->|Yes| QueueSong[Queue Song<br/>queue_song function]
    
    QueueSong --> UpdateRateLimit[Update user_last_command<br/>timestamp]
    UpdateRateLimit --> UpdateNowPlaying[Update Now Playing<br/>Display]
    UpdateNowPlaying --> Sleep1
```

## Song Queue Flow

```mermaid
flowchart TD
    Start([queue_song called]) --> BuildURL[Build YouTube Music URL<br/>music.youtube.com/watch?v=]
    BuildURL --> GetDirectURL[Get Direct Audio Stream URL<br/>get_direct_url]
    GetDirectURL --> CreateMedia[Create VLC Media Object<br/>instance.media_new]
    CreateMedia --> GetTitle[Get Video Title<br/>get_video_title]
    GetTitle --> SetMeta[Set Media Metadata<br/>media.set_meta Title]
    SetMeta --> AddToPlaylist[Add Media to Playlist<br/>media_list.add_media]
    
    AddToPlaylist --> AddHistory[Add to QUEUE_HISTORY<br/>user_id, username, song_id, song_title]
    AddHistory --> LogQueue[Log: Song Queued]
    LogQueue --> CheckState{Player<br/>State?}
    
    CheckState -->|Stopped/Ended/NothingSpecial| StartPlayback[Start Playback<br/>player.play]
    CheckState -->|Playing/Paused| ShowToast
    
    StartPlayback --> ShowToast[Show Toast Notification<br/>if TOAST_NOTIFICATIONS enabled]
    ShowToast --> RefreshHistory{Queue History<br/>Window exists?}
    RefreshHistory -->|Yes| RefreshList[Refresh Queue History List<br/>refresh_queue_history_list]
    RefreshHistory -->|No| End
    RefreshList --> End([End])
```

## VLC Playback Flow

```mermaid
flowchart TD
    Start([VLC Loop Thread]) --> CheckExit{should_exit?}
    CheckExit -->|Yes| End([End Thread])
    CheckExit -->|No| CheckState{Player State<br/>== Ended?}
    
    CheckState -->|No| Sleep1[Sleep 1 second]
    Sleep1 --> CheckExit
    CheckState -->|Yes| CheckQueue{media_list.count<br/>> 0?}
    
    CheckQueue -->|No| Sleep1
    CheckQueue -->|Yes| RestartPlay[Restart Playback<br/>player.play]
    RestartPlay --> Sleep1
```

## VLC Event Handler Flow

```mermaid
flowchart TD
    Start([on_next_item Event]) --> CheckSkip{user_initiated_skip<br/>flag?}
    CheckSkip -->|Yes| IsNatural[is_natural_completion = False]
    CheckSkip -->|No| IsNatural[is_natural_completion = True]
    
    IsNatural --> ResetFlag[Reset user_initiated_skip<br/>flag to False]
    ResetFlag --> CheckNotifications{SONG_FINISH_NOTIFICATIONS<br/>enabled AND<br/>is_natural_completion?}
    
    CheckNotifications -->|Yes| GetNewSong[Get New Song Title<br/>from media metadata]
    GetNewSong --> ShowNotification[Show Desktop Notification<br/>Now Playing: Song Title]
    ShowNotification --> CheckAutoRemove
    CheckNotifications -->|No| CheckAutoRemove
    
    CheckAutoRemove{AUTOREMOVE_SONGS<br/>enabled?} -->|No| End([End])
    CheckAutoRemove -->|Yes| LockList[Lock Media List<br/>media_list.lock]
    LockList --> CheckCount{media_list.count<br/>> 1?}
    
    CheckCount -->|Yes| RemoveFirst[Remove First Item<br/>media_list.remove_index 0]
    RemoveFirst --> UnlockList[Unlock Media List<br/>media_list.unlock]
    UnlockList --> LogRemove[Log: Removed finished song]
    LogRemove --> CheckEmpty{media_list.count<br/>== 0?}
    
    CheckEmpty -->|Yes| StopPlayer[Stop Player<br/>player.stop]
    StopPlayer --> LogEmpty[Log: Queue empty]
    LogEmpty --> End
    CheckEmpty -->|No| End
    CheckCount -->|No| UnlockList
```

## GUI Update Threads Flow

```mermaid
flowchart TD
    Start1([Update Slider Thread]) --> WaitGUI1{Slider exists?}
    WaitGUI1 -->|No| Sleep1[Sleep 0.1 seconds]
    Sleep1 --> WaitGUI1
    WaitGUI1 -->|Yes| CheckExit1{should_exit?}
    CheckExit1 -->|Yes| End1([End Thread])
    CheckExit1 -->|No| GetTime[Get Current Time<br/>get_curr_songtime]
    GetTime --> GetLength[Get Song Length<br/>get_song_length]
    GetLength --> ValidTime{Time and Length<br/>valid?}
    
    ValidTime -->|No| Sleep1
    ValidTime -->|Yes| CheckUserSeek{User seeked<br/>recently?}
    CheckUserSeek -->|Yes| UpdateTimeText[Update Time Text<br/>MM:SS / MM:SS]
    UpdateTimeText --> Sleep1
    CheckUserSeek -->|No| CalculateProgress[Calculate Progress<br/>curr / total]
    CalculateProgress --> SetSlider[Set Slider Value<br/>ignore callback flag]
    SetSlider --> UpdateTimeText
    
    Start2([Update Now Playing Thread]) --> CheckExit2{should_exit?}
    CheckExit2 -->|Yes| End2([End Thread])
    CheckExit2 -->|No| CallUpdate[Call update_now_playing]
    CallUpdate --> Sleep2[Sleep 1 second]
    Sleep2 --> CheckExit2
    
    Start3([Theme Watcher Thread]) --> WaitGUI2{MainWindow<br/>exists?}
    WaitGUI2 -->|No| Sleep3[Sleep 0.1 seconds]
    Sleep3 --> WaitGUI2
    WaitGUI2 -->|Yes| StartWatcher[Start Theme File Watcher<br/>start_theme_file_watcher]
    StartWatcher --> End3([End Thread])
```

## Configuration Menu Flow

```mermaid
flowchart TD
    Start([show_config_menu]) --> CreateContext[Create DearPyGUI Context]
    CreateContext --> LoadThemes[Load Themes<br/>create_default_theme_files<br/>load_all_themes]
    LoadThemes --> CreateWindow[Create Config Window<br/>with all settings inputs]
    
    CreateWindow --> SetupInputs[Setup Input Fields<br/>Video ID, Prefix, Command,<br/>Rate Limit, Checkboxes, etc.]
    SetupInputs --> SetupTheme[Setup Theme Dropdown<br/>get_theme_dropdown_items]
    SetupTheme --> SetupButtons[Setup Buttons<br/>Save and Start, Quit]
    SetupButtons --> SetupCallbacks[Setup Save Callback<br/>save_and_start_callback]
    
    SetupCallbacks --> ShowWindow[Show Viewport<br/>start_dearpygui]
    ShowWindow --> WaitUser{User Action}
    
    WaitUser -->|Save and Start| SaveCallback[Save Callback Executed]
    WaitUser -->|Quit| QuitCallback[Quit Program<br/>quit_program]
    QuitCallback --> End([End])
    
    SaveCallback --> UpdateSettings[Update Settings from GUI<br/>Settings.YOUTUBE_VIDEO_ID = input<br/>Settings.PREFIX = input<br/>etc.]
    UpdateSettings --> GetTheme[Get Selected Theme<br/>from dropdown]
    GetTheme --> SetTheme[Set Theme<br/>set_current_theme]
    SetTheme --> SaveSettings[Save Settings<br/>Settings.save]
    SaveSettings --> ApplyTheme[Apply Theme<br/>apply_theme]
    ApplyTheme --> StopGUI[Stop DearPyGUI<br/>stop_dearpygui]
    StopGUI --> DestroyContext[Destroy Context<br/>destroy_context]
    DestroyContext --> Return([Return to Main Flow])
```

## Settings Save Flow

```mermaid
flowchart TD
    Start([Settings.save called]) --> CheckPath{Settings path<br/>set?}
    CheckPath -->|No| RaiseError[Raise ValueError<br/>Path not set]
    CheckPath -->|Yes| AcquireLock[Acquire Thread Lock<br/>_lock]
    
    AcquireLock --> OpenFile[Open config.json<br/>for writing UTF-8]
    OpenFile --> BuildDict[Build Settings Dictionary<br/>All fields with conversions]
    BuildDict --> WriteJSON[Write JSON to File<br/>json.dump with indent=4]
    WriteJSON --> ReleaseLock[Release Thread Lock]
    ReleaseLock --> End([End])
```

## Theme File Watcher Flow

```mermaid
flowchart TD
    Start([Theme File Changed]) --> CheckType{Event Type<br/>created/modified/deleted?}
    CheckType -->|No| End([End])
    CheckType -->|Yes| CheckFile{File is<br/>JSON?}
    CheckFile -->|No| End
    CheckFile -->|Yes| CheckDebounce{Time since<br/>last reload > 0.5s?}
    
    CheckDebounce -->|No| End
    CheckDebounce -->|Yes| UpdateTimestamp[Update last_reload_time]
    UpdateTimestamp --> LogChange[Log: Theme file change detected]
    LogChange --> ReloadThemes[Reload Themes<br/>unload_all_themes<br/>load_all_themes]
    
    ReloadThemes --> ApplyCurrent[Apply Current Theme<br/>apply_theme get_current_theme]
    ApplyCurrent --> RebuildMenu[Rebuild Theme Menu<br/>rebuild_theme_menu_items]
    RebuildMenu --> LogSuccess[Log: Themes reloaded automatically]
    LogSuccess --> End
```

## Update Check Flow

```mermaid
flowchart TD
    Start([check_for_updates_wrapper]) --> FetchVersion[Fetch Latest Version<br/>fetch_latest_version]
    FetchVersion --> HasVersion{Latest version<br/>found?}
    HasVersion -->|No| End([End])
    HasVersion -->|Yes| CompareVersions[Compare Versions<br/>compare_versions current vs latest]
    
    CompareVersions --> CheckIgnored{Latest > Current<br/>AND<br/>Latest > Ignored?}
    CheckIgnored -->|No| LogUpToDate[Log: Up to date]
    LogUpToDate --> End
    CheckIgnored -->|Yes| SetUpdateState[Set UPDATE_AVAILABLE = True<br/>LATEST_VERSION = latest]
    SetUpdateState --> FetchDetails[Fetch Release Details<br/>fetch_latest_release_details]
    FetchDetails --> SetDetails[Set LATEST_RELEASE_DETAILS]
    SetDetails --> LogUpdate[Log: Update available]
    LogUpdate --> CheckToast{TOAST_NOTIFICATIONS<br/>enabled?}
    
    CheckToast -->|Yes| ShowToast[Show Desktop Notification<br/>Update Available]
    CheckToast -->|No| CheckGUI
    ShowToast --> CheckGUI{MainWindow<br/>exists?}
    
    CheckGUI -->|Yes| ShowUI[Show Download UI<br/>show_download_ui]
    CheckGUI -->|No| End
    ShowUI --> EnableMenu[Enable Update Details Menu<br/>configure_item enabled=True]
    EnableMenu --> End
```

## Ban/Unban Flow

```mermaid
flowchart TD
    Start([Ban User Callback]) --> GetInput[Get Input Value<br/>get_value ban_user_input]
    GetInput --> StripInput[Strip Whitespace]
    StripInput --> CheckEmpty{Input<br/>empty?}
    CheckEmpty -->|Yes| End([End])
    CheckEmpty -->|No| CheckExists{User already<br/>in list?}
    
    CheckExists -->|Yes| End
    CheckExists -->|No| AddPlaceholder[Add with Placeholder Name<br/>id: input, name: Loading...]
    AddPlaceholder --> SaveList[Save List to File<br/>save_banned_users]
    SaveList --> RefreshGUI[Refresh GUI List<br/>refresh_banned_users_list]
    RefreshGUI --> ClearInput[Clear Input Field<br/>set_value empty]
    ClearInput --> StartThread[Start Background Thread<br/>fetch_and_update]
    
    StartThread --> FetchName[Fetch Channel Name<br/>fetch_channel_name]
    FetchName --> UpdateEntry[Update Entry in List<br/>Replace Loading... with real name]
    UpdateEntry --> SaveList2[Save Updated List<br/>save_banned_users]
    SaveList2 --> RefreshGUI2[Refresh GUI List<br/>refresh_banned_users_list]
    RefreshGUI2 --> EndThread([End Thread])
```

## GUI Build Flow

```mermaid
flowchart TD
    Start([build_gui]) --> CreateContext[Create DearPyGUI Context]
    CreateContext --> CreateMainWindow[Create Main Window<br/>LYTE Control Panel]
    CreateMainWindow --> SetPrimary[Set Primary Window]
    SetPrimary --> CreateMenuBar[Create Menu Bar<br/>File, View, Moderation, Help]
    
    CreateMenuBar --> CreateFileMenu[File Menu<br/>Reload Config, Settings, Quit]
    CreateMenuBar --> CreateViewMenu[View Menu<br/>Theme submenu, Open Themes Folder, Reload Themes]
    CreateMenuBar --> CreateModMenu[Moderation Menu<br/>Queue History, Banned Users/Videos,<br/>Whitelisted Users/Videos]
    CreateMenuBar --> CreateHelpMenu[Help Menu<br/>Version, Check Updates,<br/>GitHub Issues, Documentation]
    
    CreateHelpMenu --> CreateNowPlaying[Create Now Playing Display<br/>add_text]
    CreateNowPlaying --> CreateControls[Create Playback Controls<br/>Play/Pause, Previous, Next, Refresh]
    CreateControls --> CreateVolume[Create Volume Slider<br/>add_slider_float]
    CreateVolume --> CreateProgress[Create Song Progress Slider<br/>add_slider_float + time display]
    CreateProgress --> CreateConsole[Create Console Output<br/>add_input_text multiline readonly]
    
    CreateConsole --> SetupLogger[Setup GUI Logger<br/>GuiLogger class]
    SetupLogger --> CreateSettingsWindow[Create Settings Window<br/>All config inputs]
    CreateSettingsWindow --> CreateBanWindows[Create Ban/Whitelist Windows<br/>BannedUsersWindow, BannedIDsWindow, etc.]
    CreateBanWindows --> CreateQueueWindow[Create Queue History Window]
    CreateQueueWindow --> CreateUpdateWindow[Create Update Details Window]
    
    CreateUpdateWindow --> CreateThemes[Create Default Theme Files<br/>create_default_theme_files]
    CreateThemes --> LoadThemes[Load All Themes<br/>load_all_themes]
    LoadThemes --> CheckTheme{Current theme<br/>exists?}
    
    CheckTheme -->|No| SetDefault[Set Default Theme<br/>dark_theme or first available]
    CheckTheme -->|Yes| CreateViewport[Create Viewport<br/>create_viewport]
    SetDefault --> CreateViewport
    
    CreateViewport --> ApplyTheme[Apply Current Theme<br/>apply_theme]
    ApplyTheme --> SetupGUI[Setup DearPyGUI<br/>setup_dearpygui]
    SetupGUI --> ShowViewport[Show Viewport<br/>show_viewport]
    ShowViewport --> SetExitCallback[Set Exit Callback<br/>on_close_attempt]
    SetExitCallback --> StartGUI[Start DearPyGUI<br/>start_dearpygui]
    StartGUI --> End([GUI Running])
```

---

## Legend

- **Rectangles**: Process/Function
- **Diamonds**: Decision/Condition
- **Ovals**: Start/End points
- **Parallelograms**: Input/Output
- **Arrows**: Flow direction

## Thread Overview

The application runs multiple background threads:

1. **Check Updates Thread**: Periodically checks for updates
2. **Enable Update Menu Thread**: Enables update menu when update available
3. **Build GUI Thread**: Builds and displays the GUI
4. **VLC Loop Thread**: Monitors VLC player state
5. **Poll Chat Thread**: Continuously polls YouTube chat for messages
6. **Update Slider Thread**: Updates song progress slider in real-time
7. **Update Now Playing Thread**: Updates "Now Playing" display periodically
8. **Theme Watcher Thread**: Starts theme file watcher after GUI ready

All threads run as daemon threads and check the `should_exit` flag for graceful shutdown.

