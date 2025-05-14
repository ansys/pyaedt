; NSIS script for SAM Bot installer

!define PRODUCT_NAME "SAM Bot"
!define OUTFILE_NAME "SAM-Bot-Installer-windows.exe"

; Define relative root paths from this script's location
!define ROOT_DIR "..\..\..\..\..\..\.."
!define DIST_DIR "${ROOT_DIR}\dist\pyaedt_bot"
!define ICON_FILE "${DIST_DIR}\_internal\assets\bot.ico"
!define LICENSE_FILE "${ROOT_DIR}\LICENSE"
!define VERSION_FILE "VERSION"
!define /file PRODUCT_VERSION "${VERSION_FILE}"

Name "${PRODUCT_NAME}"
OutFile "${DIST_DIR}\${OUTFILE_NAME}"
VIProductVersion "${PRODUCT_VERSION}"

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
  CreateShortCut "$desktop\${PRODUCT_NAME}.lnk" "$INSTDIR\${PRODUCT_NAME}.exe"
FunctionEnd

!define MUI_FINISHPAGE_RUN "$INSTDIR\${PRODUCT_NAME}.exe"
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

Section "${PRODUCT_NAME}" SEC01
  SetOutPath "$PROGRAMFILES64\ANSYS Inc\${PRODUCT_NAME}"

  File /r "${DIST_DIR}\*"

  CreateDirectory "$SMPROGRAMS\${PRODUCT_NAME}"
  CreateShortCut "$SMPROGRAMS\${PRODUCT_NAME}\${PRODUCT_NAME}.lnk" "$INSTDIR\${PRODUCT_NAME}.exe"

  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}" "DisplayName" "${PRODUCT_NAME}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}" "UninstallString" "$\"$INSTDIR\uninstall.exe$\""
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}" "DisplayIcon" "$\"$INSTDIR\${PRODUCT_NAME}.exe$\""
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}" "Publisher" "ANSYS Inc"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}" "Version" "${PRODUCT_VERSION}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}" "DisplayVersion" "${PRODUCT_VERSION}"

  WriteUninstaller "$INSTDIR\uninstall.exe"
SectionEnd

Section "Uninstall" SEC02
  Delete "$PROGRAMFILES64\${PRODUCT_NAME}\*.*"
  RMDir "$PROGRAMFILES64\${PRODUCT_NAME}"
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}"
  Delete "$SMPROGRAMS\${PRODUCT_NAME}\${PRODUCT_NAME}.lnk"
  RMDir "$SMPROGRAMS\${PRODUCT_NAME}"
  Delete "$desktop\${PRODUCT_NAME}.lnk"
SectionEnd

Icon "${ICON_FILE}"
InstallDir "$PROGRAMFILES64\ANSYS Inc\${PRODUCT_NAME}"

InstProgressFlags smooth
Function oneclickpre
  !insertmacro MUI_HEADER_TEXT "Installing ${PRODUCT_NAME}" "Please wait while the installation completes."
  HideWindow
FunctionEnd

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_LANGUAGE English
