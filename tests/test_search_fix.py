#!/usr/bin/env python3
"""测试网络搜索功能是否正常"""
import requests
import json

BASE_URL = "http://localhost:8000"


def test_search_functionality():
    """测试搜索功能"""
    print("\n🔍 测试小乐的网络搜索功能")
    print("=" * 60)

    # 测试用例
    queries = [
        "搜索下iPhone 17 Pro最新价格",
        "帮我查一下2025年春节是几号",
        "搜索Python 3.13新特性"
    ]

    for query in queries:
        print(f"\n📝 测试查询: {query}")
        print("-" * 60)

        try:
            response = requests.post(
                f"{BASE_URL}/chat",
                json={
                    "message": query,
                    "user_id": "search_test",
                    "session_id": "search_test_session"
                },
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                answer = result.get('response', '')

                print(f"✅ 响应成功")
                print(f"📊 回复长度: {len(answer)} 字符")
                print(f"💬 回复内容:\n{answer[:200]}...")

                # 检查是否真的调用了搜索
                if "搜索" in answer or "查询" in answer or "找到" in answer:
                    print("✅ 似乎使用了搜索功能")
                else:
                    print("⚠️  未明确提及使用搜索")

            else:
                print(f"❌ 请求失败: {response.status_code}")
                print(f"错误: {response.text[:200]}")

        except Exception as e:
            print(f"❌ 异常: {e}")

    print("\n" + "=" * 60)
    print("测试完成!")


def check_tools_status():
    """检查工具列表"""
    print("\n🔧 检查已注册工具")
    print("=" * 60)

    try:
        response = requests.get(f"{BASE_URL}/tools/list")
        if response.status_code == 200:
            tools = response.json()
            print(f"✅ 共有 {len(tools)} 个工具:")
            for tool in tools:
                status = "✅" if tool.get('enabled', True) else "❌"
                print(
                    f"  {status} {tool.get('name')}: {tool.get('description', '')[:50]}...")

            # 检查search工具
            search_tool = next(
                (t for t in tools if t.get('name') == 'search'), None)
            if search_tool:
                print(f"\n✅ 搜索工具已注册: {search_tool}")
            else:
                print("\n❌ 搜索工具未找到")
        else:
            print(f"❌ 获取工具列表失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 异常: {e}")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("小乐网络搜索功能测试")
    print("=" * 60)

    check_tools_status()
    test_search_functionality()
