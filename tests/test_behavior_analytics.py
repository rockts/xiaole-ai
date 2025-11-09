"""
测试用户行为分析功能 - v0.3.0
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"


def test_behavior_analytics():
    """测试行为分析完整流程"""
    print("=" * 60)
    print("🧪 测试 v0.3.0 用户行为分析功能")
    print("=" * 60)

    # 1. 发起多次对话生成数据
    print("\n📝 Step 1: 生成测试数据（3次对话）...")
    user_id = "test_user_behavior"
    prompts = [
        "你好，我是小明，今年25岁，喜欢打篮球",
        "我还喜欢看电影，尤其是科幻片",
        "对了，我的生日是3月15日"
    ]

    session_ids = []
    for i, prompt in enumerate(prompts, 1):
        try:
            resp = requests.post(
                f"{BASE_URL}/chat",
                params={"prompt": prompt, "user_id": user_id},
                timeout=15
            )
            if resp.status_code == 200:
                data = resp.json()
                session_id = data.get("session_id", "unknown")
                session_ids.append(session_id)
                print(f"  ✅ 对话{i}: {session_id[:8]}...")
            else:
                print(f"  ❌ 对话{i}失败: {resp.status_code}")
        except Exception as e:
            print(f"  ❌ 对话{i}异常: {e}")

        time.sleep(1)  # 避免请求过快

    # 2. 查询行为分析报告
    print(f"\n📊 Step 2: 查询用户行为分析报告...")
    try:
        resp = requests.get(
            f"{BASE_URL}/analytics/behavior",
            params={"user_id": user_id, "days": 7}
        )
        if resp.status_code == 200:
            report = resp.json()

            # 对话统计
            if "conversation_stats" in report:
                print("\n  📈 对话统计:")
                stats = report["conversation_stats"]
                print(f"    总会话数: {stats.get('total_sessions', 0)}")
                print(f"    总消息数: {stats.get('total_messages', 0)}")
                print(f"    用户消息数: {stats.get('total_user_messages', 0)}")
                print(f"    平均每会话消息数: "
                      f"{stats.get('avg_messages_per_session', 0)}")
                print(f"    平均消息长度: {stats.get('avg_message_length', 0)}")
                print(f"    总时长: {stats.get('total_duration_minutes', 0)} 分钟")

            # 活跃模式
            if "activity_pattern" in report:
                print("\n  ⏰ 活跃时间模式:")
                pattern = report["activity_pattern"]
                print(f"    总会话数: {pattern.get('total_sessions', 0)}")
                print(f"    最活跃时段: {pattern.get('most_active_hour', 'N/A')}点")
                print(f"    最活跃日: {pattern.get('most_active_day', 'N/A')}")
                if pattern.get('hourly_distribution'):
                    print(f"    小时分布: "
                          f"{list(pattern['hourly_distribution'].keys())[:5]}...")

            # 话题偏好
            if "topic_preferences" in report:
                print("\n  🏷️  话题偏好:")
                topics = report["topic_preferences"]
                if topics and topics.get('top_topics'):
                    print(f"    总话题数: {topics.get('total_topics', 0)}")
                    print("    高频话题:")
                    for topic, count in topics['top_topics'][:5]:
                        print(f"      - {topic}: {count}次")
                else:
                    print("    （暂无话题数据）")

            print("\n✅ 行为分析测试通过!")

        else:
            print(f"  ❌ 查询失败: {resp.status_code}")
            print(f"  响应: {resp.text}")

    except Exception as e:
        print(f"  ❌ 查询异常: {e}")

    # 3. 测试单独的API端点
    print("\n🔍 Step 3: 测试单独的分析端点...")

    try:
        # 活跃模式
        resp = requests.get(
            f"{BASE_URL}/analytics/activity",
            params={"user_id": user_id}
        )
        if resp.status_code == 200:
            print("  ✅ /analytics/activity - 正常")
        else:
            print(f"  ❌ /analytics/activity - {resp.status_code}")

        # 话题偏好
        resp = requests.get(
            f"{BASE_URL}/analytics/topics",
            params={"user_id": user_id}
        )
        if resp.status_code == 200:
            print("  ✅ /analytics/topics - 正常")
        else:
            print(f"  ❌ /analytics/topics - {resp.status_code}")

    except Exception as e:
        print(f"  ❌ 测试异常: {e}")

    print("\n" + "=" * 60)
    print("🎉 测试完成!")
    print("=" * 60)


if __name__ == "__main__":
    test_behavior_analytics()
