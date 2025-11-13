#!/usr/bin/env python3
from datetime import datetime, timedelta
from db_setup import SessionLocal, ProactiveQuestion, Message
import sys
sys.path.insert(0, '/Users/rockts/Dev/xiaole-ai')

output = []
output.append("="*70)
output.append("v0.7.0 测试结果")
output.append("="*70)

s = SessionLocal()
ten_min = datetime.now() - timedelta(minutes=10)

fqs = s.query(ProactiveQuestion).filter(
    ProactiveQuestion.created_at >= ten_min).all()
msgs = s.query(Message).filter(Message.created_at >=
                               ten_min).order_by(Message.created_at.asc()).all()

output.append(f"\n对话数: {len(msgs)}")
output.append(f"追问数: {len(fqs)}\n")

if fqs:
    output.append("✅ 追问记录:")
    for i, fq in enumerate(fqs, 1):
        output.append(
            f"\n[{i}] {fq.question_type} (置信度{fq.confidence_score}%)")
        output.append(f"    原问题: {fq.original_question[:40]}")
        output.append(f"    追问: {fq.followup_question}")

if msgs:
    output.append("\n\n最近对话:")
    for m in msgs[-10:]:
        role = "USER" if m.role == "user" else "AI"
        cont = str(m.content)[:50]
        output.append(f"  {role}: {cont}")

with open('/Users/rockts/Dev/xiaole-ai/test_result.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(output))

s.close()
print("结果已保存到 test_result.txt")
