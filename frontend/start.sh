#!/bin/bash

# 小乐 AI 前端独立启动脚本

cd "$(dirname "$0")"

echo "🚀 启动小乐 AI 管家 Vue3 前端"
echo "================================"

# 加载 nvm
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

# 自动使用 .nvmrc 中指定的 Node 版本
if [ -f .nvmrc ]; then
    echo "📦 检测到 .nvmrc，使用指定的 Node 版本..."
    nvm install
    nvm use
else
    echo "⚠️  未找到 .nvmrc，使用 Node 20..."
    nvm use 20 2>/dev/null || nvm install 20
fi

NODE_VERSION=$(node --version)
NPM_VERSION=$(npm --version)
echo "✅ Node: $NODE_VERSION"
echo "✅ npm: $NPM_VERSION"
echo ""

# 检查 node_modules 是否存在
if [ ! -d "node_modules" ]; then
    echo "📦 首次运行，正在安装依赖..."
    npm install
    echo ""
fi

# 检查 .env 文件
if [ ! -f ".env" ]; then
    echo "📝 创建 .env 文件..."
    cp .env.example .env 2>/dev/null || echo "⚠️  .env.example 不存在"
    echo ""
fi

echo "✅ 前端将运行在: http://localhost:3000"
echo "✅ 后端 API 代理: http://localhost:8000"
echo ""
echo "🔧 确保后端服务器已启动在 8000 端口"
echo ""

npm run dev
