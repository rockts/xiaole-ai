#!/bin/bash

# 小乐 AI 统一启动脚本
# 用法: ./start.sh

set -e

echo "🚀 启动小乐 AI..."

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# 检查并停止已有进程
echo "📋 检查现有进程..."
pkill -f "python.*main.py" 2>/dev/null || true
pkill -f "vite" 2>/dev/null || true
sleep 1

# 启动后端
echo "🔧 启动后端服务 (端口 8000)..."
source .venv/bin/activate
# 在项目根目录运行,避免导入路径问题
nohup python -m backend.main > logs/backend.log 2>&1 &
BACKEND_PID=$!
echo "✅ 后端已启动 (PID: $BACKEND_PID)"

# 等待后端启动
sleep 2

# 启动前端
echo "🎨 启动前端服务 (端口 3000)..."
cd frontend

# 加载 nvm 并使用项目指定的 Node 版本
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

# 自动使用 .nvmrc 中指定的版本
if [ -f .nvmrc ]; then
    echo "📦 使用 .nvmrc 指定的 Node 版本..."
    nvm use || nvm install
else
    echo "⚠️  未找到 .nvmrc，使用 Node 20..."
    nvm use 20 2>/dev/null || nvm install 20
fi

NODE_VERSION=$(node --version)
echo "✅ Node 版本: $NODE_VERSION"

# 清理缓存并启动
rm -rf node_modules/.vite
nohup npm run dev > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
echo "✅ 前端已启动 (PID: $FRONTEND_PID)"

cd ..

# 保存 PID
echo $BACKEND_PID > .backend.pid
echo $FRONTEND_PID > .frontend.pid

echo ""
echo "✨ 小乐 AI 已启动！"
echo ""
echo "📌 访问地址:"
echo "   前端: http://localhost:3000"
echo "   后端: http://localhost:8000"
echo ""
echo "📝 日志文件:"
echo "   后端: logs/backend.log"
echo "   前端: logs/frontend.log"
echo ""
echo "🛑 停止服务: ./stop.sh"
echo ""
