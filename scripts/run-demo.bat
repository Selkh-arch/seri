@echo off
REM ============================================================
REM   SERI - Run the Abadla 2015 demonstration (Windows)
REM ============================================================
REM   Double-click this file to run the bundled demo script
REM   in a console window. The console stays open after the
REM   demo finishes so you can read the output.
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

python examples\demo_abadla_2015.py

echo.
echo ============================================================
echo  Demo finished. Press any key to close this window.
echo ============================================================
pause >nul
endlocal
