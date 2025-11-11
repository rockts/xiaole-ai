#!/usr/bin/env python3
"""
测试主动问答完整流程
验证待追问和置信度功能
"""
import json
from datetime import datetime
from proactive_qa import ProactiveQA, SessionLocal, Message
import sys
sys.path.insert(0, '/Users/rockts/Dev/xiaole-ai')


def test_proactive_qa_flow():
    """测试主动问答流程"""
    print("=" * 60)
    print("🧪 测试主动问答功能（待追问 + 置信度）")
    print("=" * 60)

    qa = ProactiveQA()
    session = SessionLocal()

    # 创建测试会话
    test_session_id = "test_proactive_flow_001"
    test_user_id = "test_user"

    print("\n📝 清理旧测试数据...")
    session.query(Message).filter_by(session_id=test_session_id).delete()
    session.commit()

    # 场景1: 用户提问，AI回答不完整（包含"不知道"）
    print("\n📌 场景1: 不完整回答（包含'不知道'）")
    print("-" * 60)

    # 添加用户问题
    user_msg = Message(
        session_id=test_session_id,
        user_id=test_user_id,
        role="user",
        content="Python的异步编程是什么？",
        created_at=datetime.now()
    )
    session.add(user_msg)

    # 添加AI不完整回答
    ai_msg = Message(
        session_id=test_session_id,
        user_id=test_user_id,
        role="assistant",
        content="不太清楚具体细节，可能是用于处理并发的。",
        created_at=datetime.now()
    )
    session.add(ai_msg)
    session.commit()

    # 分析对话
    analysis = qa.analyze_conversation(test_session_id, test_user_id)

    print(f"✅ 需要追问: {analysis['needs_followup']}")
    if analysis['questions']:
        q = analysis['questions'][0]
        print(f"📋 原始问题: {q['question']}")
        print(f"🔍 缺失信息: {q['missing_info']}")
        print(f"📊 置信度: {q['confidence']}%")
        print(f"💬 AI回答: {q['ai_response']}")

        # 生成追问
        followup = qa.generate_followup_question(
            q['question'],
            q['missing_info'],
            q['ai_response']
        )
        print(f"💡 建议追问: {followup}")

        # 保存追问记录
        question_id = qa.save_proactive_question(
            session_id=test_session_id,
            user_id=test_user_id,
            original_question=q['question'],
            question_type=q['type'],
            missing_info=q['missing_info'],
            confidence=q['confidence'],
            followup_question=followup
        )
        print(f"💾 已保存记录ID: {question_id}")

    # 场景2: 回答过短（少于5个字）
    print("\n📌 场景2: 回答过短（高置信度）")
    print("-" * 60)

    user_msg2 = Message(
        session_id=test_session_id,
        user_id=test_user_id,
        role="user",
        content="Docker是什么？",
        created_at=datetime.now()
    )
    session.add(user_msg2)

    ai_msg2 = Message(
        session_id=test_session_id,
        user_id=test_user_id,
        role="assistant",
        content="容器",
        created_at=datetime.now()
    )
    session.add(ai_msg2)
    session.commit()

    analysis2 = qa.analyze_conversation(test_session_id, test_user_id)

    if analysis2['questions']:
        # 找到Docker相关的问题
        for q in analysis2['questions']:
            if 'Docker' in q['question']:
                print(f"📋 原始问题: {q['question']}")
                print(f"🔍 缺失信息: {q['missing_info']}")
                print(f"📊 置信度: {q['confidence']}% (回答过短应该很高)")

                followup2 = qa.generate_followup_question(
                    q['question'],
                    q['missing_info'],
                    q['ai_response']
                )
                print(f"💡 建议追问: {followup2}")

                question_id2 = qa.save_proactive_question(
                    session_id=test_session_id,
                    user_id=test_user_id,
                    original_question=q['question'],
                    question_type=q['type'],
                    missing_info=q['missing_info'],
                    confidence=q['confidence'],
                    followup_question=followup2
                )
                print(f"💾 已保存记录ID: {question_id2}")
                break

    # 查询待追问列表
    print("\n📋 查询待追问列表...")
    print("-" * 60)
    pending = qa.get_pending_followups(test_session_id, limit=10)

    if pending:
        print(f"✅ 找到 {len(pending)} 条待追问记录:")
        for idx, p in enumerate(pending, 1):
            print(f"\n{idx}. 原始问题: {p['question']}")
            print(f"   追问建议: {p['followup']}")
            print(f"   置信度: {p['confidence']}%")
            print(f"   创建时间: {p['created_at']}")
    else:
        print("❌ 没有待追问记录！")

    # 测试去重功能
    print("\n📌 场景3: 测试去重（同一问题不应重复保存）")
    print("-" * 60)

    # 再次保存相同问题
    duplicate_id = qa.save_proactive_question(
        session_id=test_session_id,
        user_id=test_user_id,
        original_question="Python的异步编程是什么？",
        question_type="incomplete",
        missing_info=["完整回答"],
        confidence=80,
        followup_question="关于'Python的异步编程是什么？'，您能说得更具体一些吗？"
    )

    # 再次查询
    pending_after = qa.get_pending_followups(test_session_id, limit=10)

    if len(pending_after) == len(pending):
        print(f"✅ 去重成功！仍然是 {len(pending_after)} 条记录")
        print(f"   返回的ID: {duplicate_id} (应该是已存在记录的ID)")
    else:
        print(f"❌ 去重失败！从 {len(pending)} 变成了 {len(pending_after)} 条")

    # 测试标记已追问
    print("\n📌 场景4: 标记追问已发送")
    print("-" * 60)

    if pending:
        first_id = pending[0]['id']
        print(f"标记问题ID {first_id} 为已追问...")
        qa.mark_followup_asked(first_id)

        # 验证
        pending_final = qa.get_pending_followups(test_session_id, limit=10)
        print(f"✅ 待追问列表更新: {len(pending)} -> {len(pending_final)} 条")

    # 查看历史记录
    print("\n📋 查看追问历史...")
    print("-" * 60)
    history = qa.get_followup_history(session_id=test_session_id, limit=10)

    if history:
        print(f"✅ 找到 {len(history)} 条历史记录:")
        for idx, h in enumerate(history, 1):
            status = "✅ 已追问" if h['followup_asked'] else "⏳ 待追问"
            print(f"\n{idx}. [{status}] 置信度: {h['confidence']}%")
            print(f"   原始: {h['original_question']}")
            print(f"   追问: {h['followup_question']}")
    else:
        print("❌ 没有历史记录！")

    session.close()

    print("\n" + "=" * 60)
    print("✅ 测试完成！")
    print("=" * 60)


if __name__ == "__main__":
    test_proactive_qa_flow()
