"""
远程桌面服务器端

功能:
- 屏幕捕获和传输
- 接收鼠标键盘控制
- 文件传输
- 系统监控
"""

import os
import io
import time
import socket
import logging
from datetime import datetime
from threading import Lock

import pyautogui
import psutil
from PIL import Image
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit, disconnect
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建 Flask 应用
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SERVER_PASSWORD', 'secret')
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# 配置
SERVER_HOST = os.getenv('SERVER_HOST', '0.0.0.0')
SERVER_PORT = int(os.getenv('SERVER_PORT', 5000))
SERVER_PASSWORD = os.getenv('SERVER_PASSWORD', 'remote123')
IMAGE_QUALITY = int(os.getenv('IMAGE_QUALITY', 80))
CAPTURE_INTERVAL = float(os.getenv('SCREEN_CAPTURE_INTERVAL', 0.1))

# 全局状态
connected_clients = {}
client_lock = Lock()
is_capturing = False


def get_screen_capture():
    """获取屏幕截图"""
    try:
        screenshot = pyautogui.screenshot()
        img_io = io.BytesIO()
        screenshot.save(img_io, 'JPEG', quality=IMAGE_QUALITY)
        img_io.seek(0)
        return img_io.getvalue()
    except Exception as e:
        logger.error(f"截图失败：{e}")
        return None


def get_system_info():
    """获取系统信息"""
    try:
        return {
            'cpu': psutil.cpu_percent(interval=1),
            'memory': psutil.virtual_memory().percent,
            'disk': psutil.disk_usage('/').percent,
            'network': {
                'upload': psutil.net_io_counters().bytes_sent,
                'download': psutil.net_io_counters().bytes_recv,
            }
        }
    except Exception as e:
        logger.error(f"获取系统信息失败：{e}")
        return None


@socketio.on('connect')
def handle_connect():
    """处理客户端连接"""
    logger.info(f"客户端连接：{request.sid}")


@socketio.on('disconnect')
def handle_disconnect():
    """处理客户端断开"""
    logger.info(f"客户端断开：{request.sid}")
    with client_lock:
        if request.sid in connected_clients:
            del connected_clients[request.sid]


@socketio.on('auth')
def handle_auth(data):
    """处理认证"""
    password = data.get('password', '')
    
    if password == SERVER_PASSWORD:
        with client_lock:
            connected_clients[request.sid] = {
                'connected_at': datetime.now(),
                'ip': request.remote_addr
            }
        
        emit('auth_success', {'status': 'ok'})
        logger.info(f"认证成功：{request.sid}")
    else:
        emit('auth_error', {'status': 'invalid_password'})
        disconnect()
        logger.warning(f"认证失败：{request.sid}")


@socketio.on('request_screen')
def handle_screen_request():
    """处理屏幕请求"""
    global is_capturing
    
    if request.sid not in connected_clients:
        emit('error', {'message': '未认证'})
        return
    
    if is_capturing:
        return
    
    is_capturing = True
    
    try:
        screen_data = get_screen_capture()
        if screen_data:
            import base64
            screen_base64 = base64.b64encode(screen_data).decode('utf-8')
            emit('screen_data', {
                'image': screen_base64,
                'timestamp': time.time()
            })
    except Exception as e:
        logger.error(f"发送屏幕失败：{e}")
        emit('error', {'message': str(e)})
    finally:
        is_capturing = False


@socketio.on('mouse_event')
def handle_mouse_event(data):
    """处理鼠标事件"""
    if request.sid not in connected_clients:
        return
    
    try:
        action = data.get('action')
        x = data.get('x', 0)
        y = data.get('y', 0)
        button = data.get('button', 'left')
        
        if action == 'move':
            pyautogui.moveTo(x, y, duration=0.1)
        elif action == 'click':
            pyautogui.click(x, y, button=button)
        elif action == 'double_click':
            pyautogui.doubleClick(x, y, button=button)
        elif action == 'scroll':
            amount = data.get('amount', 0)
            pyautogui.scroll(amount, x, y)
        
        logger.debug(f"鼠标事件：{action} ({x}, {y})")
    except Exception as e:
        logger.error(f"鼠标控制失败：{e}")


@socketio.on('keyboard_event')
def handle_keyboard_event(data):
    """处理键盘事件"""
    if request.sid not in connected_clients:
        return
    
    try:
        key = data.get('key', '')
        
        if key:
            pyautogui.write(key, interval=0.05)
            logger.debug(f"键盘输入：{key}")
    except Exception as e:
        logger.error(f"键盘控制失败：{e}")


@socketio.on('get_system_info')
def handle_system_info_request():
    """处理系统信息请求"""
    if request.sid not in connected_clients:
        return
    
    try:
        info = get_system_info()
        if info:
            emit('system_info', info)
    except Exception as e:
        logger.error(f"发送系统信息失败：{e}")


@app.route('/')
def index():
    """服务器状态页面"""
    return jsonify({
        'status': 'running',
        'clients': len(connected_clients),
        'server': f'{SERVER_HOST}:{SERVER_PORT}'
    })


@app.route('/health')
def health():
    """健康检查"""
    return jsonify({'status': 'healthy'})


def start_screen_capture():
    """开始屏幕捕获循环"""
    while True:
        time.sleep(CAPTURE_INTERVAL)
        if connected_clients:
            with client_lock:
                clients = list(connected_clients.keys())
            
            for client_sid in clients:
                socketio.emit('request_screen', to=client_sid)


if __name__ == '__main__':
    logger.info("=" * 60)
    logger.info("  Remote Desktop Server")
    logger.info("=" * 60)
    logger.info(f"  监听地址：{SERVER_HOST}:{SERVER_PORT}")
    logger.info(f"  图像质量：{IMAGE_QUALITY}%")
    logger.info(f"  截图间隔：{CAPTURE_INTERVAL}s")
    logger.info("=" * 60)
    
    # 获取本地 IP
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    logger.info(f"  本地 IP: {local_ip}")
    logger.info("")
    logger.info("等待客户端连接...")
    
    # 启动服务器
    socketio.run(app, host=SERVER_HOST, port=SERVER_PORT, debug=False)
