@echo off
REM ============================================================
REM   SERI - Open the Jupyter demo notebook (Windows)
REM ============================================================
REM   Double-click this file to launch Jupyter and open the
REM   demonstration notebook in your default web browser.
REM
REM   Requires:  Jupyter installed in the active Python env.
REM   Install with:  pip install jupyter
REM ============================================================

setlocal
cd /d "%~dp0\.."

where python >nul 2>nul
if errorlevel 1 (
    echo ERROR: Python was not found on your PATH.
    pause
    exit /b 1
)

REM Check for Jupyter; install on the fly if missing.
python -m jupyter --version >nul 2>nul
if errorlevel 1 (
    echo Jupyter is not installed in this Python environment.
    echo Installing it now (this happens only the first time)...
    python -m pip install --upgrade jupyter
    if errorlevel 1 (
        echo ERROR: failed to install Jupyter.
        pause
        exit /b 1
    )
)

python -m jupyter notebook examples\notebook_demo.ipynb

endlocal
