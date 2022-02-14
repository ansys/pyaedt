@echo off
if  "%ANSYSEM_ROOT221%" =="" (
    if "%ANSYSEM_ROOT212%" =="" (
        if "%ANSYSEM_ROOT211%" =="" (
            echo AEDT 21R1 or greater has to be installed
            pause
            EXIT /B
        ) else (
            set aedt_path=%ANSYSEM_ROOT211%
            set aedt_var=ANSYSEM_ROOT211
            echo Found AEDT Version 21R1
          )
    ) else (
     set aedt_path=%ANSYSEM_ROOT212%
     set aedt_var=ANSYSEM_ROOT212
     echo Found AEDT Version 21R2
    )
) else (
    set aedt_path=%ANSYSEM_ROOT221%
    set aedt_var=ANSYSEM_ROOT221
    echo Found AEDT Version 22R1
)

set /p run=Python or Jupyter?(0=Spyder, 1=Jupyter, 2=Console)
setlocal enableDelayedExpansion

if not exist "%APPDATA%\pyaedt_env_ide\" (
    echo Installing Pyaedt
    cd "%APPDATA%"
    "%aedt_path%\commonfiles\CPython\3_7\winx64\Release\python\python.exe" -m venv "%APPDATA%\pyaedt_env_ide"
    "%APPDATA%\pyaedt_env_ide\Scripts\python.exe" -m pip install --upgrade pip
    "%APPDATA%\pyaedt_env_ide\Scripts\pip" install pyaedt
    "%APPDATA%\pyaedt_env_ide\Scripts\pip" install jupyterlab
    "%APPDATA%\pyaedt_env_ide\Scripts\pip" install spyder
    "%APPDATA%\pyaedt_env_ide\Scripts\pip" install ipython -U
    "%APPDATA%\pyaedt_env_ide\Scripts\pip" install ipyvtklink
    call "%APPDATA%\pyaedt_env_ide\Scripts\python" "%APPDATA%\pyaedt_env_ide\Lib\site-packages\pyaedt\misc\aedtlib_personalib_install.py" %aedt_var%
)
if [%1%]==[-update] ( 
    echo Updating Pyaedt
    "%APPDATA%\pyaedt_env_ide\Scripts\pip" install pyaedt -U
)
if %run%==1 (
     echo Launching Jupyter Lab
    "%APPDATA%\pyaedt_env_ide\Scripts\jupyter.exe" lab
) else ( if %run%==0 (
    echo Launching Spyder
    "%APPDATA%\pyaedt_env_ide\Scripts\spyder.exe"
    ) else (
    "%APPDATA%\pyaedt_env_ide\Scripts\ipython.exe"
    )
)

