@echo off
chcp 65001 >nul
title Remote Desktop - Configuration Wizard

echo ========================================
echo   Remote Desktop Configuration
echo ========================================
echo.

echo [1/4] Installing Server Dependencies...
echo This may take 5-10 minutes...
echo.

pip install flask flask-socketio pillow pyautogui psutil python-dotenv eventlet

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Server installation failed!
    echo Please check your internet connection and try again.
    pause
    exit /b 1
)

echo.
echo [OK] Server dependencies installed!
echo.

echo [2/4] Installing Client Dependencies...
echo.

pip install PyQt5 requests python-dotenv pillow

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [WARN] Client installation failed!
    echo You can still use the server, but client won't work.
    echo.
)

echo.
echo [3/4] Configuration Complete!
echo.

echo ========================================
echo   Next Steps:
echo ========================================
echo.
echo 1. Edit .env file to change password:
echo    SERVER_PASSWORD=your_password
echo.
echo 2. Start Server:
echo    start-server.bat
echo.
echo 3. Start Client (on another PC):
echo    start-client.bat
echo.

pause
