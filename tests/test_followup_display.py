#!/usr/bin/env python3
"""
测试追问提示功能
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import json

API_BASE = "http://localhost:8000"

print("=" * 60)
print("测试追问提示功能")
print("=" * 60)

# 1. 发送一个不完整的问题
print("\n1️⃣ 发送不完整问题...")
question = "Python好还是Java好？"
response = requests.post(
    f"{API_BASE}/chat",
    params={"prompt": question}
)

data = response.json()
print(f"✅ 服务器响应:")
print(f"   原始响应: {json.dumps(data, ensure_ascii=False, indent=2)}")

if 'reply' in data:
    print(f"   回复: {data['reply'][:100]}...")
    print(f"   Session ID: {data.get('session_id', 'N/A')}")
else:
    print(f"   ⚠️ 响应中没有reply字段")
    if 'error' in data or 'detail' in data:
        print(f"   错误: {data.get('error') or data.get('detail')}")

# 检查是否有followup
if 'followup' in data:
    print(f"\n🎉 发现追问提示!")
    followup = data['followup']
    print(f"   ID: {followup.get('id')}")
    print(f"   追问: {followup.get('followup')}")
    print(f"   置信度: {followup.get('confidence')}")
    print("\n✅ 前端会显示追问提示卡片")
else:
    print(f"\n⚠️  本次对话没有触发追问")
    print("   可能原因: 问题比较完整或置信度不够")

# 2. 查看待追问记录
print(f"\n2️⃣ 查看所有待追问记录...")
response = requests.get(f"{API_BASE}/proactive_qa/pending")
if response.status_code == 200:
    pending = response.json()
    print(f"✅ 找到 {len(pending)} 条待追问记录:")
    for item in pending[:3]:  # 只显示前3条
        print(f"\n   [{item['id']}] {item['original_question']}")
        print(f"        追问: {item['followup_question']}")
        print(f"        置信度: {item['confidence']}")
else:
    print(f"❌ 获取失败: {response.status_code}")

print(f"\n" + "=" * 60)
print("测试完成！")
print("=" * 60)
print("\n💡 操作说明:")
print("   1. 打开浏览器 http://localhost:8000")
print("   2. 发送一个不完整的问题")
print("   3. 看到回复后应该会弹出追问提示卡片")
print("   4. 点击卡片会自动发送追问")
