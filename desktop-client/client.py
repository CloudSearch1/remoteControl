"""
桌面客户端 - 连接到中继服务器

功能:
- 屏幕捕获并上传
- 接收控制命令
- 执行鼠标键盘操作
- 发送系统信息
"""

import os
import io
import json
import time
import socket
import asyncio
import logging
from datetime import datetime

import websockets
import pyautogui
import psutil
from PIL import Image, ImageGrab
from dotenv import load_dotenv

# 加载配置
load_dotenv()

# 配置
SERVER_URL = os.getenv('SERVER_URL', 'ws://your-server-ip:8080/ws/device')
DEVICE_ID = os.getenv('DEVICE_ID', 'my-pc-001')
DEVICE_PASSWORD = os.getenv('DEVICE_PASSWORD', 'relay123')
IMAGE_QUALITY = int(os.getenv('IMAGE_QUALITY', 75))
SCREEN_INTERVAL = float(os.getenv('SCREEN_INTERVAL', 0.1))
PING_TIMEOUT = 30  # 心跳超时时间（秒）
PING_INTERVAL = 10  # 心跳间隔（秒）

# 日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 全局状态
ws = None
client_connected = False


def get_screen_base64():
    """获取屏幕截图 Base64"""
    try:
        screenshot = ImageGrab.grab()
        img_io = io.BytesIO()
        screenshot.save(img_io, 'JPEG', quality=IMAGE_QUALITY)
        img_io.seek(0)
        import base64
        return base64.b64encode(img_io.read()).decode('utf-8')
    except Exception as e:
        logger.error(f"截图失败：{e}")
        return None


def get_system_info():
    """获取系统信息"""
    try:
        return {
            'cpu': psutil.cpu_percent(interval=1),
            'memory': psutil.virtual_memory().percent,
            'disk': psutil.disk_usage('C:').percent,
            'network': {
                'upload': psutil.net_io_counters().bytes_sent,
                'download': psutil.net_io_counters().bytes_recv,
            }
        }
    except Exception as e:
        logger.error(f"获取系统信息失败：{e}")
        return None


def control_mouse(data):
    """控制鼠标"""
    try:
        action = data.get('type', '')
        x = data.get('x', 0)
        y = data.get('y', 0)
        button = data.get('button', 'left')
        
        if action == 'move':
            pyautogui.moveTo(x, y, duration=0.1)
        elif action == 'click':
            pyautogui.click(x, y, button=button)
        elif action == 'double_click':
            pyautogui.doubleClick(x, y, button=button)
        
        logger.debug(f"鼠标控制：{action} ({x}, {y})")
        return True
    except Exception as e:
        logger.error(f"鼠标控制失败：{e}")
        return False


def control_keyboard(data):
    """控制键盘"""
    try:
        key = data.get('key', '')
        text = data.get('text', '')
        
        if text:
            pyautogui.write(text, interval=0.05)
        elif key:
            pyautogui.press(key)
        
        logger.debug(f"键盘控制：{key or text}")
        return True
    except Exception as e:
        logger.error(f"键盘控制失败：{e}")
        return False


async def handle_message(message):
    """处理服务器消息"""
    global client_connected
    
    try:
        data = json.loads(message)
        action = data.get('action', '')
        
        if action == 'client_connected':
            client_connected = True
            logger.info("控制客户端已连接")
        
        elif action == 'get_screen':
            screen_data = get_screen_base64()
            if screen_data and ws:
                await ws.send(json.dumps({
                    'action': 'screen',
                    'data': screen_data
                }))
        
        elif action == 'get_system_info':
            info = get_system_info()
            if info and ws:
                await ws.send(json.dumps({
                    'action': 'system_info',
                    'data': info
                }))
        
        elif action in ['mouse', 'keyboard']:
            if action == 'mouse':
                success = control_mouse(data)
            else:
                success = control_keyboard(data)
            
            if ws:
                await ws.send(json.dumps({
                    'action': 'control_response',
                    'success': success
                }))
        
    except Exception as e:
        logger.error(f"处理消息失败：{e}")


async def screen_capture_loop():
    """屏幕捕获循环"""
    while True:
        try:
            if client_connected and ws:
                screen_data = get_screen_base64()
                if screen_data:
                    await ws.send(json.dumps({
                        'action': 'screen',
                        'data': screen_data
                    }))
            
            await asyncio.sleep(SCREEN_INTERVAL)
        except Exception as e:
            logger.error(f"屏幕捕获错误：{e}")
            await asyncio.sleep(1)


async def system_info_loop():
    """系统信息循环"""
    while True:
        try:
            if client_connected and ws:
                info = get_system_info()
                if info:
                    await ws.send(json.dumps({
                        'action': 'system_info',
                        'data': info
                    }))
            
            await asyncio.sleep(1)
        except Exception as e:
            logger.error(f"系统信息错误：{e}")
            await asyncio.sleep(5)


async def main_loop():
    """主循环"""
    global ws, client_connected
    
    while True:
        try:
            logger.info(f"尝试连接到服务器：{SERVER_URL}")
            
            # 使用更大的 ping 超时保持连接
            async with websockets.connect(
                SERVER_URL,
                ping_timeout=PING_TIMEOUT,
                ping_interval=PING_INTERVAL,
                close_timeout=10
            ) as websocket:
                ws = websocket
                client_connected = False
                
                # 注册设备
                await ws.send(json.dumps({
                    'action': 'register',
                    'device_id': DEVICE_ID,
                    'password': DEVICE_PASSWORD
                }))
                
                # 等待注册响应
                response = await ws.recv()
                data = json.loads(response)
                
                if data.get('status') == 'ok':
                    logger.info(f"设备注册成功：{DEVICE_ID}")
                    print(f"\n✅ 设备已注册：{DEVICE_ID}")
                    print(f"   服务器：{SERVER_URL}")
                    print(f"   时间：{datetime.now()}")
                    print(f"\n等待控制客户端连接...\n")
                    
                    client_connected = True
                    
                    # 启动后台任务
                    screen_task = asyncio.create_task(screen_capture_loop())
                    info_task = asyncio.create_task(system_info_loop())
                    
                    try:
                        # 接收消息
                        async for message in ws:
                            await handle_message(message)
                    finally:
                        screen_task.cancel()
                        info_task.cancel()
                        client_connected = False
                else:
                    logger.error(f"设备注册失败：{data.get('message')}")
                    print(f"\n❌ 注册失败：{data.get('message')}\n")
                    await asyncio.sleep(5)
        
        except websockets.exceptions.ConnectionClosed:
            logger.warning("连接已关闭，5 秒后重连...")
            client_connected = False
            await asyncio.sleep(5)
        
        except Exception as e:
            logger.error(f"连接错误：{e}")
            await asyncio.sleep(5)


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
    print("  Remote Desktop Client")
    print("=" * 60)
    print()
    print(f"  设备 ID: {DEVICE_ID}")
    print(f"  服务器：{SERVER_URL}")
    print(f"  本地 IP: {get_local_ip()}")
    print()
    print("=" * 60)
    print("  正在连接服务器...")
    print("=" * 60)
    print()
    
    try:
        asyncio.run(main_loop())
    except KeyboardInterrupt:
        print("\n\n客户端已停止")


if __name__ == '__main__':
    main()
