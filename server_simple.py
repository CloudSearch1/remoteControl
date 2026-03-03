"""
超简单远程桌面 - 服务器端

使用纯 Python 标准库 + 基础 HTTP
无需复杂依赖！
"""

import os
import io
import base64
import json
import time
import socket
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import parse_qs
import subprocess

# 尝试导入，如果失败使用替代方案
try:
    import pyautogui
    HAS_PYAUTOGUI = True
except:
    HAS_PYAUTOGUI = False
    print("警告：pyautogui 未安装，鼠标键盘控制将不可用")

try:
    from PIL import Image, ImageGrab
    HAS_PIL = True
except:
    HAS_PIL = False
    print("警告：Pillow 未安装，屏幕捕获将使用替代方案")

# 配置
HOST = '0.0.0.0'
PORT = 5000
PASSWORD = 'remote123'

# 全局状态
clients = {}
screen_cache = None


def get_screen_base64():
    """获取屏幕截图（Base64）"""
    global screen_cache
    
    if HAS_PIL:
        try:
            screenshot = ImageGrab.grab()
            img_io = io.BytesIO()
            screenshot.save(img_io, 'JPEG', quality=75)
            img_io.seek(0)
            screen_cache = base64.b64encode(img_io.read()).decode('utf-8')
            return screen_cache
        except Exception as e:
            print(f"截图失败：{e}")
    
    # 替代方案：返回占位图
    return None


def control_mouse(action, x, y, button='left'):
    """控制鼠标"""
    if not HAS_PYAUTOGUI:
        return False
    
    try:
        if action == 'move':
            pyautogui.moveTo(x, y)
        elif action == 'click':
            pyautogui.click(x, y, button=button)
        return True
    except Exception as e:
        print(f"鼠标控制失败：{e}")
        return False


def control_keyboard(text):
    """控制键盘"""
    if not HAS_PYAUTOGUI:
        return False
    
    try:
        pyautogui.write(text, interval=0.05)
        return True
    except Exception as e:
        print(f"键盘控制失败：{e}")
        return False


def get_system_info():
    """获取系统信息"""
    try:
        import psutil
        return {
            'cpu': psutil.cpu_percent(interval=1),
            'memory': psutil.virtual_memory().percent,
            'disk': psutil.disk_usage('C:').percent,
        }
    except:
        return {'cpu': 0, 'memory': 0, 'disk': 0}


class RemoteHandler(SimpleHTTPRequestHandler):
    """HTTP 请求处理器"""
    
    def do_GET(self):
        """处理 GET 请求"""
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            # 返回控制页面
            html = self.get_control_page()
            self.wfile.write(html.encode())
        
        elif self.path.startswith('/screen'):
            # 返回屏幕截图
            screen_data = get_screen_base64()
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = json.dumps({'screen': screen_data})
            self.wfile.write(response.encode())
        
        elif self.path.startswith('/system'):
            # 返回系统信息
            info = get_system_info()
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = json.dumps(info)
            self.wfile.write(response.encode())
        
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        """处理 POST 请求"""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data.decode())
            action = data.get('action', '')
            
            # 认证
            if data.get('password', '') != PASSWORD:
                self.send_response(401)
                self.end_headers()
                return
            
            # 执行操作
            if action == 'mouse':
                x = data.get('x', 0)
                y = data.get('y', 0)
                button = data.get('button', 'left')
                control_mouse(data.get('type', 'click'), x, y, button)
            
            elif action == 'keyboard':
                control_keyboard(data.get('text', ''))
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"status": "ok"}')
        
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            print(f"处理请求失败：{e}")
    
    def get_control_page(self):
        """返回控制页面 HTML"""
        return '''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Remote Desktop Control</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: Arial, sans-serif; 
            background: #1a1a1a; 
            color: #fff;
            overflow: hidden;
        }
        #screen { 
            width: 100vw; 
            height: 100vh; 
            background: #000;
            cursor: crosshair;
        }
        #screen img {
            width: 100%;
            height: 100%;
            object-fit: contain;
        }
        #controls {
            position: fixed;
            top: 10px;
            right: 10px;
            background: rgba(0,0,0,0.8);
            padding: 15px;
            border-radius: 8px;
            z-index: 1000;
        }
        #controls input {
            padding: 8px;
            margin: 5px 0;
            width: 200px;
            border: 1px solid #444;
            border-radius: 4px;
            background: #333;
            color: #fff;
        }
        #controls button {
            padding: 8px 15px;
            margin: 5px 0;
            width: 100%;
            background: #4CAF50;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }
        #controls button:hover {
            background: #45a049;
        }
        #status {
            padding: 5px;
            text-align: center;
            color: #999;
        }
        #info {
            position: fixed;
            bottom: 10px;
            left: 10px;
            background: rgba(0,0,0,0.8);
            padding: 10px;
            border-radius: 4px;
            font-size: 12px;
        }
    </style>
</head>
<body>
    <div id="screen">
        <img id="screen-img" src="" alt="Screen">
    </div>
    
    <div id="controls">
        <h3>Remote Control</h3>
        <input type="password" id="password" placeholder="Password" value="remote123">
        <button onclick="connect()">连接</button>
        <button onclick="disconnect()">断开</button>
        <div id="status">未连接</div>
    </div>
    
    <div id="info">
        <div>CPU: <span id="cpu">0</span>%</div>
        <div>内存：<span id="memory">0</span>%</div>
        <div>磁盘：<span id="disk">0</span>%</div>
    </div>
    
    <script>
        let connected = false;
        let screenInterval = null;
        let infoInterval = null;
        
        function connect() {
            const password = document.getElementById('password').value;
            if (password) {
                connected = true;
                document.getElementById('status').textContent = '已连接';
                document.getElementById('status').style.color = '#0f0';
                
                // 开始刷新屏幕
                screenInterval = setInterval(updateScreen, 100);
                infoInterval = setInterval(updateInfo, 1000);
            }
        }
        
        function disconnect() {
            connected = false;
            document.getElementById('status').textContent = '未连接';
            document.getElementById('status').style.color = '#999';
            
            clearInterval(screenInterval);
            clearInterval(infoInterval);
        }
        
        function updateScreen() {
            if (!connected) return;
            
            fetch('/screen')
                .then(r => r.json())
                .then(data => {
                    if (data.screen) {
                        document.getElementById('screen-img').src = 'data:image/jpeg;base64,' + data.screen;
                    }
                });
        }
        
        function updateInfo() {
            if (!connected) return;
            
            fetch('/system')
                .then(r => r.json())
                .then(data => {
                    document.getElementById('cpu').textContent = data.cpu || 0;
                    document.getElementById('memory').textContent = data.memory || 0;
                    document.getElementById('disk').textContent = data.disk || 0;
                });
        }
        
        // 鼠标事件
        const screen = document.getElementById('screen');
        
        screen.addEventListener('mousemove', e => {
            if (!connected) return;
            sendControl('mouse', {
                type: 'move',
                x: e.clientX,
                y: e.clientY
            });
        });
        
        screen.addEventListener('click', e => {
            if (!connected) return;
            sendControl('mouse', {
                type: 'click',
                x: e.clientX,
                y: e.clientY,
                button: e.button === 2 ? 'right' : 'left'
            });
        });
        
        screen.addEventListener('contextmenu', e => e.preventDefault());
        
        // 键盘事件
        document.addEventListener('keydown', e => {
            if (!connected) return;
            sendControl('keyboard', {
                text: e.key
            });
        });
        
        function sendControl(action, data) {
            if (!connected) return;
            
            const password = document.getElementById('password').value;
            fetch('/', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    password: password,
                    action: action,
                    ...data
                })
            });
        }
    </script>
</body>
</html>'''
    
    def log_message(self, format, *args):
        """自定义日志"""
        print(f"[{self.address_string()}] {format % args}")


def get_local_ip():
    """获取本地 IP"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"


def main():
    """主函数"""
    print("=" * 60)
    print("  Remote Desktop Server (Simple Version)")
    print("=" * 60)
    print()
    
    local_ip = get_local_ip()
    print(f"  本地 IP: {local_ip}")
    print(f"  端口：{PORT}")
    print(f"  密码：{PASSWORD}")
    print()
    print(f"  访问地址:")
    print(f"    本地：http://localhost:{PORT}")
    print(f"    远程：http://{local_ip}:{PORT}")
    print()
    print("=" * 60)
    print("  等待连接...")
    print("=" * 60)
    print()
    
    # 启动服务器
    server = HTTPServer((HOST, PORT), RemoteHandler)
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n服务器已停止")
        server.shutdown()


if __name__ == '__main__':
    main()
