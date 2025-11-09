#!/bin/bash
# 简单的API测试脚本

echo "🚀 测试小乐AI API"
echo ""

echo "1️⃣ 测试首页..."
curl -s http://localhost:8000/ | jq '.'
echo ""

echo "2️⃣ 测试思考功能..."
curl -s -X POST "http://localhost:8000/think?prompt=你好" | jq '.'
echo ""

echo "3️⃣ 测试执行任务（保存记忆）..."
curl -s -X POST "http://localhost:8000/act?command=记住我喜欢编程" | jq '.'
echo ""

echo "4️⃣ 查看记忆..."
curl -s "http://localhost:8000/memory?tag=task" | jq '.'
echo ""

echo "✅ 测试完成！"
