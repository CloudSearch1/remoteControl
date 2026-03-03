# 三设备远程桌面控制系统

> **基于公网中继的三设备架构远程桌面系统**

---

## 🏗️ 系统架构

### 三设备架构

```
┌─────────────────┐      WebSocket      ┌──────────────────┐      WebSocket      ┌─────────────────┐
│   控制端         │ ←─────────────────→ │   中转服务器      │ ←─────────────────→ │   被控端         │
│   (浏览器)       │    HTTP/WebSocket   │   (公网 VPS)      │    WebSocket        │   (Windows)      │
│                 │                     │                  │                     │                 │
│ 任何设备         │                     │ Linux            │                     │ 你的电脑         │
│ 有浏览器即可     │                     │ 端口：8080        │                     │ 运行客户端       │
└─────────────────┘                     └──────────────────┘                     └─────────────────┘
     ↓                                           ↓                                       ↓
  发送控制指令                              转发数据和事件                           执行控制操作
  显示远程屏幕                              设备管理和认证                           屏幕捕获上传
```

### 数据流向

**控制流程**:
```
控制端 (浏览器)
    ↓ 鼠标/键盘事件
    ↓ WebSocket
中转服务器 (VPS:8080)
    ↓ 转发事件
    ↓ WebSocket
被控端 (Windows Client)
    ↓ 执行控制 (PyAutoGUI)
    ↓ 屏幕截图
    ↓ WebSocket
中转服务器 (VPS:8080)
    ↓ 转发截图
    ↓ WebSocket
控制端 (浏览器)
    ↓ 显示远程屏幕
```

---

## 📋 设备角色说明

### 设备 1: 中转服务器 (Relay Server)

**职责**:
- WebSocket 中继转发
- 设备管理和认证
- 连接状态维护
- 数据加密传输

**要求**:
- 公网 IP
- Linux (Ubuntu/Debian)
- Python 3.8+
- 开放端口：8080

**部署位置**: 公网 VPS（阿里云/腾讯云/AWS 等）

---

### 设备 2: 被控端 (Desktop Client)

**职责**:
- 屏幕捕获和上传
- 接收控制命令
- 执行鼠标键盘操作
- 发送系统信息

**要求**:
- Windows 10/11
- Python 3.8+
- 能访问公网
- 安装 PyAutoGUI

**部署位置**: 你的电脑（被控制的电脑）

---

### 设备 3: 控制端 (Browser Client)

**职责**:
- 显示远程屏幕
- 发送控制指令
- 系统状态监控

**要求**:
- 任何设备（手机/平板/电脑）
- 现代浏览器（Chrome/Edge/Firefox）
- 能访问 VPS

**部署位置**: 任何地方（控制其他设备的设备）

---

## 🚀 快速部署

### 1. 中转服务器部署 (VPS)

```bash
# SSH 登录
ssh root@your-vps-ip

# 克隆项目
cd /opt
git clone git@github.com:CloudSearch1/remoteControl.git
cd remoteControl/relay-server

# 安装依赖
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 配置
cp .env.example .env
nano .env  # 修改密码

# 启动
nohup python server.py > server.log 2>&1 &

# 防火墙
sudo ufw allow 8080/tcp
```

---

### 2. 被控端部署 (Windows)

```powershell
# 克隆项目
cd F:\
git clone git@github.com:CloudSearch1/remoteControl.git
cd remoteControl\desktop-client

# 安装依赖
pip install -r requirements.txt

# 配置
copy .env.example .env
notepad .env
```

**修改 `.env`**:
```bash
SERVER_URL=ws://YOUR-VPS-IP:8080/ws/device
DEVICE_ID=my-home-pc
DEVICE_PASSWORD=your_password
```

**启动**:
```powershell
python client.py
```

---

### 3. 控制端使用 (浏览器)

1. 打开浏览器
2. 访问：`http://YOUR-VPS-IP:8080`
3. 输入设备 ID 和密码
4. 点击"连接"
5. 开始远程控制！

---

## 🔐 安全配置

### 服务器配置
```bash
# .env
SERVER_PASSWORD=VeryStrongPassword123!
HOST=0.0.0.0
PORT=8080
```

### 客户端配置
```bash
# .env
SERVER_URL=ws://123.45.67.89:8080/ws/device
DEVICE_ID=my-home-pc
DEVICE_PASSWORD=VeryStrongPassword123!
```

### 安全建议
1. 使用强密码（12 位以上）
2. 配置 HTTPS（生产环境）
3. 启用设备白名单
4. 定期更新密码
5. 监控连接日志

---

## 📊 性能优化

### 图像质量配置
```bash
# 高质量（局域网）
IMAGE_QUALITY=90
SCREEN_INTERVAL=0.05

# 平衡（互联网）
IMAGE_QUALITY=75
SCREEN_INTERVAL=0.1

# 低质量（慢速网络）
IMAGE_QUALITY=60
SCREEN_INTERVAL=0.2
```

### 服务器优化
```bash
# 使用 Nginx 反向代理
# 启用 WebSocket 压缩
# 限制并发连接数
# 配置连接超时
```

---

## ❓ 故障排查

### 被控端连接失败
1. 检查 VPS 防火墙：`sudo ufw status`
2. 检查 `.env` 配置：`SERVER_URL` 是否正确
3. 检查密码是否一致
4. 查看日志：`tail -f server.log`

### 控制端连接失败
1. 检查 VPS 公网 IP 是否正确
2. 检查服务器是否运行：`ps aux | grep python`
3. 检查防火墙：`sudo ufw allow 8080/tcp`
4. 浏览器控制台查看错误

### 控制延迟高
1. 降低图像质量
2. 增大截图间隔
3. 检查网络带宽
4. 关闭其他占用程序

---

## 📁 项目结构

```
remoteControl/
├── relay-server/          # 中转服务器
│   ├── server.py          # 服务器主程序
│   ├── requirements.txt   # 依赖
│   ├── .env.example      # 配置模板
│   └── start.sh          # 启动脚本
│
├── desktop-client/        # 被控客户端
│   ├── client.py          # 客户端主程序
│   ├── requirements.txt   # 依赖
│   ├── .env.example      # 配置模板
│   └── start.bat         # 启动脚本
│
└── docs/
    ├── ARCHITECTURE.md    # 架构说明（本文件）
    ├── DEPLOYMENT.md      # 部署指南
    └── CONFIG_EXAMPLES.md # 配置示例
```

---

## 🎯 使用场景

### 适用场景
- ✅ 远程技术支持
- ✅ 家庭电脑控制
- ✅ 办公室远程协助
- ✅ 跨地区设备管理
- ✅ 多设备集中控制

### 不适用场景
- ❌ 高帧率游戏（延迟较高）
- ❌ 专业图形工作（色彩精度）
- ❌ 大规模企业部署（需要企业版）

---

## 📈 性能指标

### 局域网
- **延迟**: < 100ms
- **帧率**: 10-20 FPS
- **带宽**: 1-5 Mbps

### 互联网
- **延迟**: 100-500ms
- **帧率**: 5-10 FPS
- **带宽**: 500K-2 Mbps

### 优化建议
1. 使用有线网络
2. 降低图像质量
3. 调整截图间隔
4. 关闭其他占用程序

---

*三设备远程桌面控制系统 - 让远程控制更简单* 🚀
