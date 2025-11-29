#!/bin/bash
# API 端点测试脚本

echo "🔍 测试关键 API 端点..."
echo ""

echo "1️⃣  测试会话列表 (/api/sessions)"
curl -m 3 -s http://localhost:8000/api/sessions 2>&1 | head -3
echo -e "\n"

echo "2️⃣  测试记忆统计 (/api/memory/stats)"
curl -m 3 -s http://localhost:8000/api/memory/stats 2>&1 | head -3
echo -e "\n"

echo "3️⃣  测试记忆列表 (/api/memory/recent)"
curl -m 3 -s "http://localhost:8000/api/memory/recent?hours=24&limit=5" 2>&1 | head -3
echo -e "\n"

echo "4️⃣  测试行为分析 (/api/analytics/behavior)"
curl -m 3 -s "http://localhost:8000/api/analytics/behavior?days=30" 2>&1 | head -3
echo -e "\n"

echo "✅ 测试完成"
