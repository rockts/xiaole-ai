#!/bin/bash
# 检查 Node 版本的启动前脚本

NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)

if [ "$NODE_VERSION" -lt 18 ]; then
    echo "❌ 错误: Node 版本过低 (当前: v$NODE_VERSION)"
    echo "📦 需要: Node >= 18.0.0"
    echo ""
    echo "🔧 修复方法:"
    echo "  nvm use 20"
    echo "  或"
    echo "  source ~/.zshrc && nvm use"
    exit 1
fi

echo "✅ Node 版本: $(node --version)"
