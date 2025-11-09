#!/usr/bin/env python3
"""
清理测试数据脚本
删除测试过程中产生的记忆、会话和行为数据
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# 数据库连接
if os.getenv('DATABASE_URL'):
    DB_URL = os.getenv('DATABASE_URL')
else:
    DB_URL = (
        f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASS')}"
        f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}"
        f"/{os.getenv('DB_NAME')}"
    )

engine = create_engine(DB_URL)
SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()


def clean_test_data():
    """清理所有测试数据"""
    print("\n" + "="*60)
    print("🧹 清理测试数据")
    print("="*60)
    
    # 1. 查看并删除test_user相关的数据
    print("\n1️⃣  清理测试用户数据...")
    
    # 删除test_user的行为记录
    result = session.execute(
        text("DELETE FROM user_behaviors WHERE user_id LIKE '%test%'")
    )
    print(f"   ✅ 删除行为记录: {result.rowcount} 条")
    
    # 删除test_user的会话
    result = session.execute(
        text("DELETE FROM conversations WHERE user_id LIKE '%test%'")
    )
    print(f"   ✅ 删除会话记录: {result.rowcount} 条")
    
    # 删除test相关的消息
    result = session.execute(
        text("""
            DELETE FROM messages 
            WHERE session_id IN (
                SELECT session_id FROM conversations 
                WHERE user_id LIKE '%test%'
            )
        """)
    )
    print(f"   ✅ 删除消息记录: {result.rowcount} 条")
    
    # 2. 查看facts标签的记忆
    print("\n2️⃣  查看facts标签记忆...")
    result = session.execute(
        text("SELECT id, content, created_at FROM memories WHERE tag='facts' ORDER BY created_at DESC LIMIT 20")
    )
    memories = result.fetchall()
    
    if memories:
        print(f"\n   最近20条facts记忆:")
        for i, (id, content, created_at) in enumerate(memories, 1):
            print(f"   {i}. [{id}] {content[:60]}... ({created_at.strftime('%m-%d %H:%M')})")
        
        # 询问是否删除
        print("\n   📋 发现的测试相关记忆（包含'小明'、'test'等）:")
        test_memories = [
            (id, content) for id, content, _ in memories 
            if any(keyword in content for keyword in ['小明', 'test', '测试', '25岁', '篮球', '科幻'])
        ]
        
        if test_memories:
            print(f"\n   找到 {len(test_memories)} 条可能的测试记忆:")
            for id, content in test_memories[:10]:
                print(f"   - [{id}] {content[:60]}")
            
            # 自动删除测试记忆
            test_ids = [id for id, _ in test_memories]
            if test_ids:
                placeholders = ', '.join([':id' + str(i) for i in range(len(test_ids))])
                params = {f'id{i}': test_ids[i] for i in range(len(test_ids))}
                result = session.execute(
                    text(f"DELETE FROM memories WHERE id IN ({placeholders})"),
                    params
                )
                print(f"\n   ✅ 删除测试记忆: {result.rowcount} 条")
        else:
            print("   ✅ 未发现明显的测试记忆")
    else:
        print("   ℹ️  facts标签无记忆")
    
    # 3. 清理orphan消息（会话已删除但消息还在）
    print("\n3️⃣  清理孤立消息...")
    result = session.execute(
        text("""
            DELETE FROM messages 
            WHERE session_id NOT IN (SELECT session_id FROM conversations)
        """)
    )
    print(f"   ✅ 删除孤立消息: {result.rowcount} 条")
    
    # 提交所有更改
    session.commit()
    
    print("\n" + "="*60)
    print("✅ 清理完成!")
    print("="*60)
    
    # 4. 显示清理后的统计
    print("\n📊 当前数据库统计:")
    
    result = session.execute(text("SELECT COUNT(*) FROM memories"))
    print(f"   记忆总数: {result.scalar()}")
    
    result = session.execute(text("SELECT COUNT(*) FROM conversations"))
    print(f"   会话总数: {result.scalar()}")
    
    result = session.execute(text("SELECT COUNT(*) FROM messages"))
    print(f"   消息总数: {result.scalar()}")
    
    result = session.execute(text("SELECT COUNT(*) FROM user_behaviors"))
    print(f"   行为记录: {result.scalar()}")
    
    print()


def show_current_data():
    """显示当前数据概况"""
    print("\n📊 数据库概况:")
    print("-"*60)
    
    # 记忆统计
    result = session.execute(
        text("SELECT tag, COUNT(*) FROM memories GROUP BY tag")
    )
    print("\n记忆（按标签）:")
    for tag, count in result.fetchall():
        print(f"  {tag}: {count} 条")
    
    # 用户统计
    result = session.execute(
        text("SELECT user_id, COUNT(*) FROM conversations GROUP BY user_id")
    )
    print("\n会话（按用户）:")
    for user_id, count in result.fetchall():
        print(f"  {user_id}: {count} 个")
    
    print()


if __name__ == "__main__":
    try:
        # 先显示当前数据
        show_current_data()
        
        # 执行清理
        clean_test_data()
        
        # 再次显示数据
        show_current_data()
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        session.rollback()
    finally:
        session.close()
