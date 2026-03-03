# Remote Desktop with Public Relay

基于公网服务器的远程桌面中继系统

## 架构

```
控制端 (浏览器) ←→ 公网服务器 (中继) ←→ 被控端 (你的电脑)
```

## 项目结构

```
remote-desktop/
├── relay-server/          # 公网服务器（中继）
│   ├── server.py          # 中继服务器
│   ├── requirements.txt   # 依赖
│   └── start.sh          # 启动脚本
│
├── desktop-client/        # 被控电脑（客户端）
│   ├── client.py          # 桌面客户端
│   ├── requirements.txt   # 依赖
│   └── start.bat         # 启动脚本
│
└── README.md             # 使用说明
```

---

## 部署步骤

### 1. 公网服务器部署

**服务器要求**:
- 公网 IP
- Linux (Ubuntu/Debian)
- Python 3.8+
- 开放端口：8080

**安装**:
```bash
# SSH 登录服务器
ssh user@your-server-ip

# 克隆项目
git clone https://github.com/your-username/remote-desktop.git
cd remote-desktop/relay-server

# 安装依赖
pip3 install -r requirements.txt

# 配置
cp .env.example .env
vim .env  # 修改配置

# 启动
./start.sh
```

### 2. 被控电脑部署

**Windows 电脑**:
```bash
# 克隆项目
git clone https://github.com/your-username/remote-desktop.git
cd remote-desktop/desktop-client

# 安装依赖
pip install -r requirements.txt

# 配置
copy .env.example .env
notepad .env  # 修改服务器地址

# 启动
start.bat
```

### 3. 控制端访问

**浏览器访问**:
```
http://your-server-ip:8080
```

输入设备 ID 和密码即可控制。

---

## 配置说明

### 服务器配置 (.env)
```bash
# 服务器监听
HOST=0.0.0.0
PORT=8080

# 认证
SERVER_PASSWORD=your_server_password

# 连接超时
TIMEOUT=300
```

### 客户端配置 (.env)
```bash
# 服务器地址
SERVER_URL=ws://your-server-ip:8080

# 设备 ID（自定义）
DEVICE_ID=my-pc-001

# 认证密码
DEVICE_PASSWORD=your_device_password
```

---

## 安全建议

1. **使用 HTTPS** - 配置 SSL 证书
2. **强密码** - 至少 12 位复杂密码
3. **设备白名单** - 只允许特定设备连接
4. **访问日志** - 记录所有连接
5. **速率限制** - 防止暴力破解

---

## 性能优化

### 服务器
- 使用 Nginx 反向代理
- 配置 WebSocket 超时
- 限制并发连接数
- 启用 Gzip 压缩

### 客户端
- 降低图像质量
- 增大截图间隔
- 使用硬件编码

---

## 故障排查

### 连接失败
1. 检查服务器是否运行
2. 检查防火墙设置
3. 检查设备 ID 是否正确
4. 查看服务器日志

### 画面卡顿
1. 降低图像质量
2. 检查网络带宽
3. 减小分辨率
4. 关闭其他占用程序

---

*Remote Desktop with Public Relay*
