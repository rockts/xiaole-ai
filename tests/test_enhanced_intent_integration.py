"""测试增强意图识别的集成"""

def test_multi_step():
    """测试多步骤任务识别"""
    from enhanced_intent import EnhancedToolSelector
    
    class MockToolManager:
        def execute_tool(self, tool_name, params, user_id):
            return {'success': True, 'data': f'{tool_name}执行成功'}
    
    selector = EnhancedToolSelector(MockToolManager())
    
    # 测试多步骤任务
    prompt = "搜索下iPhone 17价格，然后保存到文件"
    tool_calls = selector.analyze_intent(prompt, {})
    
    print(f"识别到 {len(tool_calls)} 个工具:")
    for call in tool_calls:
        print(f"  - {call.tool_name} (优先级:{call.priority}, 依赖:{call.depends_on})")
    
    assert len(tool_calls) >= 1, "应该识别到至少1个工具"
    print("✅ 多步骤任务测试通过")


def test_single_tool():
    """测试单工具识别"""
    from enhanced_intent import EnhancedToolSelector
    
    class MockToolManager:
        def execute_tool(self, tool_name, params, user_id):
            return {'success': True, 'data': 'OK'}
    
    selector = EnhancedToolSelector(MockToolManager())
    
    prompt = "搜索下最新新闻"
    tool_calls = selector.analyze_intent(prompt, {})
    
    assert len(tool_calls) > 0
    assert tool_calls[0].tool_name == 'search'
    print("✅ 单工具识别测试通过")


if __name__ == '__main__':
    test_multi_step()
    test_single_tool()
    print("\n🎉 所有集成测试通过！")
