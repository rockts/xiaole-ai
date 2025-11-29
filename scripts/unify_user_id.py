"""
统一更新所有表的 user_id 为当前登录用户
v0.9.0 - 2025-11-29
"""
from sqlalchemy import text
from backend.db_setup import (
    SessionLocal, Conversation, UserBehavior, ProactiveQuestion,
    LearnedPattern, ToolExecution, FaceEncoding
)
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def get_current_user():
    """获取当前登录用户（默认是 admin）"""
    return "admin"


def unify_user_id():
    """将所有表的 user_id 统一更新为当前登录用户"""
    session = SessionLocal()
    target_user_id = get_current_user()

    try:
        # 统计各表当前的 user_id 分布
        print(f"\n🔍 目标用户: {target_user_id}")
        print("\n📊 当前各表 user_id 分布:")
        print("-" * 60)

        # Conversations
        conv_count = session.query(Conversation).count()
        conv_other = session.query(Conversation).filter(
            Conversation.user_id != target_user_id
        ).count()
        print(f"conversations: {conv_count} 条记录, {conv_other} 条需要更新")

        # UserBehaviors
        behavior_count = session.query(UserBehavior).count()
        behavior_other = session.query(UserBehavior).filter(
            UserBehavior.user_id != target_user_id
        ).count()
        print(f"user_behaviors: {behavior_count} 条记录, {behavior_other} 条需要更新")

        # ProactiveQuestions
        pq_count = session.query(ProactiveQuestion).count()
        pq_other = session.query(ProactiveQuestion).filter(
            ProactiveQuestion.user_id != target_user_id
        ).count()
        print(f"proactive_questions: {pq_count} 条记录, {pq_other} 条需要更新")

        # LearnedPatterns
        pattern_count = session.query(LearnedPattern).count()
        pattern_other = session.query(LearnedPattern).filter(
            LearnedPattern.user_id != target_user_id
        ).count()
        print(f"learned_patterns: {pattern_count} 条记录, {pattern_other} 条需要更新")

        # ToolExecutions
        tool_count = session.query(ToolExecution).count()
        tool_other = session.query(ToolExecution).filter(
            ToolExecution.user_id != target_user_id
        ).count()
        print(f"tool_executions: {tool_count} 条记录, {tool_other} 条需要更新")

        # FaceEncodings
        face_count = session.query(FaceEncoding).count()
        face_other = session.query(FaceEncoding).filter(
            FaceEncoding.user_id != target_user_id
        ).count()
        print(f"face_encodings: {face_count} 条记录, {face_other} 条需要更新")

        total_to_update = (
            conv_other + behavior_other + pq_other +
            pattern_other + tool_other + face_other
        )

        if total_to_update == 0:
            print("\n✅ 所有表的 user_id 已经统一,无需更新")
            return

        print(f"\n⚠️  共需更新 {total_to_update} 条记录")
        confirm = input(f"\n确认将所有 user_id 更新为 '{target_user_id}'? (yes/no): ")

        if confirm.lower() != 'yes':
            print("❌ 操作已取消")
            return

        print("\n🔄 开始更新...")

        # 执行更新
        updated = []

        if conv_other > 0:
            session.query(Conversation).filter(
                Conversation.user_id != target_user_id
            ).update({Conversation.user_id: target_user_id})
            updated.append(f"conversations: {conv_other}")

        if behavior_other > 0:
            session.query(UserBehavior).filter(
                UserBehavior.user_id != target_user_id
            ).update({UserBehavior.user_id: target_user_id})
            updated.append(f"user_behaviors: {behavior_other}")

        if pq_other > 0:
            session.query(ProactiveQuestion).filter(
                ProactiveQuestion.user_id != target_user_id
            ).update({ProactiveQuestion.user_id: target_user_id})
            updated.append(f"proactive_questions: {pq_other}")

        if pattern_other > 0:
            session.query(LearnedPattern).filter(
                LearnedPattern.user_id != target_user_id
            ).update({LearnedPattern.user_id: target_user_id})
            updated.append(f"learned_patterns: {pattern_other}")

        if tool_other > 0:
            session.query(ToolExecution).filter(
                ToolExecution.user_id != target_user_id
            ).update({ToolExecution.user_id: target_user_id})
            updated.append(f"tool_executions: {tool_other}")

        if face_other > 0:
            session.query(FaceEncoding).filter(
                FaceEncoding.user_id != target_user_id
            ).update({FaceEncoding.user_id: target_user_id})
            updated.append(f"face_encodings: {face_other}")

        session.commit()

        print("\n✅ 更新完成:")
        for item in updated:
            print(f"  - {item}")

        print(f"\n🎉 所有表的 user_id 已统一为 '{target_user_id}'")

    except Exception as e:
        session.rollback()
        print(f"\n❌ 更新失败: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    unify_user_id()
