"""
直接测试搜索工具API
"""
import asyncio
import sys
sys.path.insert(0, '/Users/rockts/Dev/xiaole-ai')

from tools.search_tool import search_tool


async def test():
    print("\n测试1: 搜索 'GitHub Copilot'")
    print("="*60)
    
    result = await search_tool.execute(
        query="GitHub Copilot",
        max_results=3
    )
    
    print(f"Success: {result['success']}")
    if result['success']:
        print(f"Count: {result.get('count', 0)}")
        print(f"\n{result['data']}")
    else:
        print(f"Error: {result.get('error')}")
    
    print("\n测试2: 搜索中文 'FastAPI教程'")
    print("="*60)
    
    result = await search_tool.execute(
        query="FastAPI教程",
        max_results=2
    )
    
    print(f"Success: {result['success']}")
    if result['success']:
        print(f"Count: {result.get('count', 0)}")
        print(f"\n{result['data']}")
    else:
        print(f"Error: {result.get('error')}")


if __name__ == "__main__":
    asyncio.run(test())
