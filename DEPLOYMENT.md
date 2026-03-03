# Git 部署指南

> **通过 Git 快速部署到公网服务器**

---

## 📋 前提条件

### 公网服务器
- ✅ Linux (Ubuntu/Debian)
- ✅ Python 3.8+
- ✅ Git
- ✅ 公网 IP
- ✅ 开放端口：8080

### 被控电脑
- ✅ Windows/Mac/Linux
- ✅ Python 3.8+
- ✅ Git（可选）

---

## 🚀 部署步骤

### 1. 初始化 Git 仓库

**在你的电脑上**:

```bash
cd F:\remote-desktop
git init
git add .
git commit -m "Initial commit - Remote Desktop Relay"
```

### 2. 推送到 GitHub

**创建 GitHub 仓库**:
1. 访问 https://github.com
2. 创建新仓库：`remote-desktop`
3. 选择私有或公开

**推送代码**:
```bash
git remote add origin https://github.com/your-username/remote-desktop.git
git branch -M main
git push -u origin main
```

### 3. 部署到公网服务器

**SSH 登录服务器**:
```bash
ssh user@your-server-ip
```

**克隆项目**:
```bash
cd /opt
git clone https://github.com/your-username/remote-desktop.git
cd remote-desktop/relay-server
```

**配置环境**:
```bash
# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 配置
cp .env.example .env
nano .env  # 修改密码和配置
```

**启动服务器**:
```bash
# 方式 1: 直接启动
./start.sh

# 方式 2: 后台运行（推荐）
nohup python server.py > server.log 2>&1 &

# 方式 3: 使用 systemd（生产环境）
sudo nano /etc/systemd/system/relay-server.service
```

**Systemd 配置** (可选):
```ini
[Unit]
Description=Remote Desktop Relay Server
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/remote-desktop/relay-server
Environment="PATH=/opt/remote-desktop/relay-server/venv/bin"
ExecStart=/opt/remote-desktop/relay-server/venv/bin/python server.py
Restart=always

[Install]
WantedBy=multi-user.target
```

**启用服务**:
```bash
sudo systemctl daemon-reload
sudo systemctl enable relay-server
sudo systemctl start relay-server
sudo systemctl status relay-server
```

### 4. 配置防火墙

**Ubuntu/Debian**:
```bash
sudo ufw allow 8080/tcp
sudo ufw reload
```

**CentOS/RHEL**:
```bash
sudo firewall-cmd --permanent --add-port=8080/tcp
sudo firewall-cmd --reload
```

**云服务器**（阿里云/腾讯云/AWS）:
- 登录控制台
- 安全组配置
- 添加入站规则：TCP 8080

### 5. 部署被控客户端

**在你的 Windows 电脑上**:

```bash
cd F:\remote-desktop\desktop-client

# 安装依赖
pip install -r requirements.txt

# 配置
copy .env.example .env
notepad .env  # 修改服务器地址为公网 IP

# 启动
start.bat
```

### 6. 访问控制界面

**浏览器访问**:
```
http://your-server-ip:8080
```

**输入**:
- 设备 ID: `my-pc-001`
- 密码：你在 `.env` 中设置的密码

---

## 🔄 更新部署

### 更新服务器代码

```bash
# SSH 登录服务器
ssh user@your-server-ip

# 进入项目目录
cd /opt/remote-desktop/relay-server

# 拉取最新代码
git pull

# 重启服务
sudo systemctl restart relay-server

# 或如果使用后台运行
pkill -f server.py
nohup python server.py > server.log 2>&1 &
```

### 更新客户端代码

```bash
# 在你的电脑上
cd F:\remote-desktop
git pull

# 重启客户端
# 关闭当前运行的客户端
# 重新运行 start.bat
```

---

## 🔐 安全加固

### 1. 使用 HTTPS

**安装 Nginx**:
```bash
sudo apt install nginx
```

**配置 Nginx**:
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
    }
}
```

**申请 SSL 证书**:
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### 2. 修改默认密码

编辑 `.env`:
```bash
SERVER_PASSWORD=your_very_strong_password
```

### 3. 配置防火墙白名单

```bash
# 只允许特定 IP 访问
sudo ufw allow from your-trusted-ip to any port 8080
```

### 4. 启用日志

```bash
# 查看日志
tail -f /opt/remote-desktop/relay-server/server.log

# Systemd 日志
sudo journalctl -u relay-server -f
```

---

## ❓ 故障排查

### 服务器无法访问

1. **检查服务状态**:
   ```bash
   sudo systemctl status relay-server
   ```

2. **检查端口**:
   ```bash
   netstat -tlnp | grep 8080
   ```

3. **检查防火墙**:
   ```bash
   sudo ufw status
   ```

4. **查看日志**:
   ```bash
   tail -f server.log
   ```

### 客户端连接失败

1. **检查服务器地址**: 确保 `.env` 中的 `SERVER_URL` 正确
2. **检查网络**: 确保能 ping 通服务器
3. **检查密码**: 确保客户端和服务器密码一致
4. **查看日志**: 客户端启动时的错误信息

### 画面卡顿

1. **降低图像质量**: 编辑 `.env` 中的 `IMAGE_QUALITY`
2. **增大截图间隔**: 编辑 `SCREEN_INTERVAL`
3. **检查带宽**: 确保网络带宽充足

---

## 📊 性能优化

### 服务器优化

1. **使用 Nginx 反向代理**
2. **启用 WebSocket 压缩**
3. **限制并发连接数**
4. **配置连接超时**

### 客户端优化

1. **降低图像质量**: `IMAGE_QUALITY=60`
2. **增大截图间隔**: `SCREEN_INTERVAL=0.2`
3. **减小分辨率**: 在代码中设置

---

## 🎯 快速部署脚本

**服务器一键部署**:

```bash
#!/bin/bash

# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装依赖
sudo apt install -y python3 python3-pip python3-venv git nginx

# 克隆项目
cd /opt
sudo git clone https://github.com/your-username/remote-desktop.git
sudo chown -R $USER:$USER remote-desktop
cd remote-desktop/relay-server

# 配置环境
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 配置
cp .env.example .env
nano .env  # 修改配置

# 启动
./start.sh
```

---

*部署完成！开始远程控制吧！* 🚀
