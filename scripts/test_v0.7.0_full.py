#!/usr/bin/env python3
"""
v0.7.0 完整功能测试
测试所有新功能：智能追问、冲突检测优化、情感感知、学习层
"""
from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from db_setup import Message
from learning import LearningManager
from memory import MemoryManager
from proactive_qa import ProactiveQA, SmartTrigger
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


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

engine = create_engine(DB_URL, connect_args={'client_encoding': 'utf8'})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def test_enhanced_conflict_detection():
    """测试优化后的冲突检测"""
    print("\n" + "=" * 60)
    print("测试1: 增强冲突检测（语义相似度）")
    print("=" * 60)

    mm = MemoryManager()
    trigger = SmartTrigger(mm)

    # 测试语义冲突（不同说法，含义相反）
    mm.remember(content="我非常喜欢喝咖啡", tag="facts")

    test_cases = [
        ("我讨厌咖啡", True, "情感相反"),
        ("我不太想喝咖啡", True, "态度相反"),
        ("我想喝茶", False, "不冲突"),
        ("咖啡很好喝", False, "不冲突"),
    ]

    for new_fact, expected, desc in test_cases:
        has_conflict, old_fact = trigger.detect_memory_conflict(new_fact)
        status = "✅" if (has_conflict == expected) else "❌"
        print(f"{status} {desc}: '{new_fact}'")
        print(
            f"   冲突={has_conflict}, 旧信息={old_fact[:20] if old_fact else 'N/A'}...")

    print()


def test_emotion_detection():
    """测试情感感知"""
    print("\n" + "=" * 60)
    print("测试2: 情感感知（不耐烦检测）")
    print("=" * 60)

    session = SessionLocal()

    try:
        # 获取最近的session_id
        latest = session.query(Message).order_by(
            Message.created_at.desc()
        ).first()

        if not latest:
            print("⚠️ 没有消息记录，跳过测试")
            return

        test_session_id = latest.session_id

        mm = MemoryManager()
        trigger = SmartTrigger(mm)

        is_impatient, reason = trigger.detect_user_impatience(test_session_id)

        print(f"测试会话: {test_session_id[:20]}...")
        print(f"是否不耐烦: {is_impatient}")
        if reason:
            print(f"原因: {reason}")

        # 显示最近3条用户消息
        recent = session.query(Message).filter(
            Message.session_id == test_session_id,
            Message.role == "user"
        ).order_by(Message.created_at.desc()).limit(3).all()

        print("\n最近用户消息:")
        for msg in reversed(recent):
            preview = msg.content[:30].replace('\n', ' ')
            print(f"  - {preview}...")

    finally:
        session.close()

    print()


def test_learning_layer():
    """测试学习层"""
    print("\n" + "=" * 60)
    print("测试3: 学习层（知识追踪）")
    print("=" * 60)

    lm = LearningManager()

    # 添加测试知识
    print("📚 添加知识点...")
    lm.add_knowledge(
        user_id="test_user_v0.7",
        topic="AI知识",
        content="大语言模型使用Transformer架构",
        mastery_level=0.7,
        related_topics=["机器学习", "深度学习"]
    )
    lm.add_knowledge(
        user_id="test_user_v0.7",
        topic="AI知识",
        content="RAG是检索增强生成的缩写",
        mastery_level=0.4
    )

    # 查询学习进度
    print("\n📊 学习进度:")
    progress = lm.get_learning_progress("test_user_v0.7")
    for p in progress:
        print(f"  主题: {p['topic']}")
        print(f"  进度: {p['progress']}%")
        print(f"  掌握: {p['mastered']}/{p['total_knowledge']}")

    # 检测知识空白
    print("\n🔍 知识空白:")
    gaps = lm.get_knowledge_gaps("test_user_v0.7")
    for gap in gaps[:3]:
        print(f"  - {gap['content'][:40]}...")
        print(f"    掌握度: {gap['mastery_level']:.0%}")

    # 推荐话题
    print("\n💡 推荐话题:")
    recommendations = lm.recommend_topics("test_user_v0.7")
    for rec in recommendations:
        print(f"  - {rec['topic']}: {rec['reason']}")

    lm.close()
    print()


def test_integrated_qa():
    """测试集成后的智能追问"""
    print("\n" + "=" * 60)
    print("测试4: 集成智能追问（完整流程）")
    print("=" * 60)

    session = SessionLocal()

    try:
        # 获取最近的session_id
        latest = session.query(Message).order_by(
            Message.created_at.desc()
        ).first()

        if not latest:
            print("⚠️ 没有消息记录，跳过测试")
            return

        test_session_id = latest.session_id

        qa = ProactiveQA()
        result = qa.analyze_conversation(test_session_id)

        print(f"会话: {test_session_id[:20]}...")
        print(f"需要追问: {result['needs_followup']}")
        print(f"检测到 {len(result['questions'])} 个追问点")

        if result['questions']:
            print("\n📋 追问详情:")
            for i, q in enumerate(result['questions'][:3], 1):
                print(f"\n{i}. 类型: {q.get('type')}")
                print(f"   置信度: {q.get('confidence')}")
                print(f"   原问题: {q.get('question', '')[:40]}...")

                # 生成追问
                followup = qa.generate_followup_question(
                    q.get('question', ''),
                    q.get('missing_info', []),
                    q.get('ai_response', ''),
                    q.get('type', 'incomplete'),
                    q.get('reason', '')
                )
                print(f"   追问: {followup}")

    finally:
        session.close()

    print()


def main():
    print("=" * 60)
    print("🚀 小乐 v0.7.0 完整功能测试")
    print("=" * 60)

    try:
        test_enhanced_conflict_detection()
        test_emotion_detection()
        test_learning_layer()
        test_integrated_qa()

        print("\n" + "=" * 60)
        print("✅ 所有测试完成！")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
