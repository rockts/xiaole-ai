#!/usr/bin/env python3
"""直接用psycopg2删除最后3条"""
import psycopg2

conn = psycopg2.connect(
    dbname='xiaole_ai',
    user='xiaole_user',
    password='xiaole_password',
    host='192.168.88.188',
    port=5432
)

cur = conn.cursor()

# 查询删除前
cur.execute('SELECT COUNT(*) FROM memories')
before = cur.fetchone()[0]
print(f'删除前总数: {before}')

# 查询最后10条
cur.execute('SELECT id, tag, content FROM memories ORDER BY id DESC LIMIT 10')
rows = cur.fetchall()
print('\n最后10条:')
for i, (id, tag, content) in enumerate(rows, 1):
    print(f'{i}. [ID={id}] {tag}: {content[:60]}')

# 获取最后3条的ID
cur.execute('SELECT id FROM memories ORDER BY id DESC LIMIT 3')
ids = [row[0] for row in cur.fetchall()]
print(f'\n将删除ID: {ids}')

# 删除
if ids:
    placeholders = ','.join(['%s'] * len(ids))
    cur.execute(f'DELETE FROM memories WHERE id IN ({placeholders})', ids)
    conn.commit()
    print(f'✅ 已删除 {cur.rowcount} 条')

# 查询删除后
cur.execute('SELECT COUNT(*) FROM memories')
after = cur.fetchone()[0]
print(f'\n删除后总数: {after}')
print(f'实际删除: {before - after} 条')

# 显示新的最后5条
cur.execute('SELECT id, tag, content FROM memories ORDER BY id DESC LIMIT 5')
rows = cur.fetchall()
print('\n现在的最后5条:')
for i, (id, tag, content) in enumerate(rows, 1):
    print(f'{i}. [ID={id}] {tag}: {content[:60]}')

cur.close()
conn.close()
