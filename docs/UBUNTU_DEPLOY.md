# Ubuntu 部署脚本

> **Linux/Ubuntu 系统中转服务器部署指南**

---

## 📋 系统要求

- **操作系统**: Ubuntu 20.04+ / Debian 10+
- **Python**: 3.8+
- **权限**: root 或 sudo
- **网络**: 公网 IP
- **端口**: 8080

---

## 🚀 一键部署

### 方法 1: 自动部署脚本（推荐）

```bash
# 1. SSH 登录服务器
ssh root@your-vps-ip

# 2. 克隆项目
cd /opt
git clone git@github.com:CloudSearch1/remoteControl.git
cd remoteControl/relay-server

# 3. 运行部署脚本
chmod +x deploy.sh
sudo ./deploy.sh
```

**脚本会自动**:
- ✅ 更新系统
- ✅ 安装依赖
- ✅ 创建虚拟环境
- ✅ 安装 Python 包
- ✅ 配置环境
- ✅ 配置防火墙
- ✅ 启动服务

---

### 方法 2: 手动部署

```bash
# 1. SSH 登录
ssh root@your-vps-ip

# 2. 更新系统
apt update && apt upgrade -y

# 3. 安装依赖
apt install -y python3 python3-pip python3-venv git

# 4. 克隆项目
cd /opt
git clone git@github.com:CloudSearch1/remoteControl.git
cd remoteControl/relay-server

# 5. 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 6. 安装依赖
pip install --upgrade pip
pip install -r requirements.txt

# 7. 配置环境
cp .env.example .env
nano .env  # 修改密码

# 8. 启动服务
nohup python server.py > server.log 2>&1 &

# 9. 配置防火墙
ufw allow 8080/tcp
```

---

## 🔧 Systemd 服务配置

### 创建服务文件

```bash
sudo nano /etc/systemd/system/relay-server.service
```

**内容**:
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

### 启用服务

```bash
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

# 重启服务
sudo systemctl restart relay-server

# 停止服务
sudo systemctl stop relay-server
```

---

## 🔐 Nginx 反向代理（可选）

### 安装 Nginx

```bash
sudo apt install nginx -y
```

### 配置 Nginx

```bash
sudo nano /etc/nginx/sites-available/remote-desktop
```

**内容**:
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:8080;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 启用配置

```bash
sudo ln -s /etc/nginx/sites-available/remote-desktop /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 配置 HTTPS（推荐）

```bash
# 安装 certbot
sudo apt install certbot python3-certbot-nginx -y

# 申请证书
sudo certbot --nginx -d your-domain.com

# 自动续期
sudo crontab -e
# 添加：0 3 * * * certbot renew --quiet
```

---

## 📊 配置说明

### 服务器配置 (.env)

```bash
# 服务器监听
HOST=0.0.0.0
PORT=8080

# 认证密码（必须修改！）
SERVER_PASSWORD=YourSecurePassword123!

# 连接超时（秒）
TIMEOUT=300

# 日志级别
LOG_LEVEL=INFO
```

### 防火墙配置

**UFW**:
```bash
sudo ufw allow 8080/tcp
sudo ufw reload
sudo ufw status
```

**iptables**:
```bash
sudo iptables -A INPUT -p tcp --dport 8080 -j ACCEPT
sudo iptables-save
```

**云服务器安全组**:
- 阿里云/腾讯云：控制台 → 安全组 → 添加规则 TCP 8080
- AWS：安全组 → 入站规则 → 添加 TCP 8080

---

## 📝 日志管理

### 查看日志

```bash
# 实时查看
tail -f server.log

# 查看最后 100 行
tail -n 100 server.log

# Systemd 日志
sudo journalctl -u relay-server -f
```

### 日志轮转

```bash
sudo nano /etc/logrotate.d/relay-server
```

**内容**:
```
/var/log/relay-server.log {
    daily
    rotate 7
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    postrotate
        systemctl reload relay-server
    endscript
}
```

---

## 🔍 故障排查

### 服务无法启动

```bash
# 检查端口
sudo netstat -tlnp | grep 8080

# 检查日志
tail -f server.log

# 手动启动测试
cd /opt/remoteControl/relay-server
source venv/bin/activate
python server.py
```

### 无法访问

```bash
# 检查防火墙
sudo ufw status

# 检查服务状态
sudo systemctl status relay-server

# 检查端口监听
sudo ss -tlnp | grep 8080

# 测试本地访问
curl http://localhost:8080/health
```

### 连接超时

```bash
# 检查公网 IP
curl ifconfig.me

# 测试端口
telnet your-vps-ip 8080

# 检查安全组
# 登录云控制台检查安全组配置
```

---

## 📋 部署检查清单

- [ ] 系统已更新
- [ ] Python 3.8+ 已安装
- [ ] 项目已克隆
- [ ] 虚拟环境已创建
- [ ] 依赖已安装
- [ ] 密码已修改
- [ ] 防火墙已配置
- [ ] 服务已启动
- [ ] 能访问 http://VPS-IP:8080
- [ ] 配置了 systemd 服务（推荐）
- [ ] 配置了 Nginx（可选）
- [ ] 配置了 HTTPS（推荐）

---

## 🚀 快速命令参考

```bash
# 启动服务
sudo systemctl start relay-server

# 停止服务
sudo systemctl stop relay-server

# 重启服务
sudo systemctl restart relay-server

# 查看状态
sudo systemctl status relay-server

# 查看日志
sudo journalctl -u relay-server -f

# 防火墙
sudo ufw allow 8080/tcp

# 更新部署
cd /opt/remoteControl/relay-server
sudo git pull
sudo systemctl restart relay-server
```

---

*Ubuntu 部署脚本 - 让 Linux 部署更简单* 🚀
