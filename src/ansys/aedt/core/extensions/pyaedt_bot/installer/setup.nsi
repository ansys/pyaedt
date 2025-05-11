; NSIS script for Template Toolkit installer

; Set the name, version, and output path of the installer
!define LICENSE_FILE "LICENSE"
!define PRODUCT_NAME "Template Toolkit"
!define /file PRODUCT_VERSION "installer\VERSION"
!define OUTFILE_NAME "Template-Toolkit-Installer-windows.exe"

Name "${PRODUCT_NAME}"
OutFile "dist\${OUTFILE_NAME}"
VIProductVersion "${PRODUCT_VERSION}"

; Multi-user & UI
!define MULTIUSER_EXECUTIONLEVEL Highest
!define MULTIUSER_MUI
!define MULTIUSER_INSTALLMODE_COMMANDLINE
!include MultiUser.nsh
!include MUI2.nsh
!include InstallOptions.nsh

!define MUI_PAGE_CUSTOMFUNCTION_PRE oneclickpre
!insertmacro MULTIUSER_PAGE_INSTALLMODE
!insertmacro MUI_PAGE_LICENSE "${LICENSE_FILE}"
!insertmacro MUI_PAGE_INSTFILES
!include "uninstall.nsi"

Function CreateDesktopShortCut
  CreateShortCut "$desktop\${PRODUCT_NAME}.lnk" "$INSTDIR\Template Toolkit.exe"
FunctionEnd

!define MUI_FINISHPAGE_RUN "$INSTDIR\Template Toolkit.exe"
!define MUI_FINISHPAGE_SHOWREADME
!define MUI_FINISHPAGE_SHOWREADME_TEXT "Create Desktop Shortcut"
!define MUI_FINISHPAGE_SHOWREADME_FUNCTION "CreateDesktopShortCut"
!insertmacro MUI_PAGE_FINISH

Function .onInit
  !insertmacro MULTIUSER_INIT
FunctionEnd

Function un.onInit
  !insertmacro MULTIUSER_UNINIT
FunctionEnd


; Define the installer sections
Section "${PRODUCT_NAME}" SEC01
  ; Set the installation directory to the program files directory
  SetOutPath "$PROGRAMFILES64\ANSYS Inc\${PRODUCT_NAME}"

  ; Copy the files from the dist\template_toolkit directory
  ; File /r /oname=ignore "dist\template_toolkit\*"
  File /r "dist\template_toolkit\*"

  ; Create the start menu directory
  CreateDirectory "$SMPROGRAMS\${PRODUCT_NAME}"

  ; Create the start menu shortcut
  CreateShortCut "$SMPROGRAMS\${PRODUCT_NAME}\${PRODUCT_NAME}.lnk" "$INSTDIR\${PRODUCT_NAME}.exe"

  ; Add the program to the installed programs list
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}" "DisplayName" "${PRODUCT_NAME}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}" "UninstallString" "$\"$INSTDIR\uninstall.exe$\""
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}" "DisplayIcon" "$\"$INSTDIR\Ansys Python Manager.exe$\""
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}" "Publisher" "ANSYS Inc"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}" "Version" "${PRODUCT_VERSION}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}" "DisplayVersion" "${PRODUCT_VERSION}"

  WriteUninstaller "$INSTDIR\uninstall.exe"

SectionEnd

; Define the uninstaller section
Section "Uninstall" SEC02

  Delete "$PROGRAMFILES64\${PRODUCT_NAME}\*.*"
  RMDir "$PROGRAMFILES64\${PRODUCT_NAME}"
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}"
  Delete "$SMPROGRAMS\${PRODUCT_NAME}\${PRODUCT_NAME}.lnk"
  RMDir "$SMPROGRAMS\${PRODUCT_NAME}"
  Delete "$desktop\${PRODUCT_NAME}.lnk"
SectionEnd

Icon "dist\template_toolkit\_internal\assets\splash_icon.ico"
InstallDir "$PROGRAMFILES64\ANSYS Inc\${PRODUCT_NAME}"

; Define the custom functions for the MUI2 OneClick plugin
InstProgressFlags smooth
Function oneclickpre
  !insertmacro MUI_HEADER_TEXT "Installing ${PRODUCT_NAME}" "Please wait while the installation completes."
  ; !define MUI_UNICON "${NSISDIR}\Contrib\Graphics\Icons\modern-uninstall.ico"
  HideWindow
FunctionEnd

; Call the MUI2 OneClick plugin
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_LANGUAGE English
