#!/usr/bin/env python3
"""通过MemoryManager API清理测试数据"""

import sys
sys.path.insert(0, '.')

from db_setup import Memory, Conversation, Message, UserBehavior, SessionLocal

def clean():
    session = SessionLocal()
    
    try:
        print("\n开始清理测试数据...")
        
        # 1. 删除test用户的行为数据
        count = session.query(UserBehavior).filter(
            UserBehavior.user_id.like('%test%')
        ).delete(synchronize_session=False)
        print(f"删除行为记录: {count} 条")
        
        # 2. 删除test用户的消息
        test_sessions = session.query(Conversation).filter(
            Conversation.user_id.like('%test%')
        ).all()
        session_ids = [s.session_id for s in test_sessions]
        
        if session_ids:
            count = session.query(Message).filter(
                Message.session_id.in_(session_ids)
            ).delete(synchronize_session=False)
            print(f"删除消息记录: {count} 条")
        
        # 3. 删除test用户的会话
        count = session.query(Conversation).filter(
            Conversation.user_id.like('%test%')
        ).delete(synchronize_session=False)
        print(f"删除会话记录: {count} 条")
        
        # 4. 删除测试记忆
        keywords = ['小明', 'test', '测试', '25岁', '篮球', '科幻', '3月15']
        deleted = 0
        for kw in keywords:
            count = session.query(Memory).filter(
                Memory.content.like(f'%{kw}%')
            ).delete(synchronize_session=False)
            deleted += count
        print(f"删除测试记忆: {deleted} 条")
        
        session.commit()
        print("\n✅ 清理完成")
        
        # 显示统计
        print("\n当前数据统计:")
        print(f"  记忆总数: {session.query(Memory).count()}")
        print(f"  会话总数: {session.query(Conversation).count()}")
        print(f"  消息总数: {session.query(Message).count()}")
        print(f"  行为记录: {session.query(UserBehavior).count()}")
        
    except Exception as e:
        print(f"错误: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == '__main__':
    clean()
