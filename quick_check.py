#!/usr/bin/env python3
from datetime import datetime, timedelta
from db_setup import SessionLocal, ProactiveQuestion, Message
import sys
sys.path.insert(0, '/Users/rockts/Dev/xiaole-ai')


print("\n" + "="*60)
print("v0.7.0 实际测试结果")
print("="*60)

s = SessionLocal()

# 最近10分钟的追问
ten_min = datetime.now() - timedelta(minutes=10)
followups = s.query(ProactiveQuestion).filter(
    ProactiveQuestion.created_at >= ten_min
).order_by(ProactiveQuestion.created_at.desc()).all()

print(f"\n✅ 最近10分钟触发的追问数: {len(followups)}\n")

if followups:
    for i, fq in enumerate(followups, 1):
        print(f"【追问#{i}】")
        print(f"  类型: {fq.question_type}")
        print(f"  原问题: {fq.original_question[:40]}...")
        print(f"  追问: {fq.followup_question}")
        print(f"  置信度: {fq.confidence_score}")
        print(f"  时间: {fq.created_at.strftime('%H:%M:%S')}")
        print()
else:
    # 显示最近对话
    msgs = s.query(Message).filter(
        Message.created_at >= ten_min
    ).order_by(Message.created_at.desc()).limit(10).all()

    print(f"📝 最近10分钟对话数: {len(msgs)}")
    if msgs:
        print("\n最近的对话:")
        for msg in reversed(msgs[-6:]):
            role = "👤" if msg.role == "user" else "🤖"
            content = msg.content[:50]
            print(f"{role} {content}...")

s.close()
print("="*60 + "\n")
