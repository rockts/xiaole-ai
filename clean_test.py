#!/usr/bin/env python3
"""通过MemoryManager API清理测试数据"""

import sys
sys.path.insert(0, '.')

from db_setup import Memory, Conversation, Message, UserBehavior, SessionLocal


def clean():
    session = SessionLocal()
    
    try:
        print("\n" + "="*60)
        print("开始清理测试数据...")
        print("="*60)
        
        # 1. 删除test用户的行为数据
        count = session.query(UserBehavior).filter(
            UserBehavior.user_id.like('%test%')
        ).delete(synchronize_session=False)
        print(f"✓ 删除行为记录: {count} 条")
        
        # 2. 删除test用户的消息
        test_sessions = session.query(Conversation).filter(
            Conversation.user_id.like('%test%')
        ).all()
        session_ids = [s.session_id for s in test_sessions]
        
        if session_ids:
            count = session.query(Message).filter(
                Message.session_id.in_(session_ids)
            ).delete(synchronize_session=False)
            print(f"✓ 删除消息记录: {count} 条")
        
        # 3. 删除test用户的会话
        count = session.query(Conversation).filter(
            Conversation.user_id.like('%test%')
        ).delete(synchronize_session=False)
        print(f"✓ 删除会话记录: {count} 条")
        
        # 4. 删除测试记忆（包含测试关键词）
        keywords = [
            '小明', 'test', '测试', '25岁', '篮球', 
            '科幻', '3月15', '看电影', '5月20', '张三', '28岁', '上海'
        ]
        deleted = 0
        for kw in keywords:
            count = session.query(Memory).filter(
                Memory.content.like(f'%{kw}%')
            ).delete(synchronize_session=False)
            deleted += count
        print(f"✓ 删除测试记忆: {deleted} 条")
        
        session.commit()
        print("\n" + "="*60)
        print("✅ 清理完成")
        print("="*60)
        
        # 显示统计
        print("\n当前数据库统计:")
        print(f"  记忆总数: {session.query(Memory).count()}")
        print(f"  会话总数: {session.query(Conversation).count()}")
        print(f"  消息总数: {session.query(Message).count()}")
        print(f"  行为记录: {session.query(UserBehavior).count()}")
        
        # 显示facts记忆
        facts = session.query(Memory).filter(
            Memory.tag == 'facts'
        ).order_by(Memory.created_at.desc()).limit(10).all()
        
        if facts:
            print(f"\nfacts标签最近{len(facts)}条记忆:")
            for i, m in enumerate(facts, 1):
                print(f"  {i}. {m.content[:60]}...")
        else:
            print("\nfacts标签: 无记忆")
        
        print()
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        session.rollback()
    finally:
        session.close()


if __name__ == '__main__':
    clean()

