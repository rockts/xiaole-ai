#!/bin/bash

# 小乐AI管家 - 一键启动脚本

echo "🤖 启动小乐AI管家..."
echo ""

# 检查虚拟环境
if [ ! -d ".venv" ]; then
    echo "❌ 虚拟环境不存在，请先运行: python3 -m venv .venv && .venv/bin/pip install -r requirements.txt"
    exit 1
fi

# 检查.env文件
if [ ! -f ".env" ]; then
    echo "❌ .env文件不存在，请先配置环境变量"
    exit 1
fi

# 停止旧进程
echo "🔄 停止旧进程..."
pkill -f 'uvicorn main:app' 2>/dev/null

# 等待进程完全停止
sleep 1

# 启动服务器
echo "🚀 启动FastAPI服务器..."
.venv/bin/uvicorn main:app --reload --host 0.0.0.0 --port 8000 &

# 等待服务器启动
sleep 3

# 检查服务状态
if curl -s http://localhost:8000/ > /dev/null; then
    echo ""
    echo "✅ 小乐AI管家启动成功!"
    echo ""
    echo "📌 访问地址:"
    echo "   🌐 Web界面: http://localhost:8000/static/index.html"
    echo "   📚 API文档: http://localhost:8000/docs"
    echo "   🔌 API地址: http://localhost:8000"
    echo ""
    echo "📊 功能概览:"
    echo "   - 多轮对话 (支持上下文)"
    echo "   - 记忆管理 (持久化到NAS PostgreSQL)"
    echo "   - 会话管理 (自动保存历史)"
    echo "   - 错误重试 (自动恢复)"
    echo ""
    echo "📝 查看日志: tail -f logs/xiaole_ai.log"
    echo "🛑 停止服务: pkill -f 'uvicorn main:app'"
else
    echo ""
    echo "❌ 服务启动失败，请检查日志: logs/xiaole_ai.log"
    exit 1
fi
