@echo off
setlocal

set "VENV_PYTHON=D:\AntigravitySupport\Superscan_venv\Scripts\python.exe"

if not exist "%VENV_PYTHON%" (
    echo [ERROR] Virtual Environment not found at D:\AntigravitySupport\Superscan_venv
    echo Please run Install.bat first.
    pause
    exit /b 1
)

:: Run the application (headless)
start "" "%VENV_PYTHON%" main.py
