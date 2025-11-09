#!/usr/bin/env python3
"""强制清理所有测试数据 - 使用SQL直接删除"""
import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

# 连接数据库
conn = psycopg2.connect(
    host=os.getenv('DB_HOST'),
    port=os.getenv('DB_PORT'),
    database=os.getenv('DB_NAME'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASS')
)

cur = conn.cursor()

print("强制清理测试数据...")

# 删除test用户数据
cur.execute("DELETE FROM user_behaviors WHERE user_id LIKE '%test%'")
print(f"删除行为记录: {cur.rowcount}")

cur.execute("DELETE FROM messages WHERE session_id IN (SELECT session_id FROM conversations WHERE user_id LIKE '%test%')")
print(f"删除消息: {cur.rowcount}")

cur.execute("DELETE FROM conversations WHERE user_id LIKE '%test%'")
print(f"删除会话: {cur.rowcount}")

# 删除测试记忆
keywords = ['小明', 'test', '测试', '25岁', '篮球', '科幻',
            '3月15', '看电影', '5月20', '张三', '28岁', '上海']
total = 0
for kw in keywords:
    cur.execute(f"DELETE FROM memories WHERE content LIKE %s", (f'%{kw}%',))
    total += cur.rowcount

print(f"删除测试记忆: {total}")

conn.commit()

# 查看剩余
cur.execute("SELECT COUNT(*) FROM memories")
print(f"\n剩余记忆: {cur.fetchone()[0]}")

cur.execute("SELECT COUNT(*) FROM conversations")
print(f"剩余会话: {cur.fetchone()[0]}")

cur.close()
conn.close()

print("\n✅ 清理完成")
