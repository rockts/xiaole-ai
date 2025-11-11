#!/bin/bash
# 在后台启动小乐AI服务器（自动重载模式）

echo "🚀 正在后台启动小乐AI服务器（自动重载模式）..."
echo "📝 代码修改后会自动重启服务器"
echo ""

cd /Users/rockts/Dev/xiaole-ai

# 先停止旧进程
echo "🛑 停止旧进程..."
pkill -f "uvicorn main:app" 2>/dev/null || true
sleep 1

# 启动服务器（后台运行 + 自动重载）
echo "✅ 启动新服务器（后台）..."
nohup /Users/rockts/Dev/xiaole-ai/.venv/bin/uvicorn main:app \
    --reload \
    --host 0.0.0.0 \
    --port 8000 \
    --reload-dir . \
    --reload-exclude "*.pyc" \
    --reload-exclude "__pycache__" \
    --reload-exclude "*.log" \
    --reload-exclude "logs/*" \
    --reload-exclude "uploads/*" \
    --reload-exclude "chroma_db/*" \
    > /tmp/xiaole_server.log 2>&1 &

SERVER_PID=$!
echo "✅ 服务器已启动（PID: $SERVER_PID）"
echo "📋 日志文件: /tmp/xiaole_server.log"
echo "🌐 访问地址: http://localhost:8000"
echo ""
echo "📝 现在你可以："
echo "   - 修改代码（会自动重启）"
echo "   - 查看日志: tail -f /tmp/xiaole_server.log"
echo "   - 停止服务: pkill -f 'uvicorn main:app'"
