#!/usr/bin/env python3
"""
测试语义搜索功能
"""

from memory import MemoryManager
import sys
import os
# 添加 backend 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend'))


print("🧪 测试语义搜索功能\n")
print("=" * 60)

# 初始化记忆管理器
mm = MemoryManager(enable_vector_search=True)

print("\n📊 当前记忆统计:")
stats = mm.get_stats()
print(f"  总记忆数: {stats['total']}")
print(f"  标签分布: {stats['by_tag']}")

print("\n" + "=" * 60)
print("🔍 测试语义搜索\n")

# 测试查询
test_queries = [
    ("我叫什么", "facts"),
    ("多大年纪", "facts"),
    ("生日几号", "facts"),
    ("喜欢什么", "facts"),
    ("运动爱好", "facts"),
    ("咖啡", None),
]

for query, tag in test_queries:
    print(f"查询: '{query}'" + (f" [标签: {tag}]" if tag else ""))

    # 语义搜索
    results = mm.semantic_recall(query, tag=tag, limit=3, min_score=0.1)

    if results:
        for i, mem in enumerate(results, 1):
            score = mem.get('score', 0)
            print(f"  {i}. [{score:.3f}] {mem['content']}")
    else:
        print("  无匹配结果")
    print()

print("=" * 60)
print("\n✅ 测试完成")
