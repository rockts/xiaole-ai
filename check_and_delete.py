#!/usr/bin/env python3
"""查看并删除最后3条记忆"""
from db_setup import Memory, SessionLocal
import sys
sys.path.insert(0, '.')


OUTPUT = '/tmp/xiaole_delete_result.txt'

with open(OUTPUT, 'w', encoding='utf-8') as f:
    s = SessionLocal()

    f.write('=== 删除前 ===\n')
    total_before = s.query(Memory).count()
    f.write(f'总记忆数: {total_before}\n\n')

    last_10 = s.query(Memory).order_by(Memory.id.desc()).limit(10).all()
    f.write('最后10条记忆:\n')
    for i, m in enumerate(last_10, 1):
        f.write(f'{i}. [ID={m.id}] {m.tag}: {m.content[:80]}\n')

    # 获取最后3条
    last_3 = s.query(Memory).order_by(Memory.id.desc()).limit(3).all()

    if last_3:
        f.write(f'\n=== 删除最后3条 ===\n')
        ids_to_delete = [m.id for m in last_3]
        f.write(f'将删除ID: {ids_to_delete}\n')

        for m in last_3:
            s.delete(m)
        s.commit()
        f.write('✅ 删除完成\n')
    else:
        f.write('\n没有记录可删除\n')

    f.write('\n=== 删除后 ===\n')
    total_after = s.query(Memory).count()
    f.write(f'总记忆数: {total_after}\n')
    f.write(f'已删除: {total_before - total_after} 条\n\n')

    new_last = s.query(Memory).order_by(Memory.id.desc()).limit(5).all()
    f.write('现在的最后5条:\n')
    for i, m in enumerate(new_last, 1):
        f.write(f'{i}. [ID={m.id}] {m.tag}: {m.content[:80]}\n')

    s.close()

print(f'结果已写入: {OUTPUT}')
