# Ubuntu VPS 重新部署指南

> **修复导入错误和端口问题**

---

## 🚨 问题说明

服务器上的代码是旧版本，还包含已修复的错误：
- ❌ `from aiohttp import web_socket` (已删除)
- ❌ 端口 8080 (已改为 8999)

---

## ✅ 解决方案

### 方法 1: 完整重新部署（推荐）

```bash
# SSH 登录
ssh root@your-vps-ip

# 删除旧项目
rm -rf /opt/remoteControl

# 重新克隆
cd /opt
git clone git@github.com:CloudSearch1/remoteControl.git
cd remoteControl/relay-server

# 重新部署
sudo ./deploy.sh
```

### 方法 2: 更新现有部署

```bash
# SSH 登录
ssh root@your-vps-ip

# 进入项目目录
cd /opt/remoteControl/relay-server

# 停止旧服务
pkill -f "python server.py"

# 拉取最新代码
git fetch --all
git reset --hard origin/main

# 重新安装依赖
source venv/bin/activate
pip install -r requirements.txt

# 修改端口（如果 .env 已存在）
sed -i 's/PORT=8080/PORT=8999/' .env

# 重新配置防火墙
ufw allow 8999/tcp

# 启动服务
nohup python server.py > server.log 2>&1 &

# 检查日志
tail -f server.log
```

---

## 🔍 验证部署

```bash
# 1. 检查服务进程
ps aux | grep python

# 2. 检查端口
netstat -tlnp | grep 8999

# 3. 检查日志
tail -f server.log

# 4. 测试访问
curl http://localhost:8999/health
```

**成功标志**:
- 日志显示 "等待连接..."
- 端口 8999 已监听
- curl 返回 `{"status": "healthy"}`

---

## 📋 完整部署流程

### 1. SSH 登录
```bash
ssh root@your-vps-ip
```

### 2. 删除旧版本
```bash
rm -rf /opt/remoteControl
```

### 3. 克隆新项目
```bash
cd /opt
git clone git@github.com:CloudSearch1/remoteControl.git
cd remoteControl/relay-server
```

### 4. 运行部署脚本
```bash
sudo ./deploy.sh
```

### 5. 验证
```bash
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

### 6. 访问
```
http://VPS-IP:8999
```

---

## ❓ 常见问题

### Q: git pull 后还是旧代码？
**A**: 使用强制更新：
```bash
git fetch --all
git reset --hard origin/main
```

### Q: 服务启动失败？
**A**: 检查日志：
```bash
tail -f server.log
```

常见错误：
- 端口被占用：`netstat -tlnp | grep 8999`
- 依赖缺失：`pip install -r requirements.txt`
- 权限问题：使用 `sudo`

### Q: 无法访问？
**A**: 检查防火墙：
```bash
sudo ufw status
sudo ufw allow 8999/tcp
```

---

## 📊 检查清单

- [ ] 已删除旧项目 `/opt/remoteControl`
- [ ] 已重新克隆最新代码
- [ ] 部署脚本运行成功
- [ ] 服务进程运行中
- [ ] 端口 8999 已监听
- [ ] 日志显示"等待连接..."
- [ ] 防火墙开放 8999
- [ ] 能访问 http://VPS-IP:8999

---

*重新部署指南 - 确保使用最新代码* 🚀
