#!/usr/bin/env python3
from db_setup import Memory, SessionLocal
import sys
sys.path.insert(0, '.')

s = SessionLocal()

# 查看所有记忆
all_mems = s.query(Memory).all()
print(f'数据库总记忆数: {len(all_mems)}\n')

# 查看facts记忆
facts = s.query(Memory).filter(Memory.tag == 'facts').all()
print(f'Facts记忆数: {len(facts)}')

if facts:
    print('\nFacts记忆内容:')
    for i, m in enumerate(facts, 1):
        print(f'{i}. [{m.id}] {m.content}')

    # 询问是否删除
    print(f'\n发现测试关键词的记忆:')
    test_keywords = ['小明', 'test', '测试', '25岁', '篮球', '科幻',
                     '3月15', '看电影', '5月20', '张三', '28岁', '上海']

    to_delete = []
    for m in facts:
        for kw in test_keywords:
            if kw in m.content:
                to_delete.append(m)
                print(f'  - [{m.id}] {m.content}')
                break

    if to_delete:
        print(f'\n准备删除 {len(to_delete)} 条测试记忆...')
        for m in to_delete:
            s.delete(m)
        s.commit()
        print('✅ 删除完成')
    else:
        print('✅ 无需删除')
else:
    print('✅ Facts标签无记忆')

s.close()
