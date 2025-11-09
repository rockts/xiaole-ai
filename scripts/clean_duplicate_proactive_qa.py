"""
清理主动问答历史中的重复记录
保留每个问题的最新记录，删除旧的重复项
"""
from collections import defaultdict
from proactive_qa import SessionLocal, ProactiveQuestion
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def clean_duplicates(dry_run=True):
    """
    清理重复的主动问答记录

    Args:
        dry_run: 如果为True，只显示将要删除的记录，不实际删除
    """
    session = SessionLocal()

    try:
        # 获取所有未回答的问题
        all_records = (
            session.query(ProactiveQuestion)
            .filter_by(followup_asked=False)
            .order_by(ProactiveQuestion.created_at.desc())
            .all()
        )

        print(f"📊 总共找到 {len(all_records)} 条未回答的主动问答记录")

        # 按 user_id + original_question 分组
        grouped = defaultdict(list)
        for record in all_records:
            key = (record.user_id, record.original_question)
            grouped[key].append(record)

        # 找出重复记录
        duplicates_to_delete = []
        duplicate_groups = 0

        for key, records in grouped.items():
            if len(records) > 1:
                duplicate_groups += 1
                user_id, question = key
                # 保留最新的记录（第一个），其余标记为待删除
                keep = records[0]
                to_delete = records[1:]

                print(f"\n❌ 发现重复: {question[:50]}...")
                print(f"   用户: {user_id}")
                print(f"   保留: ID={keep.id}, Created={keep.created_at}")
                print(f"   删除: {len(to_delete)} 条旧记录")

                for r in to_delete:
                    print(f"     - ID={r.id}, Created={r.created_at}")
                    duplicates_to_delete.append(r.id)

        print(f"\n{'='*60}")
        print(f"📈 统计:")
        print(f"  - 重复的问题组: {duplicate_groups}")
        print(f"  - 待删除记录数: {len(duplicates_to_delete)}")
        print(f"  - 清理后剩余: {len(all_records) - len(duplicates_to_delete)}")

        if not duplicates_to_delete:
            print("\n✅ 没有发现重复记录，数据库很干净！")
            return 0

        if dry_run:
            print(f"\n⚠️  这是预览模式，没有实际删除数据")
            print(f"💡 要执行删除，请运行: python {sys.argv[0]} --execute")
            return len(duplicates_to_delete)

        # 实际删除
        print(f"\n🗑️  开始删除重复记录...")
        deleted = session.query(ProactiveQuestion).filter(
            ProactiveQuestion.id.in_(duplicates_to_delete)
        ).delete(synchronize_session=False)

        session.commit()
        print(f"✅ 成功删除 {deleted} 条重复记录")
        return deleted

    except Exception as e:
        session.rollback()
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return -1
    finally:
        session.close()


if __name__ == "__main__":
    # 检查命令行参数
    execute = "--execute" in sys.argv or "-e" in sys.argv

    if execute:
        print("⚠️  执行模式：将实际删除重复记录")
        print("按 Ctrl+C 取消，或等待3秒继续...")
        import time
        try:
            time.sleep(3)
        except KeyboardInterrupt:
            print("\n取消操作")
            sys.exit(0)
    else:
        print("🔍 预览模式：只显示重复记录，不删除")

    print("="*60)

    result = clean_duplicates(dry_run=not execute)

    if result > 0 and not execute:
        sys.exit(1)  # 有重复记录但未执行删除
    elif result < 0:
        sys.exit(2)  # 发生错误
    else:
        sys.exit(0)  # 成功或无重复
