#!/bin/bash

# 小乐 AI 停止脚本
# 用法: ./stop.sh

echo "🛑 停止小乐 AI..."

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# 停止后端
if [ -f .backend.pid ]; then
    BACKEND_PID=$(cat .backend.pid)
    if ps -p $BACKEND_PID > /dev/null 2>&1; then
        kill $BACKEND_PID
        echo "✅ 后端已停止 (PID: $BACKEND_PID)"
    fi
    rm .backend.pid
fi

# 停止前端
if [ -f .frontend.pid ]; then
    FRONTEND_PID=$(cat .frontend.pid)
    if ps -p $FRONTEND_PID > /dev/null 2>&1; then
        kill $FRONTEND_PID
        echo "✅ 前端已停止 (PID: $FRONTEND_PID)"
    fi
    rm .frontend.pid
fi

# 清理其他可能的进程
pkill -f "python.*main.py" 2>/dev/null && echo "🧹 清理后端残留进程" || true
pkill -f "vite" 2>/dev/null && echo "🧹 清理前端残留进程" || true

echo ""
echo "✨ 小乐 AI 已停止"
