#!/usr/bin/env python3
"""
检查最近的对话是否触发追问分析
"""
import psycopg2
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# 使用与db_setup.py相同的连接参数
conn = psycopg2.connect(
    host=os.getenv("DB_HOST", "192.168.31.200"),
    port=int(os.getenv("DB_PORT", 5432)),
    database=os.getenv("DB_NAME", "xiaole_ai"),
    user=os.getenv("DB_USER", "xiaole"),
    password=os.getenv("DB_PASSWORD", "xiaole123")
)
cursor = conn.cursor()

print("=" * 60)
print("检查最近的对话")
print("=" * 60)

# 查询最近的会话
cursor.execute("""
    SELECT session_id, user_id, created_at
    FROM conversations
    ORDER BY created_at DESC
    LIMIT 5
""")

sessions = cursor.fetchall()
print(f"\n找到 {len(sessions)} 个最近会话:\n")

for session_id, user_id, created_at in sessions:
    print(f"📝 Session: {session_id}")
    print(f"   用户: {user_id}")
    print(f"   时间: {created_at}")

    # 查询消息
    cursor.execute("""
        SELECT role, content
        FROM messages
        WHERE session_id = %s
        ORDER BY timestamp DESC
        LIMIT 3
    """, (session_id,))

    messages = cursor.fetchall()
    print(f"   消息数: {len(messages)}")
    for role, content in messages[:2]:
        preview = content[:50].replace('\n', ' ')
        print(f"   [{role}] {preview}...")

    # 查询是否有追问记录
    cursor.execute("""
        SELECT id, followup_question, confidence, followup_asked
        FROM proactive_questions
        WHERE session_id = %s
        ORDER BY created_at DESC
        LIMIT 1
    """, (session_id,))

    followup = cursor.fetchone()
    if followup:
        fid, fq, conf, asked = followup
        print(f"   ✅ 有追问记录 (ID={fid}, 置信度={conf}, 已发送={asked})")
        print(f"      {fq[:60]}...")
    else:
        print(f"   ⚠️  无追问记录")

    print()

conn.close()
