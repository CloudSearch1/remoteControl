# SSH 登录 VPS
ssh root@43.136.51.75

# 查看服务器运行的设备列表
curl http://localhost:8999/devices

# 查看服务器完整日志
tail -100 /opt/remoteControl/relay-server/server.log

# 重启服务器
cd /opt/remoteControl/relay-server
pkill -f "python server.py"
sleep 2
nohup python server.py > server.log 2>&1 &

# 查看新日志
tail -f server.log

# 再次查看设备列表（应该能看到 my-home-pc）
curl http://localhost:8999/devices
