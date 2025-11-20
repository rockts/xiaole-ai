#!/usr/bin/env python3
"""测试会话导出修复"""

from conversation import ConversationManager
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend"))


def test_export_fix():
    """测试导出数据格式"""
    conv = ConversationManager()

    # 获取最近的会话
    sessions = conv.get_recent_sessions(limit=1)

    if not sessions:
        print("❌ 没有会话数据")
        return

    session_id = sessions[0]['session_id']
    print(f"📝 测试会话: {session_id}")

    # 获取会话历史
    history = conv.get_history(session_id, limit=5)

    print(f"\n✅ 获取到 {len(history)} 条消息")

    # 检查消息格式
    if history:
        msg = history[0]
        print(f"\n消息格式检查:")
        print(f"  - role: {'✅' if 'role' in msg else '❌'}")
        print(f"  - content: {'✅' if 'content' in msg else '❌'}")
        print(f"  - timestamp: {'✅' if 'timestamp' in msg else '❌'}")
        print(f"  - created_at: {'✅' if 'created_at' in msg else '❌'}")

        print(f"\n示例消息:")
        print(f"  Role: {msg.get('role')}")
        print(f"  Content: {msg.get('content')[:50]}...")
        print(f"  Timestamp: {msg.get('timestamp')}")

    # 测试会话统计
    stats = conv.get_session_stats(session_id)
    if stats:
        print(f"\n会话统计:")
        print(f"  标题: {stats['title']}")
        print(f"  消息数: {stats['message_count']}")
        print(f"  创建时间: {stats['created_at']}")


if __name__ == "__main__":
    test_export_fix()
