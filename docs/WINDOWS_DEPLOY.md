# Windows 部署脚本

> **Windows 系统一键部署脚本**

---

## 📋 目录

1. [中转服务器部署脚本](#1-中转服务器部署脚本)
2. [被控端部署脚本](#2-被控端部署脚本)
3. [使用说明](#3-使用说明)

---

## 1. 中转服务器部署脚本

**文件**: `relay-server/deploy.bat`

**用途**: 在 Windows 服务器上部署中转服务器

**运行方式**:
1. 右键点击 `deploy.bat`
2. 选择 **"以管理员身份运行"**
3. 按提示完成配置

**功能**:
- ✅ 检查 Python 安装
- ✅ 创建虚拟环境
- ✅ 安装依赖
- ✅ 创建配置文件
- ✅ 启动服务器
- ✅ 自动打开浏览器

**配置**:
```bash
# 编辑 .env 文件
SERVER_PASSWORD=your_password
HOST=0.0.0.0
PORT=8080
```

**访问**:
```
http://localhost:8080
```

---

## 2. 被控端部署脚本

**文件**: `desktop-client/deploy.bat`

**用途**: 在 Windows 电脑上部署被控端

**运行方式**:
1. 双击运行 `deploy.bat`
2. 按提示修改配置
3. 客户端自动启动

**功能**:
- ✅ 检查 Python 安装
- ✅ 安装依赖
- ✅ 创建配置文件
- ✅ 启动客户端

**配置**:
```bash
# 编辑 .env 文件
SERVER_URL=ws://YOUR-VPS-IP:8080/ws/device
DEVICE_ID=my-home-pc
DEVICE_PASSWORD=your_password
```

**验证**:
- 客户端窗口显示 `✅ 设备已注册`

---

## 3. 使用说明

### 中转服务器部署

**步骤**:
1. 下载项目
2. 进入 `relay-server` 目录
3. 右键运行 `deploy.bat`（管理员）
4. 修改密码
5. 完成！

**防火墙配置**:
```bash
# Windows 防火墙
netsh advfirewall firewall add rule name="Remote Desktop" dir=in action=allow protocol=TCP localport=8080
```

**VPS 防火墙**:
- 阿里云/腾讯云：控制台安全组开放 8080
- 其他：参考云服务商文档

---

### 被控端部署

**步骤**:
1. 下载项目
2. 进入 `desktop-client` 目录
3. 运行 `deploy.bat`
4. 修改 `.env` 配置：
   - `SERVER_URL`: VPS 公网 IP
   - `DEVICE_ID`: 自定义设备 ID
   - `DEVICE_PASSWORD`: 与服务器一致
5. 完成！

---

### 控制端使用

**步骤**:
1. 打开浏览器
2. 访问：`http://VPS-IP:8080`
3. 输入设备 ID 和密码
4. 点击"连接"
5. 开始远程控制！

---

## 🔧 故障排查

### 中转服务器无法启动

**检查**:
1. Python 是否安装
2. 端口 8080 是否被占用
3. 防火墙是否开放

**解决**:
```bash
# 检查端口
netstat -ano | findstr :8080

# 手动启动
cd relay-server
venv\Scripts\activate
python server.py
```

### 被控端连接失败

**检查**:
1. `SERVER_URL` 是否正确
2. VPS 防火墙是否开放
3. 密码是否一致

**解决**:
```bash
# 测试连接
telnet VPS-IP 8080

# 查看日志
# 客户端窗口会显示错误信息
```

### 控制端无法访问

**检查**:
1. VPS 公网 IP 是否正确
2. 服务器是否运行
3. 浏览器是否能访问

**解决**:
```bash
# 检查服务器状态
# 访问 http://VPS-IP:8080/health
# 应该返回 {"status": "healthy"}
```

---

## 📊 部署检查清单

### 中转服务器
- [ ] Python 3.8+ 已安装
- [ ] 以管理员身份运行 deploy.bat
- [ ] 修改了默认密码
- [ ] 防火墙开放 8080
- [ ] 能访问 http://localhost:8080

### 被控端
- [ ] Python 3.8+ 已安装
- [ ] 运行 deploy.bat
- [ ] 修改 SERVER_URL 为 VPS IP
- [ ] 修改 DEVICE_ID
- [ ] 密码与服务器一致
- [ ] 客户端显示"设备已注册"

### 控制端
- [ ] 记录 VPS 公网 IP
- [ ] 记录设备 ID
- [ ] 记录密码
- [ ] 浏览器能访问 VPS

---

## 🚀 快速部署命令

### 中转服务器（手动）

```batch
cd relay-server
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
notepad .env
python server.py
```

### 被控端（手动）

```batch
cd desktop-client
pip install -r requirements.txt
copy .env.example .env
notepad .env
python client.py
```

---

## 📝 配置示例

### 中转服务器 .env

```bash
# 服务器配置
HOST=0.0.0.0
PORT=8080

# 认证密码
SERVER_PASSWORD=MySecurePassword123!

# 连接超时
TIMEOUT=300

# 日志级别
LOG_LEVEL=INFO
```

### 被控端 .env

```bash
# 服务器地址（修改为 VPS IP）
SERVER_URL=ws://123.45.67.89:8080/ws/device

# 设备 ID
DEVICE_ID=home-pc-001

# 认证密码
DEVICE_PASSWORD=MySecurePassword123!

# 图像质量
IMAGE_QUALITY=75

# 截图间隔
SCREEN_INTERVAL=0.1
```

---

*Windows 部署脚本 - 让部署更简单* 🚀
