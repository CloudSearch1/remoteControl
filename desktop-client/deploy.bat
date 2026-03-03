@echo off
chcp 65001 >nul
title Remote Desktop Client - Windows Deployment

echo ========================================
echo   Remote Desktop Client
echo   被控端部署脚本 (Windows)
echo ========================================
echo.

echo [1/5] 检查 Python 安装...
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

echo [2/5] 安装依赖...
pip install --upgrade pip -q
pip install -r requirements.txt -q
if errorlevel 1 (
    echo [错误] 依赖安装失败
    pause
    exit /b 1
)
echo [OK] 依赖安装完成
echo.

echo [3/5] 配置环境...
if not exist ".env" (
    copy .env.example .env
    echo [OK] 配置文件已创建
) else (
    echo [INFO] 配置文件已存在
)
echo.

echo [4/5] 编辑配置...
echo.
echo 请修改以下配置：
echo   SERVER_URL=ws://YOUR-VPS-IP:8080/ws/device
echo   DEVICE_ID=my-home-pc
echo   DEVICE_PASSWORD=your_password
echo.
pause
notepad .env
echo.

echo [5/5] 启动客户端...
echo.
echo 正在启动远程桌面客户端...
echo.
start "Remote Desktop Client" python client.py
echo.
echo [OK] 客户端已启动
echo.
echo ========================================
echo   部署完成！
echo ========================================
echo.
echo 客户端状态：运行中
echo 设备 ID: 见 .env 文件
echo.
echo 查看日志：客户端窗口
echo 停止服务：关闭客户端窗口
echo.
echo 提示：
echo   - 确保能访问 VPS 的 8080 端口
echo   - 检查防火墙设置
echo   - 查看配置：notepad .env
echo.
pause
