"""
公网中继服务器

功能:
- WebSocket 中继转发
- 设备管理
- Web 控制界面
- 连接认证
"""

import os
import json
import asyncio
import logging
from datetime import datetime
from typing import Dict, Optional

from aiohttp import web
import aiohttp
import base64

# 尝试导入 Pillow
try:
    from PIL import Image, ImageGrab
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    print("警告：Pillow 未安装，屏幕捕获功能受限")

# 尝试导入 pyautogui（需要 DISPLAY 环境）
HAS_PYAUTOGUI = False
try:
    import pyautogui
    # 检查是否有 DISPLAY 环境（服务器可能没有）
    if not os.environ.get('DISPLAY'):
        print("提示：无 DISPLAY 环境，鼠标控制功能受限")
    HAS_PYAUTOGUI = True
except (ImportError, KeyError) as e:
    print(f"提示：pyautogui 导入失败：{e}，控制功能受限")
    print("提示：服务器无需控制功能，可忽略此警告")

# 配置
from dotenv import load_dotenv
load_dotenv()

HOST = os.getenv('HOST', '0.0.0.0')
PORT = int(os.getenv('PORT', 8999))
SERVER_PASSWORD = os.getenv('SERVER_PASSWORD', 'relay123')
TIMEOUT = int(os.getenv('TIMEOUT', 300))

# 日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 全局状态
devices: Dict[str, dict] = {}  # 设备连接
clients: Dict[str, dict] = {}  # 控制客户端
device_to_client: Dict[str, str] = {}  # 设备 - 客户端映射


# ============ WebSocket 处理 ============

async def handle_device_websocket(request):
    """处理设备 WebSocket 连接"""
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    
    device_id = None
    
    try:
        async for msg in ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                data = json.loads(msg.data)
                action = data.get('action', '')
                
                # 设备注册
                if action == 'register':
                    device_id = data.get('device_id')
                    password = data.get('password', '')
                    
                    if password != SERVER_PASSWORD:
                        await ws.send_json({'status': 'error', 'message': '认证失败'})
                        continue
                    
                    devices[device_id] = {
                        'ws': ws,
                        'connected_at': datetime.now(),
                        'ip': request.remote
                    }
                    
                    await ws.send_json({
                        'status': 'ok',
                        'message': f'设备 {device_id} 已注册'
                    })
                    
                    logger.info(f"设备注册：{device_id} from {request.remote}")
                
                # 屏幕截图
                elif action == 'screen':
                    if device_id and device_id in device_to_client:
                        client_ws = clients.get(device_to_client[device_id])
                        if client_ws:
                            await client_ws.send_json({'action': 'screen', 'data': data.get('data')})
                
                # 系统信息
                elif action == 'system_info':
                    if device_id and device_id in device_to_client:
                        client_ws = clients.get(device_to_client[device_id])
                        if client_ws:
                            await client_ws.send_json({'action': 'system_info', 'data': data.get('data')})
                
                # 控制响应
                elif action == 'control_response':
                    if device_id and device_id in device_to_client:
                        client_ws = clients.get(device_to_client[device_id])
                        if client_ws:
                            await client_ws.send_json(data)
            
            elif msg.type == aiohttp.WSMsgType.ERROR:
                logger.error(f"设备 {device_id} WebSocket 错误：{ws.exception()}")
    
    finally:
        if device_id and device_id in devices:
            del devices[device_id]
        
        if device_id and device_id in device_to_client:
            client_id = device_to_client[device_id]
            del device_to_client[device_id]
            
            if client_id in clients:
                del clients[client_id]
        
        logger.info(f"设备断开：{device_id}")
    
    return ws


async def handle_client_websocket(request):
    """处理控制客户端 WebSocket 连接"""
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    
    client_id = None
    target_device = None
    
    try:
        async for msg in ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                data = json.loads(msg.data)
                action = data.get('action', '')
                
                # 客户端连接
                if action == 'connect':
                    client_id = data.get('client_id', f'client_{id(ws)}')
                    target_device = data.get('device_id')
                    password = data.get('password', '')
                    
                    if password != SERVER_PASSWORD:
                        await ws.send_json({'status': 'error', 'message': '认证失败'})
                        continue
                    
                    if target_device not in devices:
                        await ws.send_json({
                            'status': 'error',
                            'message': f'设备 {target_device} 不在线'
                        })
                        continue
                    
                    clients[client_id] = {
                        'ws': ws,
                        'connected_at': datetime.now(),
                        'ip': request.remote,
                        'device': target_device
                    }
                    
                    device_to_client[target_device] = client_id
                    
                    await ws.send_json({
                        'status': 'ok',
                        'message': f'已连接到设备 {target_device}'
                    })
                    
                    # 通知设备开始传输
                    device_ws = devices[target_device]['ws']
                    await device_ws.send_json({
                        'action': 'client_connected',
                        'client_id': client_id
                    })
                    
                    logger.info(f"客户端连接：{client_id} -> 设备 {target_device}")
                
                # 控制命令转发
                elif action in ['mouse', 'keyboard']:
                    if target_device and target_device in devices:
                        device_ws = devices[target_device]['ws']
                        await device_ws.send_json(data)
                
                # 请求屏幕
                elif action == 'request_screen':
                    if target_device and target_device in devices:
                        device_ws = devices[target_device]['ws']
                        await device_ws.send_json({'action': 'get_screen'})
                
                # 请求系统信息
                elif action == 'request_system':
                    if target_device and target_device in devices:
                        device_ws = devices[target_device]['ws']
                        await device_ws.send_json({'action': 'get_system_info'})
            
            elif msg.type == aiohttp.WSMsgType.ERROR:
                logger.error(f"客户端 {client_id} WebSocket 错误：{ws.exception()}")
    
    finally:
        if client_id and client_id in clients:
            del clients[client_id]
        
        if target_device and target_device in device_to_client:
            del device_to_client[target_device]
        
        logger.info(f"客户端断开：{client_id}")
    
    return ws


# ============ HTTP 路由 ============

async def handle_index(request):
    """返回控制页面"""
    html = '''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Remote Desktop Control</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Arial, sans-serif; 
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #fff;
            min-height: 100vh;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }
        header {
            text-align: center;
            padding: 30px 0;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            background: linear-gradient(45deg, #00d9ff, #00ff88);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .status {
            color: #888;
            font-size: 0.9em;
        }
        .main-content {
            display: grid;
            grid-template-columns: 300px 1fr;
            gap: 20px;
            margin-top: 30px;
        }
        .sidebar {
            background: rgba(255,255,255,0.05);
            border-radius: 12px;
            padding: 20px;
            backdrop-filter: blur(10px);
        }
        .screen-container {
            background: rgba(0,0,0,0.3);
            border-radius: 12px;
            padding: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 600px;
        }
        #screen {
            max-width: 100%;
            max-height: 600px;
            border-radius: 8px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.5);
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            color: #aaa;
            font-size: 0.9em;
        }
        input, select {
            width: 100%;
            padding: 12px;
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 8px;
            background: rgba(255,255,255,0.05);
            color: #fff;
            font-size: 1em;
        }
        input:focus, select:focus {
            outline: none;
            border-color: #00d9ff;
        }
        button {
            width: 100%;
            padding: 14px;
            border: none;
            border-radius: 8px;
            background: linear-gradient(45deg, #00d9ff, #00ff88);
            color: #1a1a2e;
            font-size: 1em;
            font-weight: bold;
            cursor: pointer;
            transition: transform 0.2s;
        }
        button:hover {
            transform: translateY(-2px);
        }
        button:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        .device-list {
            margin-top: 20px;
        }
        .device-item {
            padding: 12px;
            background: rgba(255,255,255,0.05);
            border-radius: 8px;
            margin-bottom: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .device-status {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: #00ff88;
            display: inline-block;
            margin-right: 10px;
        }
        .info-panel {
            margin-top: 20px;
            padding: 15px;
            background: rgba(255,255,255,0.05);
            border-radius: 8px;
        }
        .info-item {
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid rgba(255,255,255,0.05);
        }
        .info-item:last-child {
            border-bottom: none;
        }
        .progress-bar {
            width: 100%;
            height: 8px;
            background: rgba(255,255,255,0.1);
            border-radius: 4px;
            overflow: hidden;
            margin-top: 5px;
        }
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #00d9ff, #00ff88);
            transition: width 0.3s;
        }
        #log {
            height: 150px;
            overflow-y: auto;
            background: rgba(0,0,0,0.3);
            border-radius: 8px;
            padding: 10px;
            font-family: 'Courier New', monospace;
            font-size: 0.85em;
            margin-top: 20px;
        }
        .log-entry {
            margin-bottom: 5px;
            color: #888;
        }
        .log-entry.error {
            color: #ff4757;
        }
        .log-entry.success {
            color: #00ff88;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🖥️ Remote Desktop Control</h1>
            <p class="status">基于公网中继的远程桌面系统</p>
        </header>
        
        <div class="main-content">
            <div class="sidebar">
                <div class="form-group">
                    <label>服务器密码</label>
                    <input type="password" id="password" placeholder="输入服务器密码" value="relay123">
                </div>
                
                <div class="form-group">
                    <label>设备 ID</label>
                    <input type="text" id="device-id" placeholder="输入设备 ID" value="my-pc-001">
                </div>
                
                <button id="connect-btn" onclick="connectToDevice()">连接设备</button>
                <button id="disconnect-btn" onclick="disconnect()" style="margin-top: 10px; background: linear-gradient(45deg, #ff4757, #ff6b81);" disabled>断开连接</button>
                
                <div class="device-list">
                    <h3 style="margin-bottom: 15px; color: #00d9ff;">在线设备</h3>
                    <div id="devices">
                        <div class="device-item">
                            <div>
                                <span class="device-status"></span>
                                <span id="current-device">my-pc-001</span>
                            </div>
                            <span style="color: #00ff88;">● 在线</span>
                        </div>
                    </div>
                </div>
                
                <div class="info-panel">
                    <h3 style="margin-bottom: 15px; color: #00d9ff;">系统信息</h3>
                    <div class="info-item">
                        <span>CPU 使用率</span>
                        <span id="cpu-value">0%</span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" id="cpu-bar" style="width: 0%"></div>
                    </div>
                    
                    <div class="info-item" style="margin-top: 15px;">
                        <span>内存使用率</span>
                        <span id="memory-value">0%</span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" id="memory-bar" style="width: 0%"></div>
                    </div>
                    
                    <div class="info-item" style="margin-top: 15px;">
                        <span>磁盘使用率</span>
                        <span id="disk-value">0%</span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" id="disk-bar" style="width: 0%"></div>
                    </div>
                </div>
            </div>
            
            <div class="screen-container">
                <img id="screen" src="" alt="Remote Screen">
            </div>
        </div>
        
        <div id="log"></div>
    </div>
    
    <script>
        let ws = null;
        let screenInterval = null;
        let infoInterval = null;
        
        function addLog(message, type = 'info') {
            const log = document.getElementById('log');
            const entry = document.createElement('div');
            entry.className = `log-entry ${type}`;
            entry.textContent = `[${new Date().toLocaleTimeString()}] ${message}`;
            log.appendChild(entry);
            log.scrollTop = log.scrollHeight;
        }
        
        function connectToDevice() {
            const password = document.getElementById('password').value;
            const deviceId = document.getElementById('device-id').value;
            
            if (!password || !deviceId) {
                addLog('请输入密码和设备 ID', 'error');
                return;
            }
            
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${window.location.host}/ws/client`;
            
            ws = new WebSocket(wsUrl);
            
            ws.onopen = () => {
                addLog('WebSocket 连接已建立', 'success');
                ws.send(JSON.stringify({
                    action: 'connect',
                    client_id: 'web-client-' + Date.now(),
                    device_id: deviceId,
                    password: password
                }));
            };
            
            ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                
                if (data.status === 'ok') {
                    addLog(data.message, 'success');
                    document.getElementById('connect-btn').disabled = true;
                    document.getElementById('disconnect-btn').disabled = false;
                    
                    // 开始刷新屏幕和系统信息
                    screenInterval = setInterval(() => {
                        if (ws && ws.readyState === WebSocket.OPEN) {
                            ws.send(JSON.stringify({action: 'request_screen'}));
                        }
                    }, 100);
                    
                    infoInterval = setInterval(() => {
                        if (ws && ws.readyState === WebSocket.OPEN) {
                            ws.send(JSON.stringify({action: 'request_system'}));
                        }
                    }, 1000);
                } else if (data.status === 'error') {
                    addLog(data.message, 'error');
                } else if (data.action === 'screen' && data.data) {
                    document.getElementById('screen').src = 'data:image/jpeg;base64,' + data.data;
                } else if (data.action === 'system_info' && data.data) {
                    updateSystemInfo(data.data);
                }
            };
            
            ws.onerror = (error) => {
                addLog('WebSocket 错误：' + error, 'error');
            };
            
            ws.onclose = () => {
                addLog('连接已断开', 'error');
                disconnect();
            };
        }
        
        function disconnect() {
            if (ws) {
                ws.close();
                ws = null;
            }
            
            clearInterval(screenInterval);
            clearInterval(infoInterval);
            
            document.getElementById('connect-btn').disabled = false;
            document.getElementById('disconnect-btn').disabled = true;
            document.getElementById('screen').src = '';
            
            addLog('已断开连接');
        }
        
        function updateSystemInfo(info) {
            if (info.cpu !== undefined) {
                document.getElementById('cpu-value').textContent = info.cpu + '%';
                document.getElementById('cpu-bar').style.width = info.cpu + '%';
            }
            if (info.memory !== undefined) {
                document.getElementById('memory-value').textContent = info.memory + '%';
                document.getElementById('memory-bar').style.width = info.memory + '%';
            }
            if (info.disk !== undefined) {
                document.getElementById('disk-value').textContent = info.disk + '%';
                document.getElementById('disk-bar').style.width = info.disk + '%';
            }
        }
        
        // 鼠标控制
        const screen = document.getElementById('screen');
        
        screen.addEventListener('mousemove', (e) => {
            if (!ws || ws.readyState !== WebSocket.OPEN) return;
            
            const rect = screen.getBoundingClientRect();
            const x = Math.round((e.clientX - rect.left) / rect.width * screen.naturalWidth);
            const y = Math.round((e.clientY - rect.top) / rect.height * screen.naturalHeight);
            
            ws.send(JSON.stringify({
                action: 'mouse',
                type: 'move',
                x: x,
                y: y
            }));
        });
        
        screen.addEventListener('click', (e) => {
            if (!ws || ws.readyState !== WebSocket.OPEN) return;
            
            const rect = screen.getBoundingClientRect();
            const x = Math.round((e.clientX - rect.left) / rect.width * screen.naturalWidth);
            const y = Math.round((e.clientY - rect.top) / rect.height * screen.naturalHeight);
            
            ws.send(JSON.stringify({
                action: 'mouse',
                type: 'click',
                x: x,
                y: y,
                button: e.button === 2 ? 'right' : 'left'
            }));
        });
        
        screen.addEventListener('contextmenu', (e) => e.preventDefault());
        
        // 键盘控制
        document.addEventListener('keydown', (e) => {
            if (!ws || ws.readyState !== WebSocket.OPEN) return;
            
            ws.send(JSON.stringify({
                action: 'keyboard',
                key: e.key,
                text: e.key
            }));
        });
        
        addLog('页面已加载，请输入设备 ID 和密码进行连接');
    </script>
</body>
</html>'''
    
    return web.Response(text=html, content_type='text/html')


async def handle_health(request):
    """健康检查"""
    return web.json_response({
        'status': 'healthy',
        'devices': len(devices),
        'clients': len(clients),
        'timestamp': datetime.now().isoformat()
    })


async def handle_devices(request):
    """获取设备列表"""
    device_list = []
    for device_id, info in devices.items():
        device_list.append({
            'id': device_id,
            'ip': info['ip'],
            'connected_at': info['connected_at'].isoformat()
        })
    
    return web.json_response({'devices': device_list})


# ============ 应用配置 ============

def create_app():
    """创建应用"""
    app = web.Application()
    
    # 路由
    app.router.add_get('/', handle_index)
    app.router.add_get('/health', handle_health)
    app.router.add_get('/devices', handle_devices)
    app.router.add_get('/ws/device', handle_device_websocket)
    app.router.add_get('/ws/client', handle_client_websocket)
    
    return app


# ============ 主函数 ============

def main():
    """主函数"""
    print("=" * 60)
    print("  Remote Desktop Relay Server")
    print("=" * 60)
    print()
    print(f"  监听地址：{HOST}:{PORT}")
    print(f"  服务器密码：{SERVER_PASSWORD}")
    print()
    print("  访问地址:")
    print(f"    http://localhost:{PORT}")
    print()
    print("=" * 60)
    print("  等待连接...")
    print("=" * 60)
    print()
    
    app = create_app()
    web.run_app(app, host=HOST, port=PORT, print=lambda x: None)


if __name__ == '__main__':
    main()
