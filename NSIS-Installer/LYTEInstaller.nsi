!include "MUI2.nsh"
!include "FileFunc.nsh"
!include "LogicLib.nsh"
!include "nsDialogs.nsh"


Name "LYTE"
OutFile "LYTE_Installer.exe"
InstallDir "$APPDATA\LYTE"
InstallDirRegKey HKLM "Software\LYTE" "Install_Dir"
RequestExecutionLevel admin

;--------------------------------
; Variables for config options
;--------------------------------
Var AddStartMenu
Var AddDesktop
Var LaunchAfterInstall
Var InstallPython
Var InstallVLC
Var InstallVCRedist
Var ExtrasPageDialog
Var PythonCheckbox
Var VLCCheckbox
Var VCRedistCheckbox
Var DialogInstallPathCtrl ; global variable for install path edit control handle
Var BROWSEDEST

;--------------------------------
; Pages
;--------------------------------
!insertmacro MUI_PAGE_LICENSE "license.txt"
Page custom ConfigPageCreate ConfigPageLeave
Page custom ExtrasPageCreate ExtrasPageLeave
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

;--------------------------------
; Languages
;--------------------------------
!insertmacro MUI_LANGUAGE "English"

;--------------------------------
; Config Page Functions
;--------------------------------

Function Browsedest
nsDialogs::SelectFolderDialog "Select Destination Folder" "C:\"
Pop $INSTDIR
${NSD_SetText} $DialogInstallPathCtrl $INSTDIR
FunctionEnd

Function ConfigPageCreate
  StrCpy $INSTDIR "$APPDATA\LYTE"
  nsDialogs::Create 1018
  Pop $0
  ${If} $0 == error
    Abort
  ${EndIf}

  ; Install folder label
  ${NSD_CreateLabel} 0 10 100% 12 "Choose Install Location:"
  Pop $1

  ; Install path input box
  ${NSD_CreateText} 0 25 80% 18 "$INSTDIR"
  Pop $DialogInstallPathCtrl
  
  ; Browse button
  ${NSD_CreateBrowseButton} 85% 25 60 18 "Browse"
  Pop $BROWSEDEST

  ; Start Menu checkbox
  ${NSD_CreateCheckBox} 0 50 100% 12 "Add Start Menu shortcut"
  Pop $4
  ${NSD_SetState} $4 ${BST_CHECKED}

  ; Desktop checkbox
  ${NSD_CreateCheckBox} 0 70 100% 12 "Add Desktop shortcut"
  Pop $5
  ${NSD_SetState} $5 ${BST_CHECKED}

  ; Launch after install checkbox
  ${NSD_CreateCheckBox} 0 90 100% 12 "Launch LYTE after installation"
  Pop $6
  ${NSD_SetState} $6 ${BST_CHECKED}

  ${NSD_OnClick} $BROWSEDEST Browsedest

  nsDialogs::Show
FunctionEnd

Function ConfigPageLeave
  ; Get install path
  ${NSD_GetText} $DialogInstallPathCtrl $INSTDIR  ; Get checkboxes state
  ${NSD_GetState} $4 $AddStartMenu
  ${NSD_GetState} $5 $AddDesktop
  ${NSD_GetState} $6 $LaunchAfterInstall
FunctionEnd

Function ExtrasPageCreate
  nsDialogs::Create 1018
  Pop $ExtrasPageDialog
  ${If} $ExtrasPageDialog == error
    Abort
  ${EndIf}

  ; Create checkboxes for each extra
  ${NSD_CreateLabel} 0 10 100% 12 "Stop certain dependencies from installing:"
  Pop $0

  ${NSD_CreateCheckBox} 0 30 100% 12 "Install Python"
  Pop $PythonCheckbox
  ${NSD_SetState} $PythonCheckbox ${BST_CHECKED}

  ${NSD_CreateCheckBox} 0 50 100% 12 "Install VLC"
  Pop $VLCCheckbox
  ${NSD_SetState} $VLCCheckbox ${BST_CHECKED}

  ${NSD_CreateCheckBox} 0 70 100% 12 "Install Microsoft Visual C++ Redistributable"
  Pop $VCRedistCheckbox
  ${NSD_SetState} $VCRedistCheckbox ${BST_CHECKED}

  nsDialogs::Show
FunctionEnd

Function ExtrasPageLeave
  ${NSD_GetState} $PythonCheckbox $InstallPython
  ${NSD_GetState} $VLCCheckbox $InstallVLC
  ${NSD_GetState} $VCRedistCheckbox $InstallVCRedist
FunctionEnd

;--------------------------------
; Install Sections
;--------------------------------

Section "Install VC++ Redistributable"
  ${If} $InstallVCRedist == ${BST_CHECKED}
      DetailPrint "Downloading Microsoft Visual C++ Redistributable..."
      SetOutPath "$PLUGINSDIR"
      inetc::get /popup "" "https://aka.ms/vs/17/release/vc_redist.x64.exe" "$PLUGINSDIR\vc_redist.x64.exe" /end
      Pop $0
      ${If} $0 != "OK"
          MessageBox MB_ICONSTOP "Failed to download VC++ Redistributable."
          Abort
      ${EndIf}

      DetailPrint "Installing Microsoft Visual C++ Redistributable..."
      ExecWait '"$PLUGINSDIR\vc_redist.x64.exe" /install /quiet /norestart' $0
      ${If} $0 != 0
          MessageBox MB_ICONSTOP "VC++ Redistributable installation failed with exit code: $0"
          Abort
      ${EndIf}
    ${EndIf}
SectionEnd

Section "Download & Install Python"
  ${If} $InstallPython == ${BST_CHECKED}
    DetailPrint "Downloading Python installer..."
    SetOutPath "$PLUGINSDIR"
    inetc::get /popup "" "https://www.python.org/ftp/python/3.13.6/python-3.13.6-amd64.exe" "$PLUGINSDIR\python-3.13.6-amd64.exe" /end
    Pop $0
    ${If} $0 != "OK"
        MessageBox MB_ICONSTOP "Failed to download Python installer."
        Abort
    ${EndIf}

    DetailPrint "Installing Python..."
    ExecWait '"$PLUGINSDIR\python-3.13.6-amd64.exe" /quiet InstallAllUsers=1 PrependPath=1 Include_test=0 Include_doc=0 Include_tcltk=0' $0
    ${If} $0 != 0
        MessageBox MB_ICONSTOP "Python installation failed with exit code: $0"
        Abort
    ${EndIf}

    ; Give it a moment to finish
      Sleep 2000

      DetailPrint "Installing DearPyGui via pip..."
      ; Open cmd.exe and run the pip command
      nsExec::ExecToLog 'cmd /c "pip install dearpygui"'
      
    DetailPrint "Python installation completed successfully"
  ${EndIf}
SectionEnd

Section "Download & Install VLC"
  ${If} $InstallVLC == ${BST_CHECKED}
    DetailPrint "Downloading VLC installer..."
    SetOutPath "$PLUGINSDIR"
    inetc::get /popup "" "https://mirror.aarnet.edu.au/pub/videolan/vlc/3.0.21/win64/vlc-3.0.21-win64.exe" "$PLUGINSDIR\vlc-3.0.21-win32.exe" /end
    Pop $0
    ${If} $0 != "OK"
        MessageBox MB_ICONSTOP "Failed to download VLC installer."
        Abort
    ${EndIf}

    DetailPrint "Installing VLC..."
    ExecWait '"$PLUGINSDIR\vlc-3.0.21-win32.exe" /S' $0
    ${If} $0 != 0
        MessageBox MB_ICONSTOP "VLC installation failed with exit code: $0"
        Abort
    ${EndIf}

    DetailPrint "VLC installation completed successfully"
  ${EndIf}
SectionEnd

Section "Install LYTE"
  SetOutPath "$INSTDIR"

  ; Example: downloading LYTE.exe with InetC (adjust as needed)
  DetailPrint "Downloading LYTE..."
  inetc::get /popup "" "https://github.com/StroepWafel/LYTE/releases/latest/download/LYTE.exe" "$INSTDIR\LYTE.exe" /end
  Pop $0
  ${If} $0 != "OK"
    MessageBox MB_ICONSTOP "Failed to download LYTE."
    Abort
  ${EndIf}

  ; Create shortcuts if selected
  ${If} $AddStartMenu == ${BST_CHECKED}
    CreateDirectory "$SMPROGRAMS\LYTE"
    CreateShortcut "$SMPROGRAMS\LYTE\LYTE.lnk" "$INSTDIR\LYTE.exe"
  ${EndIf}

  ${If} $AddDesktop == ${BST_CHECKED}
    CreateShortcut "$DESKTOP\LYTE.lnk" "$INSTDIR\LYTE.exe"
  ${EndIf}

  ; Write uninstall info
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\LYTE" "DisplayName" "LYTE"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\LYTE" "UninstallString" "$INSTDIR\uninstall.exe"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\LYTE" "InstallLocation" "$INSTDIR"

  ; Write uninstaller
  WriteUninstaller "$INSTDIR\uninstall.exe"
SectionEnd

;--------------------------------
; Finish Page Run Program
;--------------------------------

Function .onInstSuccess
  ${If} $LaunchAfterInstall == ${BST_CHECKED}
    ExecShell "" "$INSTDIR\LYTE.exe"
  ${EndIf}
FunctionEnd

;--------------------------------
; Uninstaller Section
;--------------------------------
Section "Uninstall" Uninstall
  Delete "$INSTDIR\LYTE.exe"
  Delete "$INSTDIR\banned_IDs.json"
  Delete "$INSTDIR\banned_users.json"
  Delete "$INSTDIR\config.json"
  RMDir "$INSTDIR\logs"
  Delete "$INSTDIR\uninstall.exe"
  Delete "$SMPROGRAMS\LYTE\LYTE.lnk"
  RMDir "$SMPROGRAMS\LYTE"
  Delete "$DESKTOP\LYTE.lnk"
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\LYTE"
  DeleteRegKey HKLM "Software\LYTE"
  RMDir "$INSTDIR"
SectionEnd

Function un.onInit
  ReadRegStr $INSTDIR HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\LYTE" "InstallLocation"
FunctionEnd



