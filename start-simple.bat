@echo off
chcp 65001 >nul
title Remote Desktop Server (Simple)

echo ========================================
echo   Remote Desktop Server
echo   (No Dependencies Required!)
echo ========================================
echo.
echo 正在启动服务器...
echo.
echo 访问地址:
echo   本地：http://localhost:5000
echo   远程：http://你的IP:5000
echo.
echo 密码：remote123
echo.
echo 按 Ctrl+C 停止服务器
echo.

python server_simple.py

pause
