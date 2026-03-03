#!/bin/bash

# Remote Desktop Relay Server - Ubuntu Deployment Script
# 中转服务器部署脚本 (Ubuntu/Debian)

set -e

echo "========================================"
echo "  Remote Desktop Relay Server"
echo "  Ubuntu 部署脚本"
echo "========================================"
echo ""

# 检查是否 root
if [ "$EUID" -ne 0 ]; then 
    echo "错误：请使用 root 用户或 sudo 运行此脚本"
    echo "用法：sudo ./deploy.sh"
    exit 1
fi

echo "[1/8] 停止旧服务..."
pkill -f "python server.py" || true
sleep 2

echo "[2/8] 更新系统..."
apt update && apt upgrade -y

echo "[2/8] 安装系统依赖..."
apt install -y python3 python3-pip python3-venv git curl wget

echo "[3/8] 停止旧服务..."
pkill -f "python server.py" || true
sleep 2

echo "[4/8] 克隆项目..."
cd /opt
if [ -d "remoteControl" ]; then
    echo "项目已存在，删除旧版本"
    rm -rf /opt/remoteControl
fi
git clone git@github.com:CloudSearch1/remoteControl.git
cd remoteControl/relay-server

echo "[4/8] 创建虚拟环境..."
python3 -m venv venv
source venv/bin/activate

echo "[5/8] 安装 Python 依赖..."
pip install --upgrade pip
pip install -r requirements.txt

echo "[6/8] 配置环境..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo ""
    echo "请设置服务器密码："
    read -s -p "输入密码：" PASSWORD
    echo ""
    if [ -z "$PASSWORD" ]; then
        echo "错误：密码不能为空"
        exit 1
    fi
    sed -i "s/SERVER_PASSWORD=.*/SERVER_PASSWORD=$PASSWORD/" .env
    echo "密码已配置"
else
    echo "配置文件已存在"
fi

echo "[7/8] 配置防火墙..."
if command -v ufw &> /dev/null; then
    ufw allow 8999/tcp
    echo "防火墙已配置，开放端口 8999"
else
    echo "未检测到 ufw，请手动配置防火墙"
fi

echo "[8/8] 启动服务..."
pkill -f "python server.py" || true
sleep 2
pkill -f "python server.py" || true
sleep 2
nohup python server.py > server.log 2>&1 &

# 等待启动
sleep 3

# 检查状态
if pgrep -f "python server.py" > /dev/null; then
    echo ""
    echo "========================================"
    echo "  部署成功！"
    echo "========================================"
    echo ""
    echo "服务状态：运行中"
    echo "访问地址：http://$(curl -s ifconfig.me):8080"
    echo "日志文件：server.log"
    echo ""
    echo "查看日志：tail -f server.log"
    echo "停止服务：pkill -f 'python server.py'"
    echo "重启服务：./deploy.sh (重新运行脚本)"
    echo ""
else
    echo ""
    echo "========================================"
    echo "  部署失败！"
    echo "========================================"
    echo ""
    echo "请检查日志：server.log"
    exit 1
fi
