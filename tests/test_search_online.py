#!/usr/bin/env python3
"""
测试小乐的在线搜索功能
"""
import requests
import json
import time


def test_search():
    """测试搜索功能"""
    print("\n" + "="*60)
    print("🔍 测试小乐的网络搜索功能")
    print("="*60 + "\n")

    # 等待服务器完全启动
    time.sleep(2)

    test_queries = [
        "搜索下iPhone 17 Pro最新消息",
        "帮我查一下2025年春节是几月几号",
    ]

    for query in test_queries:
        print(f"📝 测试查询: {query}")
        print("-"*60)

        try:
            response = requests.post(
                "http://localhost:8000/chat",
                json={
                    "message": query,
                    "session_id": "test_session_search",
                    "user_id": "test_user"
                },
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                print(f"✅ 响应成功")
                print(f"📄 回复: {data.get('response', 'N/A')[:200]}...")

                # 检查是否使用了搜索工具
                tools_used = data.get('tools_used', [])
                if 'search' in tools_used:
                    print(f"✅ 使用了搜索工具!")
                else:
                    print(f"⚠️  未使用搜索工具，使用的工具: {tools_used}")
            else:
                print(f"❌ 请求失败: {response.status_code}")
                print(f"   {response.text}")

        except Exception as e:
            print(f"❌ 异常: {e}")

        print()


if __name__ == "__main__":
    test_search()
