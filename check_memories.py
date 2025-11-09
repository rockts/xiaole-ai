#!/usr/bin/env python3
"""检查数据库中的记忆内容"""

from memory import MemoryManager

mm = MemoryManager()

# 查看facts记忆
facts = mm.recall(tag='facts', limit=100)
print(f'\n📋 Facts标签记忆 (共{len(facts)}条):\n')
for i, f in enumerate(facts, 1):
    print(f'{i}. {f}')

# 查看general记忆
print('\n' + '='*60)
general = mm.recall(tag='general', limit=20)
print(f'\n📋 General标签记忆 (共{len(general)}条):\n')
for i, g in enumerate(general, 1):
    print(f'{i}. {g}')
