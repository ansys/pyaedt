setlocal enableDelayedExpansion
echo %1%
cd "%APPDATA%"
if not exist "%APPDATA%\aedtlibenv\" (
    "%ANSYSEM_ROOT211%\commonfiles\CPython\3_7\winx64\Release\python\python.exe" -m venv "%APPDATA%\aedtlibenv"
    "%APPDATA%\aedtlibenv\Scripts\pip" install -i https://pkgs.dev.azure.com/EMEA-FES-E/Public-Releases/_packaging/AEDTLib_Public/pypi/simple/ --extra-index-url https://pypi.org/simple AEDTLib --trusted-host pypi.org --trusted-host files.pythonhosted.org
    call "%APPDATA%\aedtlibenv\Scripts\python" "%APPDATA%\aedtlibenv\Lib\site-packages\AEDTLib\Misc\aedtlib_personalib_install.py" ANSYSEM_ROOT211
)
if [%1%]==[-update] (
    "%APPDATA%\aedtlibenv\Scripts\pip" install --upgrade -i https://pkgs.dev.azure.com/EMEA-FES-E/Public-Releases/_packaging/AEDTLib_Public/pypi/simple/ --extra-index-url https://pypi.org/simple AEDTLib --trusted-host pypi.org --trusted-host files.pythonhosted.org
)
"%APPDATA%\aedtlibenv\Scripts\python"