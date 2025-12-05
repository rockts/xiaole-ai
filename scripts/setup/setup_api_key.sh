#!/bin/bash
# Claude API Key 快速配置脚本

echo "======================================"
echo "  Claude API Key 配置向导"
echo "======================================"
echo ""

# 检查 .env 文件是否存在
if [ ! -f .env ]; then
    echo "❌ 错误: 找不到 .env 文件"
    exit 1
fi

echo "📝 请按照以下步骤获取 API Key："
echo ""
echo "1. 访问: https://console.anthropic.com/"
echo "2. 注册/登录账号"
echo "3. 进入 API Keys 页面"
echo "4. 点击 Create Key"
echo "5. 复制生成的 Key (格式: sk-ant-api03-...)"
echo ""
echo "======================================"
echo ""

# 提示用户输入
read -p "请粘贴你的 Claude API Key: " api_key

# 验证格式
if [[ ! $api_key =~ ^sk-ant- ]]; then
    echo "⚠️  警告: API Key 格式可能不正确"
    echo "应该以 sk-ant- 开头"
    read -p "确定要继续吗? (y/n): " confirm
    if [ "$confirm" != "y" ]; then
        echo "已取消"
        exit 1
    fi
fi

# 备份原文件
cp .env .env.backup
echo "✅ 已备份 .env 到 .env.backup"

# 更新配置
if grep -q "CLAUDE_API_KEY=" .env; then
    # 替换已存在的配置
    sed -i.tmp "s|CLAUDE_API_KEY=.*|CLAUDE_API_KEY=$api_key|g" .env
    rm -f .env.tmp
    echo "✅ 已更新 CLAUDE_API_KEY"
else
    # 添加新配置
    echo "CLAUDE_API_KEY=$api_key" >> .env
    echo "✅ 已添加 CLAUDE_API_KEY"
fi

echo ""
echo "======================================"
echo "🎉 配置完成！"
echo "======================================"
echo ""
echo "下一步："
echo "1. 运行测试: python test_claude.py"
echo "2. 启动服务: uvicorn main:app --reload"
echo ""
