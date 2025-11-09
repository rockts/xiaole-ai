#!/usr/bin/env python3
"""
测试智能工具调用功能
"""
import requests
import json
import time

API_BASE = "http://localhost:8000"

def test_tool_call(description, prompt, expected_tool=None):
    """测试单个工具调用"""
    print(f"\n{'='*60}")
    print(f"🧪 {description}")
    print(f"{'='*60}")
    print(f"📝 提示词: {prompt}")
    
    try:
        response = requests.post(
            f"{API_BASE}/chat",
            params={"prompt": prompt},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            reply = data.get('reply', '')
            session_id = data.get('session_id', '')
            
            print(f"✅ 状态: 成功")
            print(f"📋 会话ID: {session_id[:30]}...")
            print(f"💬 AI回复:\n{reply[:500]}")
            
            if expected_tool:
                if expected_tool in reply or "查询" in reply:
                    print(f"✅ 工具调用: 可能调用了 {expected_tool} 工具")
                else:
                    print(f"⚠️  未明确看到 {expected_tool} 工具调用")
            
            return True
        else:
            print(f"❌ 错误: HTTP {response.status_code}")
            print(f"   {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ 异常: {e}")
        return False

def main():
    """运行所有测试"""
    print("""
    🎯 小乐AI - 智能工具调用测试
    
    测试说明：
    1. AI会自动识别用户意图
    2. 从记忆中提取必要参数（如城市名）
    3. 自动调用相应工具
    4. 将工具结果融入回复
    """)
    
    tests = [
        {
            "description": "测试1: 天气查询（从记忆提取城市）",
            "prompt": "明天天气怎么样？",
            "expected_tool": "weather"
        },
        {
            "description": "测试2: 系统信息查询",
            "prompt": "我的电脑CPU使用率是多少？",
            "expected_tool": "system_info"
        },
        {
            "description": "测试3: 时间查询",
            "prompt": "现在几点了？",
            "expected_tool": "time"
        },
        {
            "description": "测试4: 计算器",
            "prompt": "计算：365 × 24",
            "expected_tool": "calculator"
        },
        {
            "description": "测试5: 综合测试（天气+带伞建议）",
            "prompt": "今天我上班需要带伞吗？",
            "expected_tool": "weather"
        }
    ]
    
    results = []
    for test in tests:
        success = test_tool_call(
            test["description"],
            test["prompt"],
            test.get("expected_tool")
        )
        results.append(success)
        time.sleep(2)  # 避免请求过快
    
    # 统计结果
    print(f"\n{'='*60}")
    print("📊 测试结果统计")
    print(f"{'='*60}")
    print(f"总测试数: {len(results)}")
    print(f"成功: {sum(results)} ✅")
    print(f"失败: {len(results) - sum(results)} ❌")
    print(f"成功率: {sum(results)/len(results)*100:.1f}%")
    
    # 检查工具历史
    print(f"\n{'='*60}")
    print("📋 查看工具执行历史")
    print(f"{'='*60}")
    try:
        response = requests.get(f"{API_BASE}/tools/history", params={"limit": 10})
        if response.status_code == 200:
            data = response.json()
            print(f"最近10条工具执行记录:")
            for i, record in enumerate(data.get('history', [])[:5], 1):
                status = "✅" if record['success'] else "❌"
                print(f"  {i}. {status} {record['tool_name']} - {record['execution_time']:.3f}s")
        else:
            print("无法获取工具历史")
    except Exception as e:
        print(f"获取工具历史失败: {e}")

if __name__ == "__main__":
    main()
