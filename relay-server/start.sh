#!/bin/bash

echo "========================================"
echo "  Remote Desktop Relay Server"
echo "========================================"
echo ""

# 创建虚拟环境
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
echo "安装依赖..."
pip install -r requirements.txt

# 配置环境
if [ ! -f ".env" ]; then
    echo "创建配置文件..."
    cp .env.example .env
    echo "请编辑 .env 文件修改密码"
fi

# 启动服务器
echo ""
echo "启动服务器..."
echo ""

python server.py
