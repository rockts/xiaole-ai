"""
v0.6.0 Phase 3 功能测试
测试 AI Enhancement 的所有新功能
"""
import time
from memory import MemoryManager
from agent import XiaoLeAgent
import sys
sys.path.insert(0, '/Users/rockts/Dev/xiaole-ai')


def test_quick_intent_match():
    """测试快速规则匹配"""
    print("\n" + "="*60)
    print("测试 1: 快速规则匹配（无AI调用）")
    print("="*60)

    agent = XiaoLeAgent()

    test_cases = [
        ("现在几点", "time"),
        ("CPU使用率", "system_info"),
        ("100 + 200", "calculator"),
        ("搜索 Python教程", "search"),
    ]

    for prompt, expected_tool in test_cases:
        result = agent._quick_intent_match(prompt)
        if result and result.get('tool_name') == expected_tool:
            print(f"✅ '{prompt}' -> {expected_tool}")
        else:
            print(f"❌ '{prompt}' -> {result}")


def test_memory_importance():
    """测试记忆重要性评分"""
    print("\n" + "="*60)
    print("测试 2: 记忆重要性评分系统")
    print("="*60)

    memory = MemoryManager()

    # 创建测试记忆
    print("\n创建测试记忆...")
    mem_id1 = memory.remember("用户姓名是张三", tag="facts", initial_importance=0.8)
    mem_id2 = memory.remember("今天天气不错", tag="general", initial_importance=0.3)
    mem_id3 = memory.remember("完成了项目A", tag="task", initial_importance=0.6)

    # 模拟访问
    print("\n模拟记忆访问...")
    for _ in range(5):
        memory._update_access(mem_id1)  # 高频访问

    for _ in range(2):
        memory._update_access(mem_id2)  # 低频访问

    # 计算重要性
    print("\n计算重要性分数...")
    score1 = memory.calculate_importance(mem_id1)
    score2 = memory.calculate_importance(mem_id2)
    score3 = memory.calculate_importance(mem_id3)

    print(f"✅ 高价值记忆 (facts, 5次访问): {score1:.3f}")
    print(f"✅ 低价值记忆 (general, 2次访问): {score2:.3f}")
    print(f"✅ 中等记忆 (task, 0次访问): {score3:.3f}")

    # 获取最重要记忆
    print("\n获取最重要的记忆...")
    top_memories = memory.get_top_memories(limit=5)
    for mem in top_memories[:3]:
        print(
            f"  - {mem['content'][:30]}... (分数: {mem['importance_score']:.3f})")


def test_memory_archiving():
    """测试记忆自动归档"""
    print("\n" + "="*60)
    print("测试 3: 记忆自动归档机制")
    print("="*60)

    memory = MemoryManager()

    # 获取统计信息
    stats = memory.get_memory_stats()
    print(f"\n当前记忆统计:")
    print(f"  总计: {stats['total']}")
    print(f"  活跃: {stats['active']}")
    print(f"  归档: {stats['archived']}")
    print(f"\n重要性分布:")
    for level, count in stats['importance_distribution'].items():
        print(f"  {level}: {count}")

    # 尝试归档（实际环境中需要老旧记忆）
    print(f"\n尝试归档低重要性记忆...")
    archived = memory.auto_archive_low_importance(
        threshold=0.1, min_age_days=0)
    print(f"✅ 归档了 {archived} 条记忆")


def test_response_styles():
    """测试响应风格"""
    print("\n" + "="*60)
    print("测试 4: 响应风格配置")
    print("="*60)

    agent = XiaoLeAgent()

    styles = ['concise', 'balanced', 'detailed', 'professional']

    for style in styles:
        params = agent._get_llm_parameters(style)
        instruction = agent._get_style_instruction(style)

        print(f"\n{style.upper()}:")
        print(f"  Temperature: {params['temperature']}")
        print(f"  Max Tokens: {params['max_tokens']}")
        print(f"  Top P: {params['top_p']}")
        print(f"  指令: {instruction[:50]}...")


def test_chat_with_style():
    """测试带风格的对话"""
    print("\n" + "="*60)
    print("测试 5: 带响应风格的对话")
    print("="*60)

    agent = XiaoLeAgent()

    if not agent.client:
        print("⚠️  未配置 API，跳过对话测试")
        return

    print("\n测试简洁模式...")
    result = agent.chat(
        "你好，介绍一下你自己",
        response_style="concise"
    )
    print(f"回复长度: {len(result['reply'])} 字符")
    print(f"回复: {result['reply'][:100]}...")


if __name__ == "__main__":
    print("\n🚀 v0.6.0 Phase 3 功能测试")
    print("=" * 60)

    try:
        # 测试 1: 快速规则匹配
        test_quick_intent_match()

        # 测试 2: 记忆重要性评分
        test_memory_importance()

        # 测试 3: 记忆归档
        test_memory_archiving()

        # 测试 4: 响应风格
        test_response_styles()

        # 测试 5: 带风格的对话（需要API）
        # test_chat_with_style()

        print("\n" + "="*60)
        print("✅ Phase 3 功能测试完成")
        print("="*60)

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
