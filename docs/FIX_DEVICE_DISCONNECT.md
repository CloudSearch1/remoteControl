# 设备不断断开修复指南

## 问题
设备 `my-home-pc` 不断注册然后断开，每 5 秒一次循环

## 根本原因
服务器代码中设备注册后：
1. 没有心跳保持连接机制
2. 如果没有收到消息，WebSocket 连接会超时断开
3. 客户端检测到断开后立即重连

## 解决方案

### 方案 1: 服务器添加心跳响应（已修复）

在 `server.py` 中添加 ping/pong 处理：

```python
# 心跳响应
elif action == 'ping':
    await ws.send_json({'action': 'pong'})
```

### 方案 2: 客户端添加心跳发送

在 `client.py` 中添加心跳循环：

```python
async def heartbeat_loop():
    """心跳循环"""
    while True:
        try:
            if ws and client_connected:
                await ws.send_json({'action': 'ping'})
            await asyncio.sleep(20)  # 每 20 秒发送一次心跳
        except Exception as e:
            logger.error(f"心跳失败：{e}")
            await asyncio.sleep(5)
```

### 方案 3: 增加 WebSocket 超时时间

在服务器启动时配置：

```python
# 增加 WebSocket 超时
ws = web.WebSocketResponse(
    receive_timeout=60,  # 60 秒超时
    heartbeat=30  # 30 秒心跳
)
```

## 修复后重启服务器

```bash
# SSH 登录
ssh root@43.136.51.75

# 进入目录
cd /opt/remoteControl/relay-server

# 激活虚拟环境
source venv/bin/activate

# 停止旧服务
pkill -f "python.*server.py" || true
sleep 2

# 启动新服务
nohup python server.py > server.log 2>&1 &

# 查看日志
tail -f server.log
```

## 验证

客户端日志应该显示：
- ✅ 设备注册一次后保持连接
- ✅ 不再频繁重连
- ✅ 浏览器能看到设备在线

---

*设备断开修复指南* 🚀
