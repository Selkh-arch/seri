@echo off
REM ============================================================
REM   SERI - Launch the graphical interface (Windows)
REM ============================================================
REM   Double-click this file to open the SERI calculator window.
REM
REM   The window opens pre-filled with the Abadla 2015 anchor
REM   case (P=10.79 mm, A=1624 km^2, February, mixed substrate)
REM   so you can verify the installation immediately.
REM
REM   If the window does not appear, run install.bat first.
REM ============================================================

setlocal
cd /d "%~dp0\.."

where python >nul 2>nul
if errorlevel 1 (
    echo ERROR: Python was not found on your PATH.
    echo Run install.bat first, or install Python from python.org.
    pause
    exit /b 1
)

REM Try the installed console script first; fall back to module form.
where seri-gui >nul 2>nul
if not errorlevel 1 (
    seri-gui
    exit /b %errorlevel%
)

python -m seri.gui
if errorlevel 1 (
    echo.
    echo ERROR: could not launch the GUI.
    echo Run install.bat first to install the package.
    pause
    exit /b 1
)

endlocal
