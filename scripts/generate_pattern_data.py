"""
生成测试数据验证模式学习功能
"""
import requests
import time

# API基础URL
API_BASE = "http://127.0.0.1:8000"

# 测试消息（模拟不同类型的用户问题）
test_messages = [
    # 天气查询（重复多次以增加频次）
    "今天天气怎么样？",
    "明天天气好吗？",
    "这周末天气如何？",
    "今天会下雨吗？",
    "明天温度多少度？",

    # 时间日期
    "现在几点了？",
    "今天是几月几号？",
    "今天星期几？",
    "今天是什么日子？",

    # 个人信息
    "你叫什么名字？",
    "你是谁？",
    "你是什么？",
    "你能做什么？",

    # 功能咨询
    "你有什么功能？",
    "你能帮我做什么？",
    "怎么使用你？",
    "如何设置提醒？",

    # 推荐建议
    "推荐一部电影",
    "有什么好书推荐吗？",
    "今天吃什么好？",
    "周末去哪玩？",

    # 闲聊
    "你好",
    "今天过得怎么样？",
    "聊聊天吧",
    "无聊了",

    # 高频词汇测试（重复使用某些词）
    "帮我查一下天气",
    "帮我设置一个提醒",
    "帮我推荐电影",
    "帮我查询资料",
    "今天天气预报",
    "今天日程安排",
    "今天新闻",
]


def send_message(message, session_id=None):
    """发送消息到小乐"""
    url = f"{API_BASE}/chat"
    data = {
        "prompt": message,
        "user_id": "test_user"
    }
    if session_id:
        data["session_id"] = session_id

    try:
        response = requests.post(url, json=data)
        if response.status_code == 200:
            result = response.json()
            print(f"✓ 发送: {message}")
            return result.get("session_id")
        else:
            print(f"✗ 错误: {response.status_code}")
            return None
    except Exception as e:
        print(f"✗ 异常: {e}")
        return None


def check_patterns():
    """检查学习到的模式"""
    print("\n" + "="*60)
    print("📊 模式学习统计")
    print("="*60)

    try:
        # 获取学习洞察
        response = requests.get(
            f"{API_BASE}/patterns/insights?user_id=test_user"
        )
        if response.status_code == 200:
            insights = response.json()
            print("\n【统计概览】")
            stats = insights.get("statistics", {})
            print(f"总学习模式: {stats.get('total_patterns', 0)}")
            print(f"高频词汇数: {stats.get('frequent_words_count', 0)}")
            print(f"常见问题数: {stats.get('common_questions_count', 0)}")

        # 获取高频词
        response = requests.get(
            f"{API_BASE}/patterns/frequent?user_id=test_user&limit=15"
        )
        if response.status_code == 200:
            data = response.json()
            words = data.get("frequent_words", [])
            if words:
                print("\n【高频词汇 TOP15】")
                for i, item in enumerate(words, 1):
                    print(f"{i}. {item['word']} - "
                          f"{item['frequency']}次 "
                          f"(置信度: {item.get('confidence', 0)})")

        # 获取常见问题
        response = requests.get(
            f"{API_BASE}/patterns/common_questions?user_id=test_user&limit=10"
        )
        if response.status_code == 200:
            data = response.json()
            questions = data.get("common_questions", [])
            if questions:
                print("\n【常见问题分类】")
                for item in questions:
                    print(f"\n{item['category']} - {item['frequency']}次")
                    examples = item.get("examples", [])
                    if examples:
                        for example in examples[:3]:
                            print(f"  • {example}")

    except Exception as e:
        print(f"查询失败: {e}")


def main():
    print("=" * 60)
    print("🧠 小乐AI - 模式学习功能测试")
    print("=" * 60)
    print(f"将发送 {len(test_messages)} 条测试消息...")
    print()

    session_id = None
    for i, message in enumerate(test_messages, 1):
        print(f"[{i}/{len(test_messages)}] ", end="")
        session_id = send_message(message, session_id)
        time.sleep(0.3)  # 避免请求过快

    print("\n✓ 所有测试消息发送完毕！")

    # 稍等片刻让数据处理完成
    time.sleep(2)

    # 检查学习结果
    check_patterns()

    print("\n" + "=" * 60)
    print("✓ 测试完成！请在浏览器中打开行为分析页面查看完整展示")
    print("=" * 60)


if __name__ == "__main__":
    main()
