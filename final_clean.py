#!/usr/bin/env python3
"""最终清理 - 删除所有测试数据"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, '.')

from db_setup import Memory, Conversation, Message, UserBehavior, SessionLocal

def final_clean():
    s = SessionLocal()
    
    # 删除所有包含测试关键词的记忆
    keywords = [
        '小明', 'test', '测试', '25岁', '篮球', '科幻',
        '3月15', '看电影', '5月20', '张三', '28岁', '上海',
        'Test', 'TEST'
    ]
    
    deleted = 0
    for kw in keywords:
        result = s.query(Memory).filter(Memory.content.like(f'%{kw}%')).delete(synchronize_session=False)
        deleted += result
    
    # 删除test用户
    s.query(UserBehavior).filter(UserBehavior.user_id.like('%test%')).delete(synchronize_session=False)
    
    test_sessions = s.query(Conversation).filter(Conversation.user_id.like('%test%')).all()
    for sess in test_sessions:
        s.query(Message).filter(Message.session_id == sess.session_id).delete(synchronize_session=False)
    s.query(Conversation).filter(Conversation.user_id.like('%test%')).delete(synchronize_session=False)
    
    s.commit()
    
    # 统计
    total = s.query(Memory).count()
    facts = s.query(Memory).filter(Memory.tag == 'facts').count()
    
    with open('/tmp/clean_result.txt', 'w') as f:
        f.write(f'删除测试记忆: {deleted} 条\n')
        f.write(f'剩余总记忆: {total} 条\n')
        f.write(f'剩余facts: {facts} 条\n')
        f.write('清理完成\n')
    
    print(f'删除: {deleted}, 剩余: {total}')
    s.close()

if __name__ == '__main__':
    final_clean()
