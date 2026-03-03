"""
远程桌面客户端 - 图形界面

功能:
- 显示远程屏幕
- 发送鼠标键盘事件
- 系统信息显示
"""

import sys
import os
import base64
from io import BytesIO

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QSpinBox, QGroupBox,
    QStatusBar, QToolBar, QAction, QFileDialog, QMessageBox,
    QProgressBar, QFrame
)
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap, QImage, QIcon

import socketio
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class ScreenLabel(QLabel):
    """屏幕显示标签 - 支持鼠标事件"""
    
    mouse_move_signal = pyqtSignal(int, int)
    mouse_click_signal = pyqtSignal(int, int, str)
    mouse_scroll_signal = pyqtSignal(int, int, int)
    key_press_signal = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.setAlignment(Qt.AlignCenter)
        self.setMinimumSize(800, 600)
        self.setStyleSheet("QLabel { background-color: #1a1a1a; border: 1px solid #333; }")
    
    def mouseMoveEvent(self, event):
        pos = self.mapFromGlobal(event.globalPos())
        self.mouse_move_signal.emit(pos.x(), pos.y())
    
    def mousePressEvent(self, event):
        pos = self.mapFromGlobal(event.globalPos())
        if event.button() == Qt.LeftButton:
            self.mouse_click_signal.emit(pos.x(), pos.y(), 'left')
        elif event.button() == Qt.RightButton:
            self.mouse_click_signal.emit(pos.x(), pos.y(), 'right')
    
    def wheelEvent(self, event):
        pos = self.mapFromGlobal(event.globalPos())
        delta = event.angleDelta().y()
        self.mouse_scroll_signal.emit(pos.x(), pos.y(), delta)
    
    def keyPressEvent(self, event):
        key = event.text()
        if key:
            self.key_press_signal.emit(key)


class ControlPanel(QGroupBox):
    """控制面板"""
    
    def __init__(self):
        super().__init__("控制面板")
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # 服务器地址
        server_layout = QHBoxLayout()
        server_layout.addWidget(QLabel("服务器:"))
        self.server_input = QLineEdit("http://localhost:5000")
        server_layout.addWidget(self.server_input)
        layout.addLayout(server_layout)
        
        # 密码
        auth_layout = QHBoxLayout()
        auth_layout.addWidget(QLabel("密码:"))
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        auth_layout.addWidget(self.password_input)
        layout.addLayout(auth_layout)
        
        # 质量
        quality_layout = QHBoxLayout()
        quality_layout.addWidget(QLabel("质量:"))
        self.quality_spin = QSpinBox()
        self.quality_spin.setRange(10, 100)
        self.quality_spin.setValue(80)
        quality_layout.addWidget(self.quality_spin)
        layout.addLayout(quality_layout)
        
        # 连接按钮
        self.connect_btn = QPushButton("连接")
        self.connect_btn.clicked.connect(self.on_connect)
        layout.addWidget(self.connect_btn)
        
        # 断开按钮
        self.disconnect_btn = QPushButton("断开")
        self.disconnect_btn.clicked.connect(self.on_disconnect)
        self.disconnect_btn.setEnabled(False)
        layout.addWidget(self.disconnect_btn)
        
        # 状态标签
        self.status_label = QLabel("状态：未连接")
        self.status_label.setStyleSheet("color: #999")
        layout.addWidget(self.status_label)
        
        self.setLayout(layout)
    
    def on_connect(self):
        self.connect_btn.setEnabled(False)
    
    def on_disconnect(self):
        self.disconnect_btn.setEnabled(False)
    
    def set_connected(self, connected):
        self.connect_btn.setEnabled(not connected)
        self.disconnect_btn.setEnabled(connected)
        self.status_label.setText("状态：已连接" if connected else "状态：未连接")
        self.status_label.setStyleSheet("color: #0f0" if connected else "color: #999")


class SystemInfoPanel(QGroupBox):
    """系统信息面板"""
    
    def __init__(self):
        super().__init__("系统信息")
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # CPU
        cpu_layout = QHBoxLayout()
        cpu_layout.addWidget(QLabel("CPU:"))
        self.cpu_bar = QProgressBar()
        self.cpu_bar.setRange(0, 100)
        self.cpu_bar.setValue(0)
        cpu_layout.addWidget(self.cpu_bar)
        layout.addLayout(cpu_layout)
        
        # 内存
        mem_layout = QHBoxLayout()
        mem_layout.addWidget(QLabel("内存:"))
        self.mem_bar = QProgressBar()
        self.mem_bar.setRange(0, 100)
        self.mem_bar.setValue(0)
        mem_layout.addWidget(self.mem_bar)
        layout.addLayout(mem_layout)
        
        # 磁盘
        disk_layout = QHBoxLayout()
        disk_layout.addWidget(QLabel("磁盘:"))
        self.disk_bar = QProgressBar()
        self.disk_bar.setRange(0, 100)
        self.disk_bar.setValue(0)
        disk_layout.addWidget(self.disk_bar)
        layout.addLayout(disk_layout)
        
        self.setLayout(layout)
    
    def update_info(self, info):
        if 'cpu' in info:
            self.cpu_bar.setValue(info['cpu'])
        if 'memory' in info:
            self.mem_bar.setValue(info['memory'])
        if 'disk' in info:
            self.disk_bar.setValue(info['disk'])


class RemoteDesktopClient(QMainWindow):
    """远程桌面客户端主窗口"""
    
    def __init__(self):
        super().__init__()
        self.sio = socketio.Client()
        self.screen_timer = QTimer()
        self.info_timer = QTimer()
        self.is_connected = False
        
        self.init_ui()
        self.setup_socketio()
        self.setup_timers()
    
    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle("Remote Desktop Control")
        self.setMinimumSize(1200, 800)
        
        # 中心部件
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        
        # 左侧控制面板
        left_panel = QVBoxLayout()
        self.control_panel = ControlPanel()
        left_panel.addWidget(self.control_panel)
        
        self.system_info = SystemInfoPanel()
        left_panel.addWidget(self.system_info)
        
        # 拉伸
        left_panel.addStretch()
        
        main_layout.addLayout(left_panel)
        
        # 右侧屏幕显示
        self.screen_label = ScreenLabel()
        main_layout.addWidget(self.screen_label)
        
        # 状态栏
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("就绪")
        
        # 连接信号
        self.control_panel.connect_btn.clicked.connect(self.connect_server)
        self.control_panel.disconnect_btn.clicked.connect(self.disconnect_server)
        
        # 屏幕事件
        self.screen_label.mouse_move_signal.connect(self.send_mouse_move)
        self.screen_label.mouse_click_signal.connect(self.send_mouse_click)
        self.screen_label.mouse_scroll_signal.connect(self.send_mouse_scroll)
        self.screen_label.key_press_signal.connect(self.send_key_press)
    
    def setup_socketio(self):
        """配置 Socket.IO"""
        @self.sio.event
        def connect():
            print("已连接到服务器")
            self.statusBar.showMessage("已连接到服务器")
        
        @self.sio.event
        def disconnect():
            print("与服务器断开连接")
            self.statusBar.showMessage("与服务器断开连接")
            self.set_connected(False)
        
        @self.sio.on('auth_success')
        def on_auth_success(data):
            print("认证成功")
            self.set_connected(True)
            self.statusBar.showMessage("认证成功")
        
        @self.sio.on('auth_error')
        def on_auth_error(data):
            print("认证失败")
            self.statusBar.showMessage("认证失败")
            QMessageBox.warning(self, "错误", "密码错误")
            self.set_connected(False)
        
        @self.sio.on('screen_data')
        def on_screen_data(data):
            try:
                image_data = base64.b64decode(data['image'])
                image = QImage()
                image.loadFromData(image_data)
                pixmap = QPixmap.fromImage(image)
                self.screen_label.setPixmap(pixmap.scaled(
                    self.screen_label.size(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                ))
            except Exception as e:
                print(f"显示图像失败：{e}")
        
        @self.sio.on('system_info')
        def on_system_info(info):
            self.system_info.update_info(info)
        
        @self.sio.on('error')
        def on_error(data):
            print(f"错误：{data.get('message', '未知错误')}")
    
    def setup_timers(self):
        """配置定时器"""
        self.screen_timer.timeout.connect(self.request_screen)
        self.info_timer.timeout.connect(self.request_system_info)
    
    def connect_server(self):
        """连接服务器"""
        server_url = self.control_panel.server_input.text()
        password = self.control_panel.password_input.text()
        
        try:
            self.sio.connect(server_url)
            self.sio.emit('auth', {'password': password})
        except Exception as e:
            QMessageBox.critical(self, "错误", f"连接失败：{e}")
            self.set_connected(False)
    
    def disconnect_server(self):
        """断开服务器"""
        try:
            self.sio.disconnect()
        except:
            pass
        self.set_connected(False)
    
    def set_connected(self, connected):
        """设置连接状态"""
        self.is_connected = connected
        self.control_panel.set_connected(connected)
        
        if connected:
            self.screen_timer.start(100)  # 10 FPS
            self.info_timer.start(1000)   # 1 秒更新一次系统信息
        else:
            self.screen_timer.stop()
            self.info_timer.stop()
    
    def request_screen(self):
        """请求屏幕"""
        if self.is_connected:
            self.sio.emit('request_screen')
    
    def request_system_info(self):
        """请求系统信息"""
        if self.is_connected:
            self.sio.emit('get_system_info')
    
    def send_mouse_move(self, x, y):
        """发送鼠标移动"""
        if self.is_connected:
            self.sio.emit('mouse_event', {
                'action': 'move',
                'x': x,
                'y': y
            })
    
    def send_mouse_click(self, x, y, button):
        """发送鼠标点击"""
        if self.is_connected:
            self.sio.emit('mouse_event', {
                'action': 'click',
                'x': x,
                'y': y,
                'button': button
            })
    
    def send_mouse_scroll(self, x, y, delta):
        """发送鼠标滚轮"""
        if self.is_connected:
            self.sio.emit('mouse_event', {
                'action': 'scroll',
                'x': x,
                'y': y,
                'amount': delta // 120
            })
    
    def send_key_press(self, key):
        """发送键盘输入"""
        if self.is_connected:
            self.sio.emit('keyboard_event', {'key': key})
    
    def closeEvent(self, event):
        """关闭事件"""
        try:
            self.sio.disconnect()
        except:
            pass
        event.accept()


def main():
    """主函数"""
    app = QApplication(sys.argv)
    
    # 设置样式
    app.setStyle('Fusion')
    
    # 创建窗口
    window = RemoteDesktopClient()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
