#!/usr/bin/env python3
from sqlalchemy import func
from db_setup import Session, Conversation
import sys
import os
sys.path.insert(0, 'backend')
os.chdir('backend')


session = Session()

# 查询特定会话
target_id = '34d04148-d90a-4938-bfb7-ad712fea3fb2'
conv = session.query(Conversation).filter(
    Conversation.session_id == target_id
).first()

if conv:
    print(f'✅ 找到会话:')
    print(f'   Session ID: {conv.session_id}')
    print(f'   Title: {conv.title}')
    print(f'   User ID: {conv.user_id}')
    print(f'   Created: {conv.created_at}')
    print(f'   Updated: {conv.updated_at}')
else:
    print(f'❌ 未找到会话 {target_id}')

# 统计各user_id的会话数
user_counts = session.query(
    Conversation.user_id,
    func.count(Conversation.session_id)
).group_by(Conversation.user_id).all()

print(f'\n会话统计:')
for user_id, count in user_counts:
    print(f'  {user_id}: {count}条')

session.close()
