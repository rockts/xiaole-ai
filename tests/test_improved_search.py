#!/usr/bin/env python3
"""
测试改进后的搜索功能
"""
from tools.search_tool import search_tool
import sys
import os
import asyncio

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "backend"))


async def test_improved_search():
    """测试改进后的搜索"""
    print("="*70)
    print("🔍 测试改进后的DuckDuckGo搜索(多策略)")
    print("="*70)

    query = "iPhone 17 Pro Max 发布时间"
    print(f"\n搜索: {query}\n")
    print("-"*70)

    result = await search_tool.execute(query=query, max_results=3)

    print("\n" + "="*70)
    print("搜索结果:")
    print("="*70)
    print(f"Success: {result.get('success')}")
    print(f"Count: {result.get('count', 0)}")

    if result.get('success'):
        print(f"\n{result.get('data')}")
    else:
        print(f"\nError: {result.get('error')}")
        print(f"\n{result.get('data')}")


if __name__ == "__main__":
    asyncio.run(test_improved_search())
