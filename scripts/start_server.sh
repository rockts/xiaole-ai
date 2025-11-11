#!/bin/bash
# 启动小乐AI服务器（自动重载模式）

echo "🚀 正在启动小乐AI服务器（自动重载模式）..."
echo "📝 代码修改后会自动重启服务器"
echo ""

cd /Users/rockts/Dev/xiaole-ai

# 先停止旧进程
echo "🛑 停止旧进程..."
pkill -f "uvicorn main:app" 2>/dev/null || true
sleep 1

# 启动服务器（带自动重载）
echo "✅ 启动新服务器..."
/Users/rockts/Dev/xiaole-ai/.venv/bin/uvicorn main:app \
    --reload \
    --host 0.0.0.0 \
    --port 8000 \
    --reload-dir . \
    --reload-exclude "*.pyc" \
    --reload-exclude "__pycache__" \
    --reload-exclude "*.log" \
    --reload-exclude "logs/*" \
    --reload-exclude "uploads/*" \
    --reload-exclude "chroma_db/*"
