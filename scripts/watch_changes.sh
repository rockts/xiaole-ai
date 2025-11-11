#!/bin/bash
# 监控代码变化并显示重启提示

echo "👀 监控代码变化中..."
echo "📝 修改 Python 文件会自动触发服务器重启"
echo "按 Ctrl+C 停止监控"
echo ""

cd /Users/rockts/Dev/xiaole-ai

# 使用 fswatch（如果没有会提示安装）
if ! command -v fswatch &> /dev/null; then
    echo "⚠️  fswatch 未安装"
    echo "可选安装命令: brew install fswatch"
    echo ""
    echo "📝 使用简单模式监控..."
    
    # 简单模式：每秒检查一次
    last_mod=0
    while true; do
        current_mod=$(find . -name "*.py" -newer /tmp/xiaole_last_check 2>/dev/null | wc -l)
        if [ "$current_mod" -gt 0 ]; then
            echo "🔄 $(date '+%H:%M:%S') - 检测到 Python 文件修改"
            echo "   服务器正在自动重启..."
            touch /tmp/xiaole_last_check
        fi
        sleep 1
    done
else
    # 高级模式：实时监控
    fswatch -o --event Created --event Updated --event Removed \
        -e ".*\.pyc$" \
        -e "__pycache__" \
        -e "\.log$" \
        -e "logs/" \
        -e "uploads/" \
        -e "chroma_db/" \
        . | while read change; do
        echo "🔄 $(date '+%H:%M:%S') - 检测到文件变化"
        echo "   服务器正在自动重启..."
    done
fi
