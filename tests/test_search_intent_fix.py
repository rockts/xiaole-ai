#!/usr/bin/env python3
"""
测试搜索意图识别修复效果
"""
import requests
import json
import time


def test_search_intent():
    """测试搜索意图是否能正确触发"""
    print("="*70)
    print("🔍 测试搜索意图识别修复效果")
    print("="*70)

    # 等待服务器完全启动
    time.sleep(2)

    test_cases = [
        {
            "query": "iPhone 17 Pro Max什么时候发布的",
            "should_search": True,
            "reason": "包含'iphone 17'和'发布'关键词"
        },
        {
            "query": "搜索Python最新版本",
            "should_search": True,
            "reason": "明确的搜索请求"
        },
        {
            "query": "2025年春节是几号",
            "should_search": True,
            "reason": "包含'2025年'时间关键词"
        },
        {
            "query": "iPhone 16 Pro Max最新价格",
            "should_search": True,
            "reason": "包含'iphone 16'和'最新价格'"
        },
        {
            "query": "什么是Python",
            "should_search": False,
            "reason": "普通知识问答,不需要搜索"
        },
    ]

    for i, test in enumerate(test_cases, 1):
        print(f"\n测试 {i}/{len(test_cases)}")
        print(f"查询: {test['query']}")
        print(f"预期: {'应该搜索' if test['should_search'] else '不需要搜索'}")
        print(f"原因: {test['reason']}")
        print("-"*70)

        try:
            response = requests.post(
                f"http://localhost:8000/chat?prompt={test['query']}",
                json={
                    "session_id": f"test_intent_{i}",
                    "user_id": "test_user"
                },
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                reply = data.get('reply', '')

                # 检查是否调用了搜索
                # 搜索结果通常包含"搜索结果"、"链接"、"🔗"等标记
                used_search = any(keyword in reply for keyword in [
                    '搜索', '找到', '🔗', 'http', '链接', '结果'
                ])

                if used_search == test['should_search']:
                    print(f"✅ 通过! {'调用了搜索' if used_search else '没有搜索'}")
                else:
                    print(f"❌ 失败! 预期{test['should_search']}, 实际{used_search}")

                print(f"回复预览: {reply[:150]}...")
            else:
                print(f"❌ 请求失败: {response.status_code}")

        except Exception as e:
            print(f"❌ 异常: {e}")

        time.sleep(1)  # 避免请求过快

    print("\n" + "="*70)
    print("测试完成!")
    print("="*70)


if __name__ == "__main__":
    test_search_intent()
