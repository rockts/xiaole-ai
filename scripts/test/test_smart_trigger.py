#!/usr/bin/env python3
"""
测试智能触发器功能
验证知识空白检测、信息冲突检测、任务反馈检测
"""
from memory import MemoryManager
from proactive_qa import SmartTrigger
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


def test_knowledge_gap():
    """测试知识空白检测"""
    print("\n===== 测试1: 知识空白检测 =====")

    mm = MemoryManager()
    trigger = SmartTrigger(mm)

    # 场景1: 模糊回答
    question1 = "明天天气怎么样？"
    answer1 = "可能会下雨吧，不太确定"
    has_gap, gap_type = trigger.detect_knowledge_gap(question1, answer1)
    print(f"场景1: {question1}")
    print(f"回答: {answer1}")
    print(f"结果: 知识空白={has_gap}, 类型={gap_type}\n")

    # 场景2: 回答过简
    question2 = "Python如何读取CSV文件并处理数据？"
    answer2 = "用pandas"
    has_gap, gap_type = trigger.detect_knowledge_gap(question2, answer2)
    print(f"场景2: {question2}")
    print(f"回答: {answer2}")
    print(f"结果: 知识空白={has_gap}, 类型={gap_type}\n")

    # 场景3: 缺少时间信息
    question3 = "项目什么时候能完成？"
    answer3 = "快了，正在进行中"
    has_gap, gap_type = trigger.detect_knowledge_gap(question3, answer3)
    print(f"场景3: {question3}")
    print(f"回答: {answer3}")
    print(f"结果: 知识空白={has_gap}, 类型={gap_type}\n")

    # 场景4: 完整回答（对照组）
    question4 = "怎么做红烧肉？"
    answer4 = "首先准备五花肉500克，切块后冷水下锅焯水去腥。然后热锅凉油，放入冰糖炒糖色，加入肉块翻炒上色。最后加入生抽、老抽、料酒，炖煮1小时即可。"
    has_gap, gap_type = trigger.detect_knowledge_gap(question4, answer4)
    print(f"场景4（对照组）: {question4}")
    print(f"回答: {answer4}")
    print(f"结果: 知识空白={has_gap}, 类型={gap_type}\n")


def test_memory_conflict():
    """测试信息冲突检测"""
    print("\n===== 测试2: 信息冲突检测 =====")

    mm = MemoryManager()
    trigger = SmartTrigger(mm)

    # 先存储一些记忆
    print("先存储历史记忆...")
    mm.remember(content="我喜欢咖啡", tag="facts")

    # 测试冲突检测
    new_fact1 = "我不喜欢咖啡"
    has_conflict, old_fact = trigger.detect_memory_conflict(new_fact1)
    print(f"\n新信息: {new_fact1}")
    print(f"结果: 冲突={has_conflict}, 旧信息={old_fact}\n")

    # 测试不冲突
    new_fact2 = "我喜欢茶"
    has_conflict, old_fact = trigger.detect_memory_conflict(new_fact2)
    print(f"新信息: {new_fact2}")
    print(f"结果: 冲突={has_conflict}, 旧信息={old_fact}\n")


def test_task_feedback():
    """测试任务反馈检测"""
    print("\n===== 测试3: 任务反馈检测 =====")

    from db_setup import Message
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from dotenv import load_dotenv
    load_dotenv()

    # 使用与proactive_qa.py相同的数据库连接逻辑
    if os.getenv('DATABASE_URL'):
        DB_URL = os.getenv('DATABASE_URL')
    else:
        DB_URL = (
            f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASS')}"
            f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}"
            f"/{os.getenv('DB_NAME')}"
        )

    engine = create_engine(
        DB_URL,
        connect_args={'client_encoding': 'utf8'}
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    session = SessionLocal()

    try:
        # 获取一个真实的session_id（有消息记录的）
        latest_msg = session.query(Message).order_by(
            Message.created_at.desc()
        ).first()

        if not latest_msg:
            print("数据库中没有消息记录，跳过此测试")
            return

        test_session_id = latest_msg.session_id

        mm = MemoryManager()
        trigger = SmartTrigger(mm)

        needs_feedback, task_desc = trigger.detect_task_feedback_missing(
            test_session_id
        )
        print(f"测试会话ID: {test_session_id}")
        print(f"结果: 需要反馈={needs_feedback}, 任务={task_desc}\n")

        # 显示该会话最近5条消息
        recent_msgs = session.query(Message).filter(
            Message.session_id == test_session_id
        ).order_by(Message.created_at.desc()).limit(5).all()

        print("最近5条消息：")
        for msg in reversed(recent_msgs):
            role_label = "用户" if msg.role == "user" else "小乐"
            content_preview = msg.content[:50] + \
                "..." if len(msg.content) > 50 else msg.content
            print(f"  [{role_label}] {content_preview}")

    finally:
        session.close()


def test_full_analysis():
    """测试完整分析流程"""
    print("\n===== 测试4: 完整分析流程 =====")

    from proactive_qa import ProactiveQA
    from db_setup import Message
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from dotenv import load_dotenv
    load_dotenv()

    # 使用与proactive_qa.py相同的数据库连接逻辑
    if os.getenv('DATABASE_URL'):
        DB_URL = os.getenv('DATABASE_URL')
    else:
        DB_URL = (
            f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASS')}"
            f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}"
            f"/{os.getenv('DB_NAME')}"
        )

    engine = create_engine(
        DB_URL,
        connect_args={'client_encoding': 'utf8'}
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    session = SessionLocal()

    try:
        # 获取最近的session
        latest_msg = session.query(Message).order_by(
            Message.created_at.desc()
        ).first()

        if not latest_msg:
            print("数据库中没有消息记录，跳过此测试")
            return

        test_session_id = latest_msg.session_id

        qa = ProactiveQA()
        result = qa.analyze_conversation(test_session_id)

        print(f"测试会话ID: {test_session_id}")
        print(f"需要追问: {result['needs_followup']}")
        print(f"问题数量: {len(result['questions'])}\n")

        if result['questions']:
            print("检测到的问题：")
            for i, q in enumerate(result['questions'][:3], 1):  # 只显示前3个
                print(f"\n问题{i}:")
                print(f"  原始问题: {q.get('question', 'N/A')[:50]}...")
                print(f"  类型: {q.get('type')}")
                print(f"  置信度: {q.get('confidence')}")
                print(f"  缺失信息: {q.get('missing_info')}")
                if 'reason' in q:
                    print(f"  原因: {q['reason']}")

                # 生成追问
                followup = qa.generate_followup_question(
                    q['question'],
                    q.get('missing_info', []),
                    q.get('ai_response', ''),
                    q.get('type', 'incomplete'),
                    q.get('reason', '')
                )
                print(f"  追问: {followup}")

    finally:
        session.close()


if __name__ == "__main__":
    print("开始测试智能触发器...")
    print("=" * 50)

    try:
        test_knowledge_gap()
        test_memory_conflict()
        test_task_feedback()
        test_full_analysis()

        print("\n" + "=" * 50)
        print("所有测试完成！")

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
