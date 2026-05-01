@echo off
REM ============================================================
REM   SERI - Run the test suite (Windows)
REM ============================================================
REM   Double-click this file to run pytest on the SERI test
REM   suite. Useful to verify the package after installation
REM   or after making local changes.
REM
REM   The headline test reproduces the Abadla 2015 anchor
REM   case (manuscript section 5.1):  SERI(Abadla) ~ 2353
REM ============================================================

setlocal
cd /d "%~dp0\.."

where python >nul 2>nul
if errorlevel 1 (
    echo ERROR: Python was not found on your PATH.
    pause
    exit /b 1
)

python -m pytest tests -v

echo.
echo ============================================================
echo  Test run finished. Press any key to close this window.
echo ============================================================
pause >nul
endlocal
