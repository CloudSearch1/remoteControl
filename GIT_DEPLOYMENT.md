# 🚀 快速部署指南

> **5 分钟部署到公网服务器**

---

## 📋 项目已完成

✅ **Git 仓库已初始化**
- 位置：`F:\remote-desktop\`
- 提交数：1
- 文件数：25+

---

## 🎯 部署步骤

### 步骤 1: 推送到 GitHub

**在你的电脑上运行**:

```bash
cd F:\remote-desktop

# 1. 创建 GitHub 仓库
# 访问 https://github.com/new
# 仓库名：remote-desktop
# 选择私有或公开

# 2. 添加远程仓库
git remote add origin https://github.com/YOUR_USERNAME/remote-desktop.git

# 3. 推送代码
git branch -M main
git push -u origin main
```

---

### 步骤 2: 部署到公网服务器

**SSH 登录服务器**:
```bash
ssh root@your-server-ip
```

**克隆项目**:
```bash
cd /opt
git clone https://github.com/YOUR_USERNAME/remote-desktop.git
cd remote-desktop/relay-server
```

**安装依赖**:
```bash
# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

**配置服务器**:
```bash
# 复制配置
cp .env.example .env

# 编辑配置（修改密码）
nano .env
```

**修改 `.env`**:
```bash
SERVER_PASSWORD=your_strong_password
```

**启动服务器**:
```bash
# 方式 1: 直接启动
python server.py

# 方式 2: 后台运行（推荐）
nohup python server.py > server.log 2>&1 &

# 方式 3: 使用 systemd（生产环境）
```

---

### 步骤 3: 配置防火墙

**Ubuntu/Debian**:
```bash
sudo ufw allow 8080/tcp
sudo ufw reload
```

**云服务器**（阿里云/腾讯云）:
1. 登录控制台
2. 安全组配置
3. 添加入站规则：TCP 8080

---

### 步骤 4: 部署被控客户端

**在你的 Windows 电脑上**:

```bash
cd F:\remote-desktop\desktop-client

# 安装依赖
pip install -r requirements.txt

# 配置
copy .env.example .env
notepad .env
```

**修改 `.env`**:
```bash
SERVER_URL=ws://YOUR_SERVER_IP:8080/ws/device
DEVICE_PASSWORD=your_strong_password
```

**启动客户端**:
```bash
start.bat
```

---

### 步骤 5: 访问控制界面

**浏览器访问**:
```
http://YOUR_SERVER_IP:8080
```

**输入**:
- 设备 ID: `my-pc-001`
- 密码：`your_strong_password`

---

## 📁 项目结构

```
remote-desktop/
├── relay-server/          # 公网服务器
│   ├── server.py          # 中继服务器
│   ├── requirements.txt   # 依赖
│   ├── start.sh          # 启动脚本
│   └── .env.example      # 配置模板
│
├── desktop-client/        # 被控客户端
│   ├── client.py          # 客户端程序
│   ├── requirements.txt   # 依赖
│   ├── start.bat         # 启动脚本
│   └── .env.example      # 配置模板
│
├── DEPLOYMENT.md          # 详细部署文档
├── README_RELAY.md        # 使用说明
└── .git/                  # Git 仓库
```

---

## 🔐 安全建议

### 必须做的
1. ✅ **修改默认密码**
   ```bash
   SERVER_PASSWORD=your_very_strong_password
   ```

2. ✅ **配置防火墙**
   - 只开放 8080 端口
   - 限制访问 IP（可选）

3. ✅ **使用 HTTPS**（推荐）
   - 配置 Nginx 反向代理
   - 申请 SSL 证书

### 可选的
- [ ] 配置域名
- [ ] 启用日志记录
- [ ] 设置连接超时
- [ ] 限制并发连接

---

## 🔄 更新代码

### 更新服务器
```bash
# SSH 登录
ssh root@your-server-ip

# 进入目录
cd /opt/remote-desktop/relay-server

# 拉取代码
git pull

# 重启服务
pkill -f server.py
nohup python server.py > server.log 2>&1 &
```

### 更新客户端
```bash
cd F:\remote-desktop
git pull

# 重启客户端
# 关闭当前运行的
# 重新运行 start.bat
```

---

## ❓ 常见问题

### Q: 连接失败？
**A**: 检查：
1. 服务器是否运行
2. 防火墙是否开放 8080
3. IP 地址是否正确
4. 密码是否一致

### Q: 画面卡顿？
**A**: 降低质量：
```bash
# 编辑 .env
IMAGE_QUALITY=60
SCREEN_INTERVAL=0.2
```

### Q: 如何开机自启？
**A**: 使用 systemd:
```bash
sudo nano /etc/systemd/system/relay-server.service
```

参考 `DEPLOYMENT.md` 中的完整配置。

---

## 📊 架构说明

```
控制端 (浏览器)
    ↓ HTTP/WebSocket
公网服务器 (中继)
    ↓ WebSocket
被控端 (你的电脑)
```

**工作流程**:
1. 被控端连接公网服务器
2. 控制端通过浏览器访问公网服务器
3. 服务器转发控制命令和屏幕数据

---

## 🎉 完成！

**现在你可以**:
1. ✅ 推送到 GitHub
2. ✅ 部署到公网服务器
3. ✅ 启动被控客户端
4. ✅ 浏览器远程控制

**项目位置**: `F:\remote-desktop\`

**详细文档**: `DEPLOYMENT.md`

---

*开始部署吧！* 🚀
