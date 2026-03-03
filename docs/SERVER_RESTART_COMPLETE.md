# VPS 服务器完整重启指南

## 问题
1. 没有 `python` 命令 → 使用 `python3`
2. 缺少 `aiohttp` 模块 → 需要激活虚拟环境或重新安装依赖

## 完整解决方案

### 方法 1: 使用虚拟环境（推荐）

```bash
# SSH 登录
ssh root@43.136.51.75

# 进入项目目录
cd /opt/remoteControl/relay-server

# 激活虚拟环境
source venv/bin/activate

# 停止旧服务
pkill -f "python.*server.py" || true

# 安装/更新依赖
pip install -r requirements.txt

# 启动服务
nohup python server.py > server.log 2>&1 &

# 查看日志
tail -f server.log

# 查看进程
ps aux | grep python

# 查看端口
netstat -tlnp | grep 8999
```

### 方法 2: 全局安装依赖（不推荐）

```bash
# SSH 登录
ssh root@43.136.51.75

# 全局安装依赖
pip3 install aiohttp websockets python-dotenv psutil Pillow pyautogui

# 启动服务
cd /opt/remoteControl/relay-server
nohup python3 server.py > server.log 2>&1 &

# 查看日志
tail -f server.log
```

### 方法 3: 重新部署（最干净）

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

## 验证成功

```bash
# 检查进程
ps aux | grep python

# 应该看到：
# root  XXXXX  python server.py

# 检查端口
netstat -tlnp | grep 8999

# 应该看到：
# tcp  0.0.0.0:8999  LISTEN  XXXXX/python

# 检查日志
tail -f server.log

# 应该看到：
# ========================================
#   Remote Desktop Relay Server
# ========================================
#   监听地址：0.0.0.0:8999
#   ...
#   等待连接...

# 测试访问
curl http://localhost:8999/health

# 应该返回：
# {"status":"healthy"}
```

## 快速命令（推荐）

```bash
ssh root@43.136.51.75
cd /opt/remoteControl/relay-server
source venv/bin/activate
pkill -f "python.*server.py" || true
pip install -r requirements.txt
nohup python server.py > server.log 2>&1 &
tail -f server.log
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
**A**: 停止旧进程
```bash
pkill -f "python.*server.py"
sleep 2
nohup python server.py > server.log 2>&1 &
```

## 成功后

1. 浏览器访问：`http://43.136.51.75:8999`
2. 按 **Ctrl+F5** 强制刷新
3. 输入设备 ID: `my-home-pc`
4. 输入密码：`Zhangshuo2001`
5. 点击"连接"

---

*完整重启指南 - 确保所有依赖正确安装* 🚀
