#!/bin/bash
# 启动小乐AI服务器

cd /Users/rockts/Dev/xiaole-ai

# 清理旧进程
echo "🧹 清理旧进程..."
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
sleep 1

# 激活虚拟环境并启动
echo "🚀 启动服务器..."
source venv/bin/activate
nohup python main.py > /tmp/xiaole.log 2>&1 &

sleep 3

# 检查进程
if ps aux | grep "[p]ython.*main.py" > /dev/null; then
    PID=$(ps aux | grep "[p]ython.*main.py" | awk '{print $2}')
    echo "✅ 服务器启动成功! PID: $PID"
    echo "📝 日志文件: /tmp/xiaole.log"
    echo "🌐 访问地址: http://localhost:8000"
    
    # 测试连接
    sleep 1
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ 服务器健康检查通过"
    else
        echo "⚠️  服务器可能还在启动中..."
    fi
else
    echo "❌ 服务器启动失败，查看日志:"
    tail -20 /tmp/xiaole.log
fi
