@echo off
setlocal
chcp 65001 > nul

echo ========================================================
echo   Superscan Installer (D-Drive Environment Edition)
echo ========================================================

:: 1. Check D Drive
if not exist "D:\" (
    echo [ERROR] D drive not found!
    echo This application requires a D drive to store heavy libraries.
    echo Please insert a D drive or contact support.
    pause
    exit /b 1
)

:: 2. Create Directory
set "TARGET_DIR=D:\AntigravitySupport"
if not exist "%TARGET_DIR%" (
    echo [INFO] Creating directory: %TARGET_DIR%
    mkdir "%TARGET_DIR%"
)

:: 3. Create venv
set "VENV_DIR=%TARGET_DIR%\Superscan_venv"
if not exist "%VENV_DIR%" (
    echo [INFO] Creating Python Virtual Environment at %VENV_DIR%...
    python -m venv "%VENV_DIR%"
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create venv. Is Python installed?
        pause
        exit /b 1
    )
) else (
    echo [INFO] Virtual Environment already exists.
)

:: 4. Install Dependencies
echo [INFO] Installing dependencies (this may take a while)...
echo Installing: EasyOCR, PyTorch, FastAPI, OpenCV, etc.

:: Ensure pip is up to date
"%VENV_DIR%\Scripts\python.exe" -m pip install --upgrade pip

:: Install usage libraries
"%VENV_DIR%\Scripts\pip" install easyocr fastapi uvicorn[standard] opencv-python pystray Pillow python-dotenv cv2-enumerate-cameras numpy requests

if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies.
    pause
    exit /b 1
)

echo.
echo ========================================================
echo   Installation Complete!
echo ========================================================
echo.
echo You can now run "start_app.bat" to launch Superscan.
pause
