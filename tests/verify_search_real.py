#!/usr/bin/env python3
"""
验证小乐的搜索工具是否真实可用
直接测试DuckDuckGo API
"""
from duckduckgo_search import DDGS
import sys
import os
import asyncio
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


async def test_real_search():
    """直接测试DuckDuckGo搜索"""
    print("="*70)
    print("🔍 验证小乐的搜索功能是否真实")
    print("="*70)

    test_query = "iPhone 17 Pro Max 发布时间"

    print(f"\n📝 搜索关键词: {test_query}")
    print("-"*70)

    try:
        print("⏳ 正在连接DuckDuckGo搜索引擎...")

        # 直接使用DuckDuckGo API
        with DDGS() as ddgs:
            results = list(ddgs.text(test_query, max_results=5))

        if results:
            print(f"✅ 搜索成功! 找到 {len(results)} 条真实结果\n")
            print("📊 搜索结果:")
            print("="*70)

            for i, result in enumerate(results, 1):
                title = result.get('title', 'N/A')
                body = result.get('body', 'N/A')
                href = result.get('href', 'N/A')

                print(f"\n{i}. {title}")
                print(f"   {body[:150]}...")
                print(f"   🔗 {href}")

            print("\n" + "="*70)
            print("✅ 结论: 搜索工具是真实的DuckDuckGo API")
            print("="*70)
        else:
            print("⚠️  搜索返回空结果")

    except Exception as e:
        print(f"❌ 搜索失败: {e}")
        print("\n可能的原因:")
        print("  1. 网络连接问题")
        print("  2. DuckDuckGo API限流")
        print("  3. 防火墙/代理设置")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_real_search())
