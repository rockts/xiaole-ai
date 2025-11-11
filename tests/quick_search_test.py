#!/usr/bin/env python3
"""快速测试搜索工具是否可用"""
from tools.search_tool import search
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


print("="*60)
print("🔍 直接测试搜索工具函数")
print("="*60)

try:
    result = search(query="2025年春节是几月几号", max_results=3)
    print(f"\n✅ 搜索成功!")
    print(f"📊 返回结果数: {len(result) if isinstance(result, list) else 1}")
    print(f"\n搜索结果:")
    print(result)
except Exception as e:
    print(f"\n❌ 搜索失败: {e}")
    import traceback
    traceback.print_exc()
