"""
测试主动对话功能
"""
import asyncio
from proactive_chat import ProactiveChat
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


async def test_proactive_chat():
    """测试主动对话触发条件"""
    print("🧪 测试主动对话功能\n")

    proactive_chat = ProactiveChat()

    # 测试1: 检查是否应该发起对话
    print("=" * 60)
    print("测试1: 检查触发条件")
    print("=" * 60)

    result = proactive_chat.should_initiate_chat("default_user")

    print(f"\n是否应该发起对话: {result['should_chat']}")
    if result['should_chat']:
        print(f"触发原因: {result['reason']}")
        print(f"优先级: {result['priority']}")
        print(f"消息内容: {result['message']}")
        if 'metadata' in result:
            print(f"元数据: {result['metadata']}")
    else:
        print("当前无触发条件")

    # 测试2: 获取统计信息
    print("\n" + "=" * 60)
    print("测试2: 获取统计信息")
    print("=" * 60)

    stats = proactive_chat.get_chat_statistics("default_user", days=30)

    print(f"\n最近30天消息数: {stats['message_count_30d']}")
    print(f"待追问问题数: {stats['pending_questions']}")
    print(f"距上次聊天天数: {stats['days_since_last_chat']}")
    print(f"建议发起对话: {stats['should_initiate']}")

    print("\n✅ 测试完成")


if __name__ == "__main__":
    asyncio.run(test_proactive_chat())
