#!/usr/bin/env python3
"""检查测试效果 - 查看实际触发的追问记录"""
from datetime import datetime, timedelta
from db_setup import SessionLocal, Message, ProactiveQuestion
from proactive_qa import ProactiveQA
import sys
sys.path.insert(0, '/Users/rockts/Dev/xiaole-ai')


def check_recent_followups():
    """检查最近的追问记录"""
    print("\n" + "="*80)
    print("📊 v0.7.0 实际测试效果分析")
    print("="*80 + "\n")

    qa = ProactiveQA()
    session = SessionLocal()

    try:
        # 1. 查看最近10分钟的对话
        ten_min_ago = datetime.now() - timedelta(minutes=10)
        recent_messages = session.query(Message).filter(
            Message.created_at >= ten_min_ago
        ).order_by(Message.created_at.desc()).limit(50).all()

        print(f"📝 最近10分钟内的对话数: {len(recent_messages)}")
        if recent_messages:
            print(f"   最新消息时间: {recent_messages[0].created_at}")
            print(f"   最早消息时间: {recent_messages[-1].created_at}")
        print()

        # 2. 查看最近的追问记录
        recent_followups = session.query(ProactiveQuestion).filter(
            ProactiveQuestion.created_at >= ten_min_ago
        ).order_by(ProactiveQuestion.created_at.desc()).all()

        print(f"🎯 最近10分钟触发的追问数: {len(recent_followups)}")
        print()

        if not recent_followups:
            print("⚠️  没有检测到追问记录")
            print("   可能原因:")
            print("   1. 对话内容没有触发追问条件")
            print("   2. 冷却时间限制（30秒间隔）")
            print("   3. 检测到用户不耐烦")
            print("   4. 对话长度不足（需要用户问+AI答的完整轮次）")
            print()

            # 显示最近的对话内容
            print("💬 最近5条对话:")
            for i, msg in enumerate(recent_messages[:5], 1):
                role = "👤用户" if msg.role == "user" else "🤖AI"
                content = msg.content[:60] + \
                    "..." if len(msg.content) > 60 else msg.content
                print(f"   {i}. {role}: {content}")
        else:
            print("✅ 成功触发追问！详细记录:\n")

            for i, fq in enumerate(recent_followups, 1):
                print(f"【追问 #{i}】")
                print(f"   类型: {fq.question_type}")
                print(f"   原问题: {fq.original_question[:50]}...")
                print(f"   追问内容: {fq.followup_question}")
                print(f"   置信度: {fq.confidence_score}")
                print(f"   是否已发送: {'✅是' if fq.followup_asked else '❌否'}")
                print(f"   触发时间: {fq.created_at}")
                print()

        # 3. 统计各类型追问
        if recent_followups:
            type_counts = {}
            for fq in recent_followups:
                type_counts[fq.question_type] = type_counts.get(
                    fq.question_type, 0) + 1

            print("📈 追问类型统计:")
            for qtype, count in type_counts.items():
                type_name = {
                    'incomplete': '不完整回答',
                    'knowledge_gap': '知识空白',
                    'memory_conflict': '信息冲突',
                    'task_feedback': '任务反馈'
                }.get(qtype, qtype)
                print(f"   {type_name}: {count}次")
            print()

        # 4. 检查最近session的对话分析
        if recent_messages:
            latest_session = recent_messages[0].session_id
            print(f"🔍 分析最新会话 (session_id={latest_session[:20]}...):")

            analysis = qa.analyze_conversation(latest_session)
            print(f"   需要追问: {'✅是' if analysis['needs_followup'] else '❌否'}")
            print(f"   检测到的问题数: {len(analysis['questions'])}")

            if analysis['questions']:
                print("\n   检测到的追问点:")
                for i, q in enumerate(analysis['questions'][:3], 1):
                    print(f"      {i}. 类型={q['type']}, 置信度={q['confidence']}")
                    if 'reason' in q:
                        print(f"         原因: {q['reason']}")

        print("\n" + "="*80)
        print("✅ 分析完成")
        print("="*80 + "\n")

    finally:
        session.close()


if __name__ == "__main__":
    check_recent_followups()
