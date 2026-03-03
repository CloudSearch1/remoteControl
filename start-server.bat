@echo off
chcp 65001 >nul
title Remote Desktop Server

echo ========================================
echo   Remote Desktop Server
echo ========================================
echo.

echo 正在启动服务器...
echo.

python server.py

pause
