"""
调试主动问答功能
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from proactive_qa import ProactiveQA
from db_setup import SessionLocal, Message, ProactiveQuestion
from datetime import datetime


def test_analyze():
    """测试分析功能"""
    print("=" * 60)
    print("测试主动问答分析功能")
    print("=" * 60)
    
    proactive_qa = ProactiveQA()
    
    # 检查最近的会话
    session = SessionLocal()
    try:
        # 获取最近的会话
        recent_session = session.query(Message.session_id).order_by(
            Message.created_at.desc()
        ).first()
        
        if not recent_session:
            print("❌ 没有找到任何会话")
            return
        
        session_id = recent_session[0]
        print(f"\n检查会话: {session_id}")
        
        # 获取该会话的消息
        messages = session.query(Message).filter(
            Message.session_id == session_id
        ).order_by(Message.created_at.desc()).limit(10).all()
        
        print(f"\n找到 {len(messages)} 条消息:")
        for msg in reversed(messages[-5:]):  # 显示最后5条
            print(f"  [{msg.role}] {msg.content[:50]}...")
        
        # 测试分析
        print("\n执行分析...")
        analysis = proactive_qa.analyze_conversation(session_id, "default_user")
        
        print(f"\n分析结果:")
        print(f"  needs_followup: {analysis.get('needs_followup')}")
        print(f"  questions: {len(analysis.get('questions', []))} 个")
        
        if analysis.get("needs_followup"):
            for i, q in enumerate(analysis.get("questions", []), 1):
                print(f"\n  问题 {i}:")
                print(f"    原问题: {q.get('question', '')[:100]}")
                print(f"    类型: {q.get('type')}")
                print(f"    置信度: {q.get('confidence')}")
                print(f"    缺失信息: {q.get('missing_info', [])}")
        
        # 检查已保存的主动问答记录
        print("\n" + "=" * 60)
        print("检查已保存的主动问答记录")
        print("=" * 60)
        
        saved_questions = session.query(ProactiveQuestion).filter(
            ProactiveQuestion.user_id == "default_user",
            ProactiveQuestion.followup_asked == False
        ).order_by(ProactiveQuestion.created_at.desc()).limit(5).all()
        
        print(f"\n找到 {len(saved_questions)} 条待追问记录:")
        for q in saved_questions:
            print(f"\n  ID: {q.id}")
            print(f"    问题: {q.original_question[:80]}...")
            print(f"    类型: {q.question_type}")
            print(f"    置信度: {q.confidence_score}")
            print(f"    创建时间: {q.created_at}")
            if q.followup_question:
                print(f"    追问: {q.followup_question[:60]}...")
        
    finally:
        session.close()


if __name__ == "__main__":
    test_analyze()
