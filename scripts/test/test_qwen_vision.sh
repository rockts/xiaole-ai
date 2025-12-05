#!/bin/bash
# 快速测试 Qwen 图像识别

echo "🧪 测试 Qwen-VL 图像识别"
echo "======================================"

# 检查 API Key
if grep -q "your_qwen_api_key_here" .env; then
    echo "❌ 错误：QWEN_API_KEY 还未配置！"
    echo ""
    echo "请按以下步骤操作："
    echo "1. 访问 https://dashscope.console.aliyun.com/"
    echo "2. 创建 API Key"
    echo "3. 编辑 .env 文件，替换 QWEN_API_KEY=your_qwen_api_key_here"
    echo ""
    echo "详细说明请查看：docs/QWEN_VISION_SETUP.md"
    exit 1
fi

echo "✅ Qwen API Key 已配置"
echo ""

# 检查测试图片
if [ ! -f "uploads/20251111_225624_IMG_9959.jpeg" ]; then
    echo "⚠️  测试图片不存在，请先上传图片"
    echo "可用图片："
    ls -lh uploads/*.{jpg,jpeg,png} 2>/dev/null | head -5
    exit 1
fi

echo "📸 测试图片：uploads/20251111_225624_IMG_9959.jpeg"
echo ""

# 直接测试 Python 函数
echo "🔍 方式1：直接调用 Python 函数"
echo "-----------------------------------"
.venv/bin/python -c "
from vision_tool import VisionTool
import json

tool = VisionTool()
print(f'Qwen可用: {\"✅\" if tool.qwen_key else \"❌\"}')
print(f'API Key: {tool.qwen_key[:20]}...' if tool.qwen_key else 'API Key: 未配置')
print()
print('正在分析图片...')
result = tool.analyze_with_qwen('uploads/20251111_225624_IMG_9959.jpeg', '请简单描述这张图片的主要内容')
print()
print('结果:')
print(json.dumps(result, ensure_ascii=False, indent=2))
"

echo ""
echo "======================================"
echo "✅ 测试完成！"
echo ""
echo "如果看到 success: true，说明配置成功！"
echo "现在可以在浏览器中使用图片识别功能了。"
