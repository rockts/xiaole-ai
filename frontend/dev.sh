#!/bin/bash
# 🔧 小乐前端快速启动 (前台运行)

cd "$(dirname "$0")"

echo "🧹 清理旧进程..."
pkill -9 -f "npm run dev" 2>/dev/null || true
pkill -9 -f "node.*vite" 2>/dev/null || true
sleep 1

echo "🗑️  清理缓存..."
rm -rf node_modules/.vite dist .vite

echo "🔍 加载 Node 环境..."
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && source "$NVM_DIR/nvm.sh"

if [ -f .nvmrc ]; then
    nvm use || nvm install
else
    nvm use 20 2>/dev/null || nvm install 20
fi

echo "✅ Node $(node --version)"
echo ""
echo "🚀 启动 Vite 开发服务器..."
echo "💡 提示: 按 Ctrl+C 停止服务"
echo ""

# 前台运行,便于看到实时日志
exec npm run dev
