@echo off
REM ============================================================
REM   SERI - First-time installation script (Windows)
REM ============================================================
REM   Double-click this file to install the SERI package and
REM   its optional plotting / Jupyter dependencies into the
REM   currently active Python environment.
REM
REM   What this script does:
REM     1. Checks that Python is on PATH.
REM     2. Upgrades pip.
REM     3. Installs SERI in editable mode from this folder, with
REM        the [plot] and [dev] extras (matplotlib + pytest).
REM     4. Runs the test suite to confirm the install works.
REM
REM   Pre-requisites:
REM     - Python 3.9 or later, with "Add Python to PATH" enabled
REM       at install time. Download from python.org if needed.
REM ============================================================

setlocal
cd /d "%~dp0\.."

echo.
echo === Checking Python installation ===
where python >nul 2>nul
if errorlevel 1 (
    echo.
    echo ERROR: Python was not found on your PATH.
    echo Please install Python 3.9 or later from https://www.python.org/downloads/
    echo and re-run this script. Make sure to tick "Add Python to PATH"
    echo during installation.
    echo.
    pause
    exit /b 1
)
python --version

echo.
echo === Upgrading pip ===
python -m pip install --upgrade pip

echo.
echo === Installing SERI (editable, with plotting + dev extras) ===
python -m pip install -e ".[plot,dev]"
if errorlevel 1 (
    echo.
    echo ERROR: pip install failed. See messages above.
    echo.
    pause
    exit /b 1
)

echo.
echo === Running the test suite ===
python -m pytest tests -q
if errorlevel 1 (
    echo.
    echo WARNING: Some tests failed. The package is installed but the
    echo Abadla 2015 anchor case may not be reproducing correctly.
    echo.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo   SUCCESS. SERI v1.0 is installed.
echo.
echo   You can now:
echo     - Double-click run-gui.bat       to open the graphical interface
echo     - Double-click run-demo.bat      to run the Abadla 2015 demo
echo     - Double-click run-notebook.bat  to open the Jupyter notebook
echo     - Or, from any terminal:         seri --help
echo ============================================================
echo.
pause
endlocal
