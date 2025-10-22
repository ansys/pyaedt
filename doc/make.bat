@ECHO OFF

pushd %~dp0

REM Command file for Sphinx documentation

if "%SPHINXOPTS%" == "" (
	set SPHINXOPTS=-j auto --color -w build_errors.txt
)
if "%SPHINXBUILD%" == "" (
	set SPHINXBUILD=sphinx-build
)
set SOURCEDIR=source
set BUILDDIR=_build
set LINKCHECKDIR=\%BUILDDIR%\linkcheck
set LINKCHECKOPTS=-d %BUILDDIR%\.doctrees -W --keep-going --color
set SKIP_BUILD_CHEAT_SHEET=False

REM This LOCs are used to uninstall and install specific package(s) during CI/CD
for /f %%i in ('pip freeze ^| findstr /c:"vtk-osmesa"') do set is_vtk_osmesa_installed=%%i
if NOT "%is_vtk_osmesa_installed%" == "vtk-osmesa" if "%ON_CI%" == "True" (
	echo "Removing package(s) to avoid conflicts with package(s) needed for CI/CD"
	pip uninstall --yes vtk
	echo "Installing CI/CD required package(s)"
	pip install --index-url https://wheels.vtk.org vtk-osmesa==9.3.1)
REM End of CICD dedicated setup

if "%1" == "" goto help
if "%1" == "clean" goto clean
if "%1" == "html" goto html
if "%1" == "pdf" goto pdf
if "%1" == "livehtml" goto livehtml

%SPHINXBUILD% >NUL 2>NUL
if errorlevel 9009 (
	echo.
	echo.The 'sphinx-build' command was not found. Make sure you have Sphinx
	echo.installed, then set the SPHINXBUILD environment variable to point
	echo.to the full path of the 'sphinx-build' executable. Alternatively you
	echo.may add the Sphinx directory to PATH.
	echo.
	echo.If you don't have Sphinx installed, grab it from
	echo.https://sphinx-doc.org/
	exit /b 1
)

%SPHINXBUILD% -M %1 %SOURCEDIR% %BUILDDIR% %SPHINXOPTS% %O%
goto end

:help
%SPHINXBUILD% -M help %SOURCEDIR% %BUILDDIR% %SPHINXOPTS% %O%
goto end

:clean
echo Cleaning everything
rmdir /s /q %SOURCEDIR%\examples > /NUL 2>&1 
rmdir /s /q %BUILDDIR% > /NUL 2>&1 
for /d /r %SOURCEDIR% %%d in (_autosummary) do @if exist "%%d" rmdir /s /q "%%d"
goto end

:html
echo Building HTML pages
::FIXME: currently linkcheck freezes and further investigation must be performed
::%SPHINXBUILD% -M linkcheck %SOURCEDIR% %BUILDDIR% %SPHINXOPTS% %LINKCHECKOPTS% %O%
%SPHINXBUILD% -M html %SOURCEDIR% %BUILDDIR% %SPHINXOPTS% %O%
echo
echo "Build finished. The HTML pages are in %BUILDDIR%."
goto end

:pdf
echo Building PDF pages
%SPHINXBUILD% -M latex %SOURCEDIR% %BUILDDIR% %SPHINXOPTS% %O%
cd "%BUILDDIR%\latex"
for %%f in (*.tex) do (
xelatex "%%f" --interaction=nonstopmode)
echo "Build finished. The PDF pages are in %BUILDDIR%."
goto end

:livehtml
echo Building live HTML pages
sphinx-autobuild "%SOURCEDIR%" "%BUILDDIR%" %SPHINXOPTS% %O%
goto end

:end
popd
