#!/bin/bash

echo "🚀 启动小乐 AI 管家 Vue3 前端"
echo "================================"

cd "$(dirname "$0")"

# 检查 node_modules 是否存在
if [ ! -d "node_modules" ]; then
    echo "📦 首次运行，正在安装依赖..."
    npm install
fi

# 检查 .env 文件
if [ ! -f ".env" ]; then
    echo "📝 创建 .env 文件..."
    cp .env.example .env
fi

echo ""
echo "✅ 前端将运行在: http://localhost:3000"
echo "✅ 后端 API 代理: http://localhost:8000"
echo ""
echo "🔧 确保后端服务器已启动在 8000 端口"
echo ""

npm run dev
