Var DeleteUserData
Var DeleteLogs

Section "Uninstall"
  MessageBox MB_YESNO|MB_ICONQUESTION "Do you want to uninstall ${PRODUCT_NAME} ${PRODUCT_VERSION}?" IDYES checkDeleteUserData
  Abort

checkDeleteUserData:
  MessageBox MB_YESNO|MB_ICONQUESTION "Delete application user data?" IDYES deleteUserData
  StrCpy $DeleteUserData 0
  Goto checkDeleteLogs

deleteUserData:
  StrCpy $DeleteUserData 1

checkDeleteLogs:
  MessageBox MB_YESNO|MB_ICONQUESTION "Delete logs?" IDYES deleteLogs
  StrCpy $DeleteLogs 0
  Goto doneAsking

deleteLogs:
  StrCpy $DeleteLogs 1

doneAsking:

  ${If} $DeleteUserData == 1
      RMDir /r "$PROFILE\.${PRODUCT_NAME}"
  ${EndIf}

  ${If} $DeleteLogs == 1
      RMDir /r "$PROFILE\.${PRODUCT_NAME}_logs"
  ${EndIf}

  Delete "$INSTDIR\*.*"
  RMDir /r "$INSTDIR"
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}"
  Delete "$SMPROGRAMS\${PRODUCT_NAME}\${PRODUCT_NAME}.lnk"
  RMDir "$SMPROGRAMS\${PRODUCT_NAME}"
  Delete "$desktop\${PRODUCT_NAME}.lnk"

  MessageBox MB_OK|MB_ICONINFORMATION "${PRODUCT_NAME} has been uninstalled."
SectionEnd