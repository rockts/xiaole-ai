#!/bin/bash

# 彻底清理并重启前端
# Usage: ./clean-restart.sh

echo "🧹 彻底清理前端..."

# 停止所有 vite 进程
pkill -f "vite" 2>/dev/null
pkill -f "node.*3000" 2>/dev/null
sleep 2

# 清理所有缓存
rm -rf node_modules/.vite
rm -rf dist
rm -rf .vite
rm -rf node_modules/.cache

echo "✅ 缓存已清理"

# 加载 nvm
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

# 切换到脚本所在目录
cd "$(dirname "$0")"

# 使用正确的 Node 版本
nvm use 20

echo "📦 Node 版本: $(node -v)"
echo "🚀 启动前端..."

# 启动
npm run dev
