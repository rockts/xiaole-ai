#!/usr/bin/env python3
"""快速检查测试结果"""
import os
import sys

# 添加项目路径
sys.path.insert(0, '/Users/rockts/Dev/xiaole-ai')
os.chdir('/Users/rockts/Dev/xiaole-ai')

try:
    from db_setup import SessionLocal, ProactiveQuestion, Message
    from datetime import datetime, timedelta

    s = SessionLocal()
    ten_min_ago = datetime.now() - timedelta(minutes=10)

    # 查询最近追问
    recent_followups = s.query(ProactiveQuestion).filter(
        ProactiveQuestion.created_at >= ten_min_ago
    ).all()

    # 查询最近消息
    recent_msgs = s.query(Message).filter(
        Message.created_at >= ten_min_ago
    ).order_by(Message.created_at.asc()).all()

    print("\n" + "="*70)
    print("📊 v0.7.0 实际测试结果分析")
    print("="*70 + "\n")

    print(f"📝 最近10分钟对话数: {len(recent_msgs)}")
    print(f"🎯 触发的追问数: {len(recent_followups)}\n")

    if recent_followups:
        print("✅ 成功触发追问！\n")
        for i, fq in enumerate(recent_followups, 1):
            print(f"【追问 #{i}】")
            print(f"   类型: {fq.question_type}")
            print(f"   原始问题: {fq.original_question[:45]}...")
            print(f"   追问内容: {fq.followup_question}")
            print(f"   置信度: {fq.confidence_score}%")
            print(f"   触发时间: {fq.created_at.strftime('%H:%M:%S')}\n")
    else:
        print("⚠️  未触发追问\n")

        if recent_msgs:
            print("最近对话记录:")
            for msg in recent_msgs[-8:]:
                role = "👤用户" if msg.role == "user" else "🤖AI  "
                content = msg.content[:55] + \
                    "..." if len(msg.content) > 55 else msg.content
                time_str = msg.created_at.strftime('%H:%M:%S')
                print(f"  [{time_str}] {role}: {content}")

            print("\n💡 可能原因:")
            print("  1. 回答都很完整，未触发知识空白检测")
            print("  2. 没有前后矛盾的说法，未触发冲突检测")
            print("  3. 冷却时间限制（30秒间隔）")
            print("  4. 用户表达了不耐烦，系统自动停止追问")
        else:
            print("💡 未检测到最近10分钟的对话")

    print("\n" + "="*70 + "\n")

    s.close()

except Exception as e:
    print(f"\n❌ 错误: {e}")
    import traceback
    traceback.print_exc()
