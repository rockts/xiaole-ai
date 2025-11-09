#!/usr/bin/env python3
"""删除memories表最后3条记录"""
from db_setup import Memory, SessionLocal
import sys
sys.path.insert(0, '.')


s = SessionLocal()

# 获取最后3条记录的ID
last_3 = s.query(Memory).order_by(Memory.id.desc()).limit(3).all()

if not last_3:
    print('数据库中没有记录')
    s.close()
    exit(0)

print('准备删除最后3条记录:')
for i, m in enumerate(last_3, 1):
    print(f'{i}. ID={m.id}, tag={m.tag}, content={m.content[:60]}...')

# 删除
count = 0
for m in last_3:
    s.delete(m)
    count += 1

s.commit()

print(f'\n✅ 成功删除 {count} 条记录')

# 显示剩余统计
total = s.query(Memory).count()
print(f'剩余记忆总数: {total}')

# 显示新的最后3条
print('\n现在的最后3条记录:')
new_last = s.query(Memory).order_by(Memory.id.desc()).limit(3).all()
for i, m in enumerate(new_last, 1):
    print(f'{i}. ID={m.id}, tag={m.tag}, content={m.content[:60]}...')

s.close()
