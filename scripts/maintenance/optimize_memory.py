#!/usr/bin/env python3
"""
记忆数据库优化脚本
1. 删除无效记忆（错误识别、重复内容）
2. 合并碎片化信息
3. 修正错误数据
4. 清理过期 conversation
"""

from db_setup import SessionLocal, Memory
from datetime import datetime, timedelta


def optimize_memory():
    db = SessionLocal()
    try:
        print("="*80)
        print("开始优化记忆数据库")
        print("="*80)

        # 1. 删除无效图片识别记忆
        print("\n1️⃣ 删除无效图片识别记忆...")
        invalid_image_keywords = [
            '不是学生课程表',
            '不是课程表',
            '并非学生课程表',
            '不是一张学生课程表'
        ]

        deleted_count = 0
        for keyword in invalid_image_keywords:
            invalid_memories = db.query(Memory).filter(
                Memory.content.like(f'%{keyword}%')
            ).all()
            for mem in invalid_memories:
                print(f"   删除 ID {mem.id}: {mem.content[:60]}...")
                db.delete(mem)
                deleted_count += 1

        print(f"   ✅ 删除了 {deleted_count} 条无效图片记忆")

        # 2. 删除重复的"儿子：有"
        print("\n2️⃣ 删除重复facts...")
        duplicate_facts = db.query(Memory).filter(
            Memory.tag == 'facts',
            Memory.content == '儿子：有'
        ).all()

        if len(duplicate_facts) > 1:
            # 保留最新的一条，删除其他
            duplicate_facts.sort(key=lambda x: x.created_at, reverse=True)
            for mem in duplicate_facts[1:]:
                print(f"   删除重复 ID {mem.id}: {mem.content}")
                db.delete(mem)

        print(
            f"   ✅ 清理了 {len(duplicate_facts)-1 if len(duplicate_facts) > 1 else 0} 条重复facts")

        # 3. 删除过期体重数据
        print("\n3️⃣ 删除过期数据...")
        old_weight = db.query(Memory).filter(
            Memory.tag == 'facts',
            Memory.content.like('%体重：160斤%')
        ).all()

        for mem in old_weight:
            print(f"   删除过期 ID {mem.id}: {mem.content[:50]}")
            db.delete(mem)

        print(f"   ✅ 删除了 {len(old_weight)} 条过期数据")

        # 4. 修正错误的用户姓名
        print("\n4️⃣ 修正错误数据...")
        wrong_user_name = db.query(Memory).filter(
            Memory.id == 150
        ).first()

        if wrong_user_name:
            print(f"   删除错误记录 ID 150: {wrong_user_name.content[:50]}")
            db.delete(wrong_user_name)

        # 5. 清理7天前的 conversation 记忆
        print("\n5️⃣ 清理旧 conversation 记忆...")
        seven_days_ago = datetime.now() - timedelta(days=7)
        old_conversations = db.query(Memory).filter(
            Memory.tag.like('conversation:%'),
            Memory.created_at < seven_days_ago
        ).all()

        print(f"   发现 {len(old_conversations)} 条超过7天的conversation")
        if len(old_conversations) > 0:
            response = input("   是否删除这些旧conversation? (y/n): ")
            if response.lower() == 'y':
                for mem in old_conversations:
                    db.delete(mem)
                print(f"   ✅ 删除了 {len(old_conversations)} 条旧conversation")
            else:
                print("   ⏭️ 跳过删除旧conversation")

        # 6. 合并碎片化的学校信息
        print("\n6️⃣ 检查需要合并的信息...")
        school_facts = db.query(Memory).filter(
            Memory.tag == 'facts',
            Memory.content.like('%学校%')
        ).all()

        if len(school_facts) > 2:
            print(f"   发现 {len(school_facts)} 条学校相关facts，建议手动合并")
            for fact in school_facts[:3]:
                print(f"     ID {fact.id}: {fact.content[:60]}")

        # 提交所有更改
        db.commit()

        print("\n" + "="*80)
        print("✅ 记忆数据库优化完成！")
        print("="*80)

        # 统计优化后的数据
        total_memories = db.query(Memory).count()
        facts_count = db.query(Memory).filter(Memory.tag == 'facts').count()
        conversations_count = db.query(Memory).filter(
            Memory.tag.like('conversation:%')).count()

        print(f"\n当前记忆统计:")
        print(f"  总记忆数: {total_memories}")
        print(f"  Facts: {facts_count}")
        print(f"  Conversations: {conversations_count}")

    except Exception as e:
        print(f"\n❌ 错误: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == '__main__':
    optimize_memory()
