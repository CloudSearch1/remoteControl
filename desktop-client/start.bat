@echo off
chcp 65001 >nul
title Remote Desktop Client

echo ========================================
echo   Remote Desktop Client
echo ========================================
echo.

echo 正在启动客户端...
echo.

python client.py

pause
