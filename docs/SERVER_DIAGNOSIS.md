# VPS 服务器诊断和修复

## 问题诊断

客户端日志显示：
1. `WinError 1225 远程计算机拒绝网络连接` - 服务器未运行或防火墙问题
2. `did not receive a valid HTTP response` - 服务器响应异常

## 完整诊断步骤

### 1. SSH 登录 VPS
```bash
ssh root@43.136.51.75
```

### 2. 检查服务器进程
```bash
# 查看 python 进程
ps aux | grep python

# 应该看到 relay-server 的进程
# 如果没有，说明服务器没运行
```

### 3. 检查端口监听
```bash
# 查看 8999 端口
netstat -tlnp | grep 8999

# 应该看到：
# tcp  0.0.0.0:8999  LISTEN  XXXXX/python
```

### 4. 检查防火墙
```bash
# 查看防火墙状态
ufw status

# 应该看到 8999 端口开放
# 如果没有，执行：
ufw allow 8999/tcp
```

### 5. 检查服务器日志
```bash
cd /opt/remoteControl/relay-server
tail -100 server.log

# 应该看到启动信息
# 如果看到错误，根据错误修复
```

### 6. 测试本地访问
```bash
# 测试 HTTP 访问
curl http://localhost:8999/health

# 应该返回：
# {"status":"healthy"}
```

## 完整修复流程

### 方案 1: 重启服务器（推荐）

```bash
# SSH 登录
ssh root@43.136.51.75

# 进入目录
cd /opt/remoteControl/relay-server

# 停止旧进程
pkill -f "python.*server.py" || true
sleep 2

# 激活虚拟环境
source venv/bin/activate

# 确保依赖已安装
pip install -r requirements.txt

# 启动服务
nohup python server.py > server.log 2>&1 &

# 查看日志
tail -f server.log

# 应该看到：
# ========================================
#   Remote Desktop Relay Server
# ========================================
#   监听地址：0.0.0.0:8999
#   ...
#   等待连接...
```

### 方案 2: 完全重新部署

```bash
# SSH 登录
ssh root@43.136.51.75

# 删除旧项目
rm -rf /opt/remoteControl

# 重新克隆
cd /opt
git clone git@github.com:CloudSearch1/remoteControl.git
cd remoteControl/relay-server

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 启动服务
pkill -f "python.*server.py" || true
nohup python server.py > server.log 2>&1 &

# 查看日志
tail -f server.log
```

### 方案 3: 检查网络问题

```bash
# SSH 登录
ssh root@43.136.51.75

# 测试外网连接
ping -c 4 github.com

# 如果不能 ping 通，检查网络
# 可能需要重启网络服务
systemctl restart networking

# 或者重启服务器
reboot
```

## 验证成功

```bash
# 1. 检查进程
ps aux | grep python
# 应该看到 python server.py

# 2. 检查端口
netstat -tlnp | grep 8999
# 应该看到 0.0.0.0:8999 LISTEN

# 3. 测试访问
curl http://localhost:8999/health
# 应该返回 {"status":"healthy"}

# 4. 查看设备列表
curl http://localhost:8999/devices
# 应该返回设备列表（可能为空）

# 5. 查看日志
tail -f server.log
# 应该看到设备连接日志
```

## 常见问题

### Q: 虚拟环境不存在？
**A**: 重新创建
```bash
cd /opt/remoteControl/relay-server
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Q: pip 命令不存在？
**A**: 使用 pip3
```bash
pip3 install -r requirements.txt
```

### Q: 端口被占用？
**A**: 查找并停止占用进程
```bash
lsof -i :8999
kill -9 <PID>
```

### Q: 日志显示地址已使用？
**A**: 等待几秒或重启服务器
```bash
pkill -f "python.*server.py"
sleep 5
nohup python server.py > server.log 2>&1 &
```

## 成功后

客户端应该：
- ✅ 不再显示连接错误
- ✅ 保持持续连接
- ✅ 浏览器能看到设备在线

---

*完整诊断和修复指南* 🚀
