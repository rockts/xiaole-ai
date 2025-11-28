#!/usr/bin/env python3
from backend.conversation import ConversationManager
import sys
sys.path.insert(0, 'backend')


conv = ConversationManager()

# 检查特定会话
session_id = '34d04148-d90a-4938-bfb7-ad712fea3fb2'
stats = conv.get_session_stats(session_id)

if stats:
    print(f'✅ 找到会话: {stats["title"]}')
    print(f'   消息数: {stats["message_count"]}')
    print(f'   创建时间: {stats["created_at"]}')
else:
    print(f'❌ 未找到会话 {session_id}')

# 获取最新会话
recent = conv.get_recent_sessions('default_user', limit=5)
print(f'\n最新5条会话:')
for s in recent:
    print(f'  - {s["title"][:40]} ({s.get("updated_at", s.get("created_at"))})')
