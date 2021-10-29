set ANSYSEM_FEATURE_SF6694_NON_GRAPHICAL_COMMAND_EXECUTION_ENABLE=1
set RUN_UNITTESTS_ARGS=%*
"%ANSYSEM_ROOT211%\ansysedt.exe" -ng -RunScriptAndExit "_unittest_ironpython\run_unittests.py"

if errorlevel 1 (
   echo Failure Reason Given is %errorlevel%
   exit /b %errorlevel%
)