#!/usr/bin/env python3
"""
网络搜索工具演示
展示如何使用搜索工具查询互联网信息
"""
from tools.search_tool import search_tool
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


async def demo():
    """演示搜索工具的使用"""
    print("=" * 70)
    print(" " * 20 + "🔍 网络搜索工具演示")
    print("=" * 70)
    print()

    # 示例1: 搜索技术问题
    print("📝 示例1: 搜索技术问题")
    print("-" * 70)
    print("搜索: Python 3.13 新特性\n")

    result = await search_tool.execute(
        query="Python 3.13 新特性",
        max_results=3
    )

    if result['success']:
        print(result['data'])
    else:
        print(f"❌ 搜索失败: {result['error']}")

    print("\n" + "=" * 70)

    # 示例2: 搜索实时信息
    print("\n📝 示例2: 搜索实时天气")
    print("-" * 70)
    print("搜索: 北京今天天气\n")

    result = await search_tool.execute(
        query="北京今天天气",
        max_results=2
    )

    if result['success']:
        print(result['data'])
    else:
        print(f"❌ 搜索失败: {result['error']}")

    print("\n" + "=" * 70)

    # 示例3: 搜索教程
    print("\n📝 示例3: 搜索学习资料")
    print("-" * 70)
    print("搜索: FastAPI 教程\n")

    result = await search_tool.execute(
        query="FastAPI 教程",
        max_results=5
    )

    if result['success']:
        print(result['data'])
        print(f"\n✅ 共找到 {result['count']} 条结果")
    else:
        print(f"❌ 搜索失败: {result['error']}")

    print("\n" + "=" * 70)
    print("✅ 演示完成！")
    print("=" * 70)
    print("\n💡 提示:")
    print("  - 直接对小乐说话，AI会自动判断是否需要搜索")
    print("  - 例如: \"帮我搜索Python教程\"")
    print("  - 或者: \"最近有什么科技新闻？\"")
    print("  - AI会自动调用搜索工具并整理结果")
    print()


if __name__ == "__main__":
    asyncio.run(demo())
