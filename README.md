# Remote Desktop Control - 远程桌面控制系统

<div align="center">

**基于 Python 的远程桌面控制系统**

支持图像捕获、远程控制、文件传输

</div>

---

## 🎯 项目简介

这是一个完整的远程桌面控制系统，包含：
- **服务器端** - 部署在被控电脑上
- **客户端** - 部署在控制电脑上

### 核心功能

- 🖥️ **实时屏幕捕获** - 高效截图传输
- 🖱️ **远程鼠标控制** - 鼠标移动、点击
- ⌨️ **远程键盘输入** - 键盘事件同步
- 📁 **文件传输** - 上传下载文件
- 🔒 **安全连接** - 加密通信
- 📊 **性能监控** - 实时状态显示

---

## 🚀 快速开始

### 服务器端（被控电脑）

```bash
# 1. 安装依赖
pip install -r requirements-server.txt

# 2. 配置服务器
copy .env.example .env
# 编辑 .env 文件

# 3. 启动服务器
python server.py
```

### 客户端（控制电脑）

```bash
# 1. 安装依赖
pip install -r requirements-client.txt

# 2. 启动客户端
python client.py
```

---

## 📋 功能特性

### 屏幕控制
- [x] 实时屏幕截图
- [x] 屏幕区域选择
- [x] 多显示器支持
- [x] 画质调节

### 鼠标控制
- [x] 鼠标移动
- [x] 左键点击
- [x] 右键点击
- [x] 双击
- [x] 滚轮

### 键盘控制
- [x] 键盘输入
- [x] 组合键
- [x] 特殊按键

### 文件管理
- [x] 文件列表
- [x] 文件上传
- [x] 文件下载
- [x] 文件删除

### 系统信息
- [x] CPU 使用率
- [x] 内存使用率
- [x] 磁盘空间
- [x] 网络状态

---

## 🔧 技术栈

### 服务器端
- **Python 3.11+**
- **Flask** - Web 服务器
- **SocketIO** - 实时通信
- **Pillow** - 图像处理
- **pyautogui** - 鼠标键盘控制
- **psutil** - 系统监控

### 客户端
- **Python 3.11+**
- **PyQt5** - 图形界面
- **SocketIO** - 实时通信
- **Pillow** - 图像处理

---

## 📁 项目结构

```
remote-desktop/
├── server/                 # 服务器端
│   ├── server.py          # 主程序
│   ├── handlers.py        # 事件处理
│   ├── screen.py          # 屏幕捕获
│   └── utils.py           # 工具函数
├── client/                 # 客户端
│   ├── client.py          # 主程序
│   ├── ui.py              # 界面
│   └── controller.py      # 控制器
├── requirements-server.txt # 服务器依赖
├── requirements-client.txt # 客户端依赖
├── .env.example           # 配置模板
└── README.md              # 项目说明
```

---

## 🔐 安全配置

### 环境变量

```bash
# 服务器配置
SERVER_HOST=0.0.0.0
SERVER_PORT=5000
SERVER_PASSWORD=your_password

# 客户端配置
SERVER_URL=http://server_ip:5000
CLIENT_PASSWORD=your_password
```

### 安全特性

- ✅ 密码认证
- ✅ 连接加密
- ✅ IP 白名单
- ✅ 会话超时

---

## 📊 性能优化

### 图像传输
- JPEG 压缩（可调节质量）
- 差异传输（只传变化区域）
- 多线程处理

### 网络优化
- WebSocket 长连接
- 心跳检测
- 断线重连

---

## 🎮 使用说明

### 连接服务器

1. 启动服务器端
2. 记录服务器 IP 和端口
3. 客户端输入服务器地址
4. 输入密码连接

### 远程控制

- **鼠标**: 移动和点击同步到远程电脑
- **键盘**: 输入同步到远程电脑
- **文件**: 拖拽上传下载

---

## ❓ 常见问题

### Q: 连接失败？
检查防火墙设置，确保端口开放。

### Q: 画面卡顿？
降低图像质量或减小分辨率。

### Q: 控制延迟？
确保网络连接稳定。

---

## 📄 许可证

MIT License

---

*Remote Desktop Control - 让远程控制更简单*
