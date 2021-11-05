set ANSYSEM_FEATURE_SF6694_NON_GRAPHICAL_COMMAND_EXECUTION_ENABLE=1
set RUN_UNITTESTS_ARGS=%*
"%ANSYSEM_ROOT212%\ansysedt.exe" -ng -RunScriptAndExit "_unittest_ironpython\run_unittests.py"