#!/usr/bin/env python3
"""
测试增强的意图识别和工具选择

v0.6.0 Phase 3 - Day 1
"""

from enhanced_intent import EnhancedToolSelector, ContextEnhancer, ToolCall
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend"))


def test_quick_match():
    """测试快速规则匹配"""
    print("=" * 60)
    print("测试1: 快速规则匹配")
    print("=" * 60)

    # 模拟tool_manager
    class MockToolManager:
        def execute_tool(self, tool_name, parameters):
            return {'success': True, 'data': f'{tool_name} executed'}

    selector = EnhancedToolSelector(MockToolManager())

    test_cases = [
        ("搜索下iPhone 17最新价格", "search", 100),
        ("今天天气怎么样？", "weather", 80),
        ("读取todo.txt文件", "file", 70),
        ("查看CPU使用率", "system_info", 60),
    ]

    for prompt, expected_tool, expected_priority in test_cases:
        print(f"\n用户: {prompt}")
        matches = selector._quick_match_tools(prompt)

        if matches:
            match = matches[0]
            print(f"  匹配工具: {match.tool_name}")
            print(f"  优先级: {match.priority}")
            print(f"  置信度: {match.confidence:.2f}")

            assert match.tool_name == expected_tool, \
                f"期望 {expected_tool}, 实际 {match.tool_name}"
            assert match.priority == expected_priority, \
                f"期望优先级 {expected_priority}, 实际 {match.priority}"
            print("  ✅ 通过")
        else:
            print("  ❌ 未匹配到工具")
            assert False, "应该匹配到工具"

    print("\n✅ 快速规则匹配测试通过")


def test_multi_tool_detection():
    """测试多工具检测"""
    print("\n" + "=" * 60)
    print("测试2: 多工具检测")
    print("=" * 60)

    class MockToolManager:
        def execute_tool(self, tool_name, parameters):
            return {'success': True, 'data': f'{tool_name} executed'}

    selector = EnhancedToolSelector(MockToolManager())

    # 需要多个工具的复杂查询
    prompt = "搜索下今天天气，然后帮我保存到文件"
    print(f"\n用户: {prompt}")

    matches = selector._quick_match_tools(prompt)
    print(f"  检测到 {len(matches)} 个工具:")

    for match in matches:
        print(f"    - {match.tool_name} (优先级: {match.priority}, "
              f"置信度: {match.confidence:.2f})")

    # 应该检测到search, weather, file三个工具
    tool_names = {m.tool_name for m in matches}
    assert 'search' in tool_names, "应该检测到search工具"
    assert 'weather' in tool_names, "应该检测到weather工具"
    assert 'file' in tool_names, "应该检测到file工具"

    print("\n✅ 多工具检测测试通过")


def test_deduplicate():
    """测试工具去重"""
    print("\n" + "=" * 60)
    print("测试3: 工具去重")
    print("=" * 60)

    class MockToolManager:
        pass

    selector = EnhancedToolSelector(MockToolManager())

    # 创建重复的工具调用
    calls = [
        ToolCall('search', {}, priority=100, confidence=0.8),
        ToolCall('search', {}, priority=90, confidence=0.95),  # 置信度更高
        ToolCall('weather', {}, priority=80, confidence=0.9),
    ]

    print(f"\n原始调用列表: {len(calls)} 个")
    for call in calls:
        print(f"  - {call.tool_name} (置信度: {call.confidence:.2f})")

    unique = selector._deduplicate_tools(calls)

    print(f"\n去重后列表: {len(unique)} 个")
    for call in unique:
        print(f"  - {call.tool_name} (置信度: {call.confidence:.2f})")

    assert len(unique) == 2, "应该只剩2个唯一工具"
    search_call = [c for c in unique if c.tool_name == 'search'][0]
    assert search_call.confidence == 0.95, "应该保留置信度更高的"

    print("\n✅ 工具去重测试通过")


def test_retry_strategy():
    """测试重试策略"""
    print("\n" + "=" * 60)
    print("测试4: 重试策略")
    print("=" * 60)

    class MockToolManager:
        def __init__(self):
            self.attempt = 0

        def execute_tool(self, tool_name, parameters):
            self.attempt += 1
            if self.attempt == 1:
                # 第一次失败
                return {
                    'success': False,
                    'error': '搜索失败: 网络错误'
                }
            else:
                # 第二次成功
                return {
                    'success': True,
                    'data': {'results': ['result1', 'result2']}
                }

    tool_manager = MockToolManager()
    selector = EnhancedToolSelector(tool_manager)

    tool_call = ToolCall(
        tool_name='search',
        parameters={'query': '搜索iPhone 17'},
        priority=100
    )

    print(f"\n执行工具: {tool_call.tool_name}")
    print(f"参数: {tool_call.parameters}")

    result = selector.execute_with_retry(tool_call, max_retries=3)

    print(f"\n执行结果:")
    print(f"  成功: {result.success}")
    print(f"  数据: {result.data}")
    print(f"  尝试次数: {tool_manager.attempt}")

    assert result.success, "重试后应该成功"
    assert tool_manager.attempt == 2, "应该尝试2次"

    print("\n✅ 重试策略测试通过")


def test_context_enhancer():
    """测试上下文增强器"""
    print("\n" + "=" * 60)
    print("测试5: 上下文增强器")
    print("=" * 60)

    # 模拟memory和conversation
    class MockMemory:
        def recall(self, tag, limit):
            return [
                "用户住在深圳",
                "用户喜欢看科技新闻",
                "用户的生日是6月15日"
            ]

        def semantic_recall(self, query, tag, limit, min_score):
            return [
                "用户关注iPhone新品发布",
                "用户经常询问天气"
            ]

    class MockConversation:
        def get_history(self, session_id, limit):
            return [
                {"role": "user", "content": "你好"},
                {"role": "assistant", "content": "你好！"},
                {"role": "user", "content": "今天天气怎么样？"}
            ]

    enhancer = ContextEnhancer(MockMemory(), MockConversation())

    prompt = "搜索下最新的iPhone消息"
    session_id = "test_session"

    print(f"\n用户输入: {prompt}")
    print(f"会话ID: {session_id}")

    context = enhancer.enhance_context(prompt, session_id)

    print(f"\n增强的上下文:")
    print(f"  最近历史: {len(context['recent_history'])} 条")
    print(f"  相关记忆: {len(context['relevant_memories'])} 条")
    print(f"  用户偏好: {context['user_preferences']}")

    assert len(context['recent_history']) > 0, "应该有对话历史"
    assert len(context['relevant_memories']) > 0, "应该有相关记忆"
    assert 'response_style' in context['user_preferences'], "应该有响应风格"

    print("\n✅ 上下文增强器测试通过")


def run_all_tests():
    """运行所有测试"""
    print("\n🧪 开始测试 Enhanced Intent 模块")
    print("=" * 60)

    try:
        test_quick_match()
        test_multi_tool_detection()
        test_deduplicate()
        test_retry_strategy()
        test_context_enhancer()

        print("\n" + "=" * 60)
        print("🎉 所有测试通过！")
        print("=" * 60)
        return True

    except AssertionError as e:
        print(f"\n❌ 测试失败: {e}")
        return False
    except Exception as e:
        print(f"\n💥 测试异常: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
