#!/usr/bin/env python3
"""测试课程表API"""

import requests
import json

API_BASE = "http://localhost:8000"

print("=" * 60)
print("测试课程表API")
print("=" * 60)

# 1. 测试GET /api/schedule - 加载课程表
print("\n1️⃣ 测试加载课程表...")
try:
    response = requests.get(f"{API_BASE}/api/schedule?user_id=default_user")
    data = response.json()
    
    if data.get("success"):
        print("✅ 加载成功")
        schedule = data.get("schedule", {})
        courses = schedule.get("courses", {})
        print(f"   找到 {len(courses)} 门课程")
        
        # 显示前3个课程
        for i, (key, course) in enumerate(list(courses.items())[:3]):
            print(f"   - {key}: {course}")
        
        if len(courses) > 3:
            print(f"   ... 还有 {len(courses) - 3} 门课程")
    else:
        print("⚠️ 加载课程表返回空数据")
        print(f"   Response: {json.dumps(data, ensure_ascii=False, indent=2)}")
        
except Exception as e:
    print(f"❌ 请求失败: {e}")
    print("   提示：请确保服务器正在运行 (python main.py)")

# 2. 测试POST /api/schedule - 保存课程表
print("\n2️⃣ 测试保存课程表...")
try:
    test_schedule = {
        "user_id": "default_user",
        "schedule": {
            "periods": ['第1节', '第2节', '第3节', '第4节', '第5节'],
            "weekdays": ['周一', '周二', '周三', '周四', '周五'],
            "courses": {
                "0_周一": "晨读",
                "1_周一": "数学",
                "3_周一": "科学(5)",
                "0_周二": "晨读",
                "2_周二": "英语"
            }
        }
    }
    
    response = requests.post(
        f"{API_BASE}/api/schedule",
        json=test_schedule
    )
    data = response.json()
    
    if data.get("success"):
        print("✅ 保存成功")
        print(f"   消息: {data.get('message')}")
    else:
        print(f"❌ 保存失败: {data.get('error')}")
        
except Exception as e:
    print(f"❌ 请求失败: {e}")

print("\n" + "=" * 60)
print("测试完成！")
print("=" * 60)
