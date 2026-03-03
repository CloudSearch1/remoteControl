# 部署脚本和配置示例

> **完整的部署脚本和配置文件示例**

---

## 📋 目录

1. [中转服务器部署脚本](#1-中转服务器部署脚本)
2. [被控端部署脚本](#2-被控端部署脚本)
3. [配置文件示例](#3-配置文件示例)
4. [Systemd 服务配置](#4-systemd 服务配置)
5. [Nginx 反向代理](#5-nginx 反向代理)
6. [一键部署脚本](#6-一键部署脚本)

---

## 1. 中转服务器部署脚本

### deploy-server.sh

```bash
#!/bin/bash

# Remote Desktop Relay Server Deployment Script
# 中转服务器部署脚本

set -e

echo "========================================"
echo "  Remote Desktop Relay Server"
echo "  中转服务器部署脚本"
echo "========================================"
echo ""

# 检查是否 root
if [ "$EUID" -ne 0 ]; then 
    echo "请使用 root 用户或 sudo 运行此脚本"
    exit 1
fi

# 更新系统
echo "[1/8] 更新系统..."
apt update && apt upgrade -y

# 安装依赖
echo "[2/8] 安装系统依赖..."
apt install -y python3 python3-pip python3-venv git curl

# 克隆项目
echo "[3/8] 克隆项目..."
cd /opt
if [ -d "remoteControl" ]; then
    echo "项目已存在，跳过克隆"
else
    git clone git@github.com:CloudSearch1/remoteControl.git
fi
cd remoteControl/relay-server

# 创建虚拟环境
echo "[4/8] 创建虚拟环境..."
python3 -m venv venv
source venv/bin/activate

# 安装 Python 依赖
echo "[5/8] 安装 Python 依赖..."
pip install --upgrade pip
pip install -r requirements.txt

# 配置环境
echo "[6/8] 配置环境..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "请编辑 .env 文件修改密码"
    read -p "输入服务器密码：" -s PASSWORD
    echo ""
    sed -i "s/SERVER_PASSWORD=.*/SERVER_PASSWORD=$PASSWORD/" .env
fi

# 配置防火墙
echo "[7/8] 配置防火墙..."
if command -v ufw &> /dev/null; then
    ufw allow 8080/tcp
    echo "防火墙已配置，开放端口 8080"
else
    echo "未检测到 ufw，请手动配置防火墙"
fi

# 启动服务
echo "[8/8] 启动服务..."
pkill -f "python server.py" || true
nohup python server.py > server.log 2>&1 &

# 等待启动
sleep 3

# 检查状态
if pgrep -f "python server.py" > /dev/null; then
    echo ""
    echo "========================================"
    echo "  部署成功！"
    echo "========================================"
    echo ""
    echo "服务状态：运行中"
    echo "访问地址：http://$(curl -s ifconfig.me):8080"
    echo "日志文件：server.log"
    echo ""
    echo "查看日志：tail -f server.log"
    echo "停止服务：pkill -f 'python server.py'"
    echo ""
else
    echo ""
    echo "========================================"
    echo "  部署失败！"
    echo "========================================"
    echo ""
    echo "请检查日志：server.log"
    exit 1
fi
```

---

## 2. 被控端部署脚本

### deploy-client.bat

```batch
@echo off
chcp 65001 >nul
title Remote Desktop Client Deployment

echo ========================================
echo   Remote Desktop Client
echo   被控端部署脚本
echo ========================================
echo.

echo [1/4] 检查 Python 安装...
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Python，请先安装 Python 3.8+
    echo 下载地址：https://www.python.org/downloads/
    pause
    exit /b 1
)
echo [OK] Python 已安装
echo.

echo [2/4] 安装依赖...
pip install -r requirements.txt
if errorlevel 1 (
    echo [错误] 依赖安装失败
    pause
    exit /b 1
)
echo [OK] 依赖安装完成
echo.

echo [3/4] 配置环境...
if not exist ".env" (
    copy .env.example .env
    echo [OK] 配置文件已创建
) else (
    echo [INFO] 配置文件已存在
)
echo.

echo [4/4] 编辑配置...
echo.
echo 请编辑 .env 文件，修改以下配置：
echo   SERVER_URL=ws://YOUR-VPS-IP:8080/ws/device
echo   DEVICE_ID=my-home-pc
echo   DEVICE_PASSWORD=your_password
echo.
pause
notepad .env
echo.

echo ========================================
echo   部署完成！
echo ========================================
echo.
echo 启动客户端：python client.py
echo.
pause
```

---

## 3. 配置文件示例

### 服务器配置 (.env)

```bash
# 服务器配置
HOST=0.0.0.0
PORT=8080

# 认证密码（必须修改！）
SERVER_PASSWORD=YourStrongPassword123!

# 连接超时（秒）
TIMEOUT=300

# 日志级别
LOG_LEVEL=INFO
```

### 被控端配置 (.env)

```bash
# 服务器地址（修改为你的 VPS IP）
SERVER_URL=ws://123.45.67.89:8080/ws/device

# 设备 ID（自定义）
DEVICE_ID=my-home-pc

# 认证密码（与服务器一致）
DEVICE_PASSWORD=YourStrongPassword123!

# 图像质量 (1-100)
IMAGE_QUALITY=75

# 截图间隔 (秒)
SCREEN_INTERVAL=0.1
```

---

## 4. Systemd 服务配置

### relay-server.service

```ini
[Unit]
Description=Remote Desktop Relay Server
Documentation=https://github.com/CloudSearch1/remoteControl
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/opt/remoteControl/relay-server
Environment="PATH=/opt/remoteControl/relay-server/venv/bin"
ExecStart=/opt/remoteControl/relay-server/venv/bin/python server.py
Restart=always
RestartSec=5
StandardOutput=append:/var/log/relay-server.log
StandardError=append:/var/log/relay-server.error.log

# 安全配置
NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

**安装服务**:
```bash
# 复制服务文件
sudo cp relay-server.service /etc/systemd/system/

# 重载 systemd
sudo systemctl daemon-reload

# 启用服务
sudo systemctl enable relay-server

# 启动服务
sudo systemctl start relay-server

# 查看状态
sudo systemctl status relay-server

# 查看日志
sudo journalctl -u relay-server -f
```

---

## 5. Nginx 反向代理

### nginx.conf

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    # 日志
    access_log /var/log/nginx/relay-access.log;
    error_log /var/log/nginx/relay-error.log;
    
    # 客户端真实 IP
    set_real_ip_from 0.0.0.0/0;
    real_ip_header X-Forwarded-For;
    real_ip_recursive on;
    
    location / {
        proxy_pass http://localhost:8080;
        proxy_http_version 1.1;
        
        # WebSocket 支持
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # 代理头
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 超时
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # 静态文件缓存
    location /static {
        proxy_pass http://localhost:8080/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

**HTTPS 配置** (推荐):
```bash
# 安装 certbot
sudo apt install certbot python3-certbot-nginx

# 申请证书
sudo certbot --nginx -d your-domain.com

# 自动续期
sudo crontab -e
# 添加：0 3 * * * certbot renew --quiet
```

---

## 6. 一键部署脚本

### VPS 一键部署

```bash
#!/bin/bash

# One-Click Deployment Script for Remote Desktop Relay Server
# VPS 一键部署脚本

set -e

echo "========================================"
echo "  Remote Desktop Relay Server"
echo "  VPS 一键部署脚本"
echo "========================================"
echo ""

# 检查 root
if [ "$EUID" -ne 0 ]; then 
    echo "错误：请使用 root 用户运行"
    exit 1
fi

# 获取 VPS IP
VPS_IP=$(curl -s ifconfig.me)

echo "VPS IP: $VPS_IP"
echo ""

# 部署
cd /opt
git clone git@github.com:CloudSearch1/remoteControl.git
cd remoteControl/relay-server

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
read -p "设置服务器密码：" -s PASSWORD
echo ""
sed -i "s/SERVER_PASSWORD=.*/SERVER_PASSWORD=$PASSWORD/" .env

# Systemd 服务
cat > /etc/systemd/system/relay-server.service << EOF
[Unit]
Description=Remote Desktop Relay Server
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/remoteControl/relay-server
Environment="PATH=/opt/remoteControl/relay-server/venv/bin"
ExecStart=/opt/remoteControl/relay-server/venv/bin/python server.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable relay-server
systemctl start relay-server

# 防火墙
ufw allow 8080/tcp

echo ""
echo "========================================"
echo "  部署完成！"
echo "========================================"
echo ""
echo "访问地址：http://$VPS_IP:8080"
echo "服务状态：systemctl status relay-server"
echo "日志：journalctl -u relay-server -f"
echo ""
```

### Windows 一键部署

```batch
@echo off
chcp 65001 >nul
title Remote Desktop Client - One Click Install

echo ========================================
echo   Remote Desktop Client
echo   Windows 一键部署
echo ========================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未安装 Python
    echo 请访问：https://www.python.org/downloads/
    pause
    exit /b 1
)

pip install -r requirements.txt
if not exist ".env" copy .env.example .env

echo.
echo ========================================
echo   部署完成！
echo ========================================
echo.
echo 编辑 .env 文件配置服务器地址
echo 然后运行：python client.py
echo.
pause
```

---

## 📊 配置检查清单

### 服务器
- [ ] 修改默认密码
- [ ] 配置防火墙
- [ ] 设置 systemd 服务
- [ ] 配置 Nginx（可选）
- [ ] 启用 HTTPS（推荐）
- [ ] 配置日志轮转

### 被控端
- [ ] 修改 SERVER_URL 为 VPS IP
- [ ] 设置设备 ID
- [ ] 修改密码（与服务器一致）
- [ ] 测试连接

### 控制端
- [ ] 记录 VPS IP
- [ ] 记录设备 ID
- [ ] 记录密码
- [ ] 测试浏览器访问

---

*部署脚本和配置示例 - 让部署更简单* 🚀
