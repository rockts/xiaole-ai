#!/bin/bash

# 小乐 AI 局域网访问启动脚本
# 适用于其他电脑访问场景

set -e

echo "🌐 启动小乐 AI (局域网访问模式)..."

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# 获取本机IP
MY_IP=$(ifconfig | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}' | head -1)
echo "📍 本机IP: $MY_IP"

# 检查并停止已有进程
echo "📋 检查现有进程..."
pkill -f "python.*main.py" 2>/dev/null || true
pkill -f "vite" 2>/dev/null || true
pkill -f "npm.*dev" 2>/dev/null || true
sleep 2

# 启动后端
echo "🔧 启动后端服务 (0.0.0.0:8000)..."

# 检查虚拟环境
if [ -d ".venv" ]; then
    echo "   使用虚拟环境: .venv"
    source .venv/bin/activate
elif [ -d "venv" ]; then
    echo "   使用虚拟环境: venv"
    source venv/bin/activate
else
    echo "   使用系统Python"
fi

cd backend
nohup python3 main.py > ../logs/backend.log 2>&1 &
BACKEND_PID=$!
cd ..
echo "✅ 后端已启动 (PID: $BACKEND_PID)"

# 等待后端启动
echo "⏳ 等待后端初始化..."
sleep 3

# 启动前端
echo "🎨 启动前端服务 (0.0.0.0:3000)..."
cd frontend

# 尝试加载nvm并使用Node 20
export NVM_DIR="$HOME/.nvm"
if [ -s "$NVM_DIR/nvm.sh" ]; then
    source "$NVM_DIR/nvm.sh"
    # 尝试使用Node 20，如果没有就用default
    nvm use 20 2>/dev/null || nvm use default 2>/dev/null || true
    echo "   Node版本: $(node --version 2>/dev/null || echo '未知')"
fi

# 检查npm是否可用
if command -v npm &> /dev/null && node --version &> /dev/null; then
    # 清理并启动
    rm -rf node_modules/.vite 2>/dev/null || true
    nohup npm run dev > ../logs/frontend.log 2>&1 &
    FRONTEND_PID=$!
    echo "✅ 前端已启动 (PID: $FRONTEND_PID)"
else
    echo "⚠️  Node环境不可用，跳过前端启动"
    echo "   请手动进入 frontend 目录执行: npm run dev"
    FRONTEND_PID=""
fi

cd ..

# 保存 PID
echo $BACKEND_PID > .backend.pid
[ ! -z "$FRONTEND_PID" ] && echo $FRONTEND_PID > .frontend.pid

echo ""
echo "✨ 小乐 AI 已启动（局域网模式）！"
echo ""
echo "📌 本机访问:"
echo "   前端: http://localhost:3000"
echo "   后端: http://localhost:8000"
echo ""
echo "📌 局域网访问:"
echo "   前端: http://${MY_IP}:3000"
echo "   后端: http://${MY_IP}:8000"
echo ""
echo "📝 日志文件:"
echo "   后端: logs/backend.log"
echo "   前端: logs/frontend.log"
echo ""
echo "💡 提示:"
echo "   - 确保防火墙允许3000和8000端口访问"
echo "   - 其他电脑访问时使用: http://${MY_IP}:3000"
echo ""
echo "🛑 停止服务: ./stop.sh"
echo ""
