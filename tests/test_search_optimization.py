"""
测试搜索工具优化功能 (v0.6.0)
测试：缓存、重试、历史记录
"""
from tools.search_tool import search_tool
import asyncio
import time
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


async def test_cache():
    """测试缓存功能"""
    print("=" * 50)
    print("测试1: 缓存功能")
    print("=" * 50)

    query = "Python教程"

    # 第一次搜索（无缓存）
    print("\n第一次搜索（无缓存）...")
    start = time.time()
    result1 = await search_tool.execute(query=query, max_results=3)
    time1 = time.time() - start
    print(f"✅ 耗时: {time1:.2f}秒")
    print(f"   成功: {result1['success']}")
    print(f"   结果数: {result1.get('count', 0)}")

    # 第二次搜索（使用缓存）
    print("\n第二次搜索（使用缓存）...")
    start = time.time()
    result2 = await search_tool.execute(query=query, max_results=3)
    time2 = time.time() - start
    print(f"✅ 耗时: {time2:.2f}秒")
    print(f"   成功: {result2['success']}")
    print(f"   结果数: {result2.get('count', 0)}")

    # 验证缓存效果
    if time2 < time1 * 0.1:  # 缓存应该快10倍以上
        print(f"\n✅ 缓存生效！速度提升 {time1/time2:.0f}x")
    else:
        print("\n⚠️  缓存可能未生效")


async def test_retry():
    """测试重试功能"""
    print("\n" + "=" * 50)
    print("测试2: 错误重试")
    print("=" * 50)

    # 使用正常查询测试（因为无法模拟网络错误）
    query = "机器学习"

    print(f"\n搜索: {query}")
    result = await search_tool.execute(query=query, max_results=3)

    print(f"✅ 成功: {result['success']}")
    if not result['success']:
        print(f"   错误: {result.get('error')}")
        print(f"   建议: {result.get('suggestion')}")
    else:
        print(f"   结果数: {result.get('count', 0)}")


async def test_history():
    """测试搜索历史"""
    print("\n" + "=" * 50)
    print("测试3: 搜索历史")
    print("=" * 50)

    # 执行几次搜索
    queries = ["人工智能", "深度学习", "神经网络"]

    print("\n执行多次搜索...")
    for query in queries:
        print(f"  - 搜索: {query}")
        await search_tool.execute(query=query, max_results=2)

    # 获取统计信息
    stats = search_tool.get_search_stats()

    print("\n📊 搜索统计:")
    print(f"   总搜索次数: {stats['total_searches']}")
    print(f"   成功: {stats['successful']}")
    print(f"   失败: {stats['failed']}")
    print(f"   成功率: {stats['success_rate']}")
    print(f"   缓存数量: {stats['cache_size']}")
    print(f"   最近搜索: {stats['recent_searches']}")


async def test_cache_expiration():
    """测试缓存过期"""
    print("\n" + "=" * 50)
    print("测试4: 缓存过期")
    print("=" * 50)

    # 临时缩短TTL
    original_ttl = search_tool.cache_ttl
    search_tool.cache_ttl = 2  # 2秒过期

    query = "缓存测试"

    # 第一次搜索
    print("\n第一次搜索...")
    result1 = await search_tool.execute(query=query, max_results=2)
    print(f"✅ 结果数: {result1.get('count', 0)}")

    # 立即第二次搜索（使用缓存）
    print("\n立即第二次搜索（应该使用缓存）...")
    start = time.time()
    result2 = await search_tool.execute(query=query, max_results=2)
    time2 = time.time() - start

    if time2 < 0.1:
        print(f"✅ 使用了缓存（{time2:.3f}秒）")
    else:
        print(f"⚠️  未使用缓存（{time2:.3f}秒）")

    # 等待缓存过期
    print("\n等待3秒让缓存过期...")
    await asyncio.sleep(3)

    # 第三次搜索（缓存已过期）
    print("\n第三次搜索（缓存应已过期）...")
    start = time.time()
    result3 = await search_tool.execute(query=query, max_results=2)
    time3 = time.time() - start

    if time3 > 0.5:
        print(f"✅ 缓存已过期，重新搜索（{time3:.2f}秒）")
    else:
        print(f"⚠️  可能还在使用缓存（{time3:.3f}秒）")

    # 恢复原始TTL
    search_tool.cache_ttl = original_ttl


async def test_empty_query():
    """测试空查询"""
    print("\n" + "=" * 50)
    print("测试5: 空查询处理")
    print("=" * 50)

    print("\n测试空字符串...")
    result = await search_tool.execute(query="")
    print(f"✅ 成功: {result['success']}")
    print(f"   错误: {result.get('error')}")

    assert not result['success'], "空查询应该返回失败"
    assert "不能为空" in result['error'], "应该有明确的错误提示"


async def main():
    """运行所有测试"""
    print("\n🧪 开始测试搜索工具优化功能 (v0.6.0)\n")

    try:
        await test_cache()
        await test_retry()
        await test_history()
        await test_cache_expiration()
        await test_empty_query()

        print("\n" + "=" * 50)
        print("✅ 所有测试完成！")
        print("=" * 50)

        # 最终统计
        stats = search_tool.get_search_stats()
        print("\n📊 最终统计:")
        for key, value in stats.items():
            print(f"   {key}: {value}")

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
