@echo off
chcp 65001 >nul
title Remote Desktop Relay Server - Windows Deployment

echo ========================================
echo   Remote Desktop Relay Server
echo   中转服务器部署脚本 (Windows)
echo ========================================
echo.

REM 检查管理员权限
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [错误] 请以管理员身份运行此脚本
    echo 右键点击脚本，选择"以管理员身份运行"
    pause
    exit /b 1
)

echo [1/6] 检查 Python 安装...
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Python
    echo 请安装 Python 3.8+：https://www.python.org/downloads/
    pause
    exit /b 1
)
echo [OK] Python 已安装
python --version
echo.

echo [2/6] 创建虚拟环境...
if not exist "venv" (
    python -m venv venv
    echo [OK] 虚拟环境已创建
) else (
    echo [INFO] 虚拟环境已存在
)
echo.

echo [3/6] 激活虚拟环境...
call venv\Scripts\activate.bat
echo [OK] 虚拟环境已激活
echo.

echo [4/6] 安装依赖...
pip install --upgrade pip -q
pip install -r requirements.txt -q
if errorlevel 1 (
    echo [错误] 依赖安装失败
    pause
    exit /b 1
)
echo [OK] 依赖安装完成
echo.

echo [5/6] 配置环境...
if not exist ".env" (
    copy .env.example .env
    echo [OK] 配置文件已创建
    echo.
    echo 请编辑 .env 文件修改密码：
    echo   SERVER_PASSWORD=your_password
    echo.
    pause
    notepad .env
) else (
    echo [INFO] 配置文件已存在
)
echo.

echo [6/6] 启动服务器...
taskkill /F /FI "WINDOWTITLE eq Remote Desktop Server*" >nul 2>&1
timeout /t 2 /nobreak >nul
start "Remote Desktop Server" python server.py
echo.
echo [OK] 服务器已启动
echo.

REM 等待 5 秒检查服务
timeout /t 5 /nobreak >nul
echo.
echo ========================================
echo   部署完成！
echo ========================================
echo.
echo 服务器状态：运行中
echo 访问地址：http://localhost:8080
echo.
echo 查看日志：server.log
echo 停止服务：关闭命令行窗口
echo.
echo 按任意键打开浏览器...
pause >nul
start http://localhost:8080

echo.
echo 提示：
echo   - 确保防火墙开放 8080 端口
echo   - 如果是 VPS，需要公网 IP
echo   - 查看配置：notepad .env
echo.
pause
