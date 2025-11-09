#!/usr/bin/env python3
"""最终清理 - 删除所有测试数据"""
import sys
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, '.')

from db_setup import Memory, Conversation, Message, UserBehavior, SessionLocal


def final_clean():
    s = SessionLocal()
    
    print("="*60)
    print("开始彻底清理测试数据")
    print("="*60)
    
    # 1. 查看当前状态
    before_total = s.query(Memory).count()
    before_facts = s.query(Memory).filter(Memory.tag == 'facts').count()
    print(f"\n清理前: 总记忆 {before_total}, facts {before_facts}")
    
    # 2. 删除所有包含测试关键词的记忆
    keywords = [
        '小明', 'test', '测试', '25岁', '篮球', '科幻',
        '3月15', '看电影', '5月20', '张三', '28岁', '上海',
        'Test', 'TEST', '喜欢打', '电影'
    ]
    
    deleted = 0
    for kw in keywords:
        result = s.query(Memory).filter(
            Memory.content.like(f'%{kw}%')
        ).delete(synchronize_session=False)
        if result > 0:
            deleted += result
            print(f"  删除包含 '{kw}': {result} 条")
    
    # 3. 删除test用户数据
    behav = s.query(UserBehavior).filter(
        UserBehavior.user_id.like('%test%')
    ).delete(synchronize_session=False)
    print(f"  删除test行为: {behav} 条")
    
    test_sessions = s.query(Conversation).filter(
        Conversation.user_id.like('%test%')
    ).all()
    
    msg_count = 0
    for sess in test_sessions:
        msg_count += s.query(Message).filter(
            Message.session_id == sess.session_id
        ).delete(synchronize_session=False)
    print(f"  删除test消息: {msg_count} 条")
    
    conv = s.query(Conversation).filter(
        Conversation.user_id.like('%test%')
    ).delete(synchronize_session=False)
    print(f"  删除test会话: {conv} 条")
    
    s.commit()
    
    # 4. 清理后统计
    after_total = s.query(Memory).count()
    after_facts = s.query(Memory).filter(Memory.tag == 'facts').count()
    
    print(f"\n清理后: 总记忆 {after_total}, facts {after_facts}")
    print(f"共删除记忆: {deleted} 条")
    
    # 5. 列出剩余facts
    remaining = s.query(Memory).filter(
        Memory.tag == 'facts'
    ).limit(10).all()
    
    if remaining:
        print(f"\n剩余facts记忆 (前10条):")
        for i, m in enumerate(remaining, 1):
            print(f"  {i}. {m.content[:70]}")
    else:
        print("\n✅ facts标签已清空")
    
    print("\n" + "="*60)
    print("清理完成")
    print("="*60)
    
    # 写入结果文件
    with open('/tmp/clean_result.txt', 'w', encoding='utf-8') as f:
        f.write(f'删除测试记忆: {deleted} 条\n')
        f.write(f'剩余总记忆: {after_total} 条\n')
        f.write(f'剩余facts: {after_facts} 条\n')
        f.write('清理完成\n')
    
    s.close()


if __name__ == '__main__':
    final_clean()

