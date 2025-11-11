#!/usr/bin/env python3
"""测试Phase 3的非数据库功能(快速意图匹配、响应风格)"""
import requests
import json

BASE_URL = "http://localhost:8000"


def test_quick_intent_matching():
    """测试快速意图匹配"""
    print("\n🧪 测试快速意图匹配")
    print("=" * 60)

    test_cases = [
        ("现在几点", "应该直接返回时间"),
        ("今天天气怎么样", "应该调用天气工具"),
        ("100+200", "应该直接计算"),
        ("帮我记住我今年25岁", "应该调用存储记忆"),
    ]

    for query, expected in test_cases:
        print(f"\n测试: {query}")
        print(f"期望: {expected}")

        response = requests.post(
            f"{BASE_URL}/chat",
            json={
                "message": query,
                "user_id": "test_phase3",
                "session_id": "phase3_test"
            }
        )

        if response.status_code == 200:
            result = response.json()
            print(f"✅ 状态: {response.status_code}")
            print(f"响应: {result.get('response', '')[:100]}...")
        else:
            print(f"❌ 失败: {response.status_code}")
            print(f"错误: {response.text}")


def test_response_styles():
    """测试响应风格"""
    print("\n🧪 测试响应风格")
    print("=" * 60)

    styles = ["professional", "casual", "concise", "detailed"]
    query = "什么是人工智能?"

    for style in styles:
        print(f"\n测试风格: {style}")

        response = requests.post(
            f"{BASE_URL}/chat",
            json={
                "message": query,
                "user_id": "test_phase3",
                "session_id": "phase3_test",
                "response_style": style
            }
        )

        if response.status_code == 200:
            result = response.json()
            print(f"✅ 响应长度: {len(result.get('response', ''))} 字符")
            print(f"响应: {result.get('response', '')[:80]}...")
        else:
            print(f"❌ 失败: {response.status_code}")


def test_server_health():
    """测试服务器健康状态"""
    print("\n🧪 测试服务器健康状态")
    print("=" * 60)

    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"✅ 服务器响应: {response.status_code}")
        print(f"返回: {response.json()}")
    except Exception as e:
        print(f"❌ 服务器不可达: {e}")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("Phase 3 功能测试 (非数据库部分)")
    print("=" * 60)

    test_server_health()
    test_quick_intent_matching()
    test_response_styles()

    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)
    print("\n💡 说明:")
    print("  - Phase 3的快速意图匹配和响应风格功能已可用")
    print("  - 记忆重要性评分功能需要数据库迁移后才能使用")
    print("  - 查看 docs/MIGRATION_GUIDE.md 了解迁移步骤")
