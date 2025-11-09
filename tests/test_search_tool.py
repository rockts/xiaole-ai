"""
测试搜索工具
"""
import asyncio
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.search_tool import search_tool


async def test_search():
    """测试搜索功能"""
    print("="*60)
    print("🔍 搜索工具测试")
    print("="*60)
    
    # 测试1: 基础搜索
    print("\n测试1: 搜索 'Python 编程语言'")
    print("-"*60)
    result = await search_tool.execute(
        query="Python 编程语言",
        max_results=3
    )
    
    if result['success']:
        print(f"✅ 搜索成功")
        print(f"找到 {result['count']} 条结果\n")
        print(result['data'])
    else:
        print(f"❌ 搜索失败: {result['error']}")
    
    # 测试2: 搜索新闻
    print("\n" + "="*60)
    print("测试2: 搜索 '人工智能最新动态'")
    print("-"*60)
    result = await search_tool.execute(
        query="人工智能最新动态",
        max_results=3
    )
    
    if result['success']:
        print(f"✅ 搜索成功")
        print(f"找到 {result['count']} 条结果\n")
        print(result['data'])
    else:
        print(f"❌ 搜索失败: {result['error']}")
    
    # 测试3: 空查询
    print("\n" + "="*60)
    print("测试3: 空查询（应该失败）")
    print("-"*60)
    result = await search_tool.execute(query="")
    
    if not result['success']:
        print(f"✅ 正确处理空查询: {result['error']}")
    else:
        print(f"❌ 应该返回错误")
    
    print("\n" + "="*60)
    print("测试完成")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(test_search())
