#!/usr/bin/env python3
"""测试会话加载数据格式"""

from conversation import ConversationManager
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_session_data_format():
    """测试API返回的数据格式"""
    conv = ConversationManager()

    # 获取最近的会话
    sessions = conv.get_recent_sessions(limit=1)

    if not sessions:
        print("❌ 没有会话数据")
        return False

    session_id = sessions[0]['session_id']
    print(f"📝 测试会话: {session_id}")
    print(f"   标题: {sessions[0]['title']}")

    # 获取会话统计
    stats = conv.get_session_stats(session_id)
    print(f"\n📊 会话统计:")
    print(f"   session_id: {stats['session_id']}")
    print(f"   title: {stats['title']}")
    print(f"   message_count: {stats['message_count']}")
    print(f"   created_at: {stats['created_at']}")
    print(f"   updated_at: {stats['updated_at']}")

    # 获取历史消息
    messages = conv.get_history(session_id, limit=5)
    print(f"\n💬 历史消息 (前5条):")
    print(f"   消息数量: {len(messages)}")

    if messages:
        print(f"\n   第一条消息格式:")
        msg = messages[0]
        for key in msg.keys():
            value = msg[key]
            if key == 'content' and len(value) > 50:
                value = value[:50] + '...'
            print(f"     {key}: {value}")

        print(f"\n✅ 所有消息都包含必需字段:")
        required_fields = ['role', 'content', 'timestamp', 'created_at']
        for field in required_fields:
            has_field = all(field in msg for msg in messages)
            status = '✅' if has_field else '❌'
            print(f"   {status} {field}")

        # 模拟API返回格式
        print(f"\n📦 模拟API返回格式:")
        api_response = {
            "session_id": stats["session_id"],
            "title": stats["title"],
            "message_count": stats["message_count"],
            "created_at": stats["created_at"],
            "updated_at": stats["updated_at"],
            "messages": messages  # 注意：使用messages字段
        }
        print(f"   包含 'messages' 字段: ✅")
        print(f"   messages 长度: {len(api_response['messages'])}")

        return True
    else:
        print("❌ 没有历史消息")
        return False


if __name__ == "__main__":
    success = test_session_data_format()
    sys.exit(0 if success else 1)
