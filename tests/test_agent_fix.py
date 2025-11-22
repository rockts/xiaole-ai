from backend.agent import XiaoLeAgent
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))), 'backend'))


def test_agent():
    print("Initializing Agent...")
    try:
        agent = XiaoLeAgent()
        print("Agent initialized successfully.")
    except Exception as e:
        print(f"Agent initialization failed: {e}")
        return

    print("\nTesting identify_complex_task...")
    try:
        # 模拟一个简单的任务识别
        result = agent.identify_complex_task("帮我倒杯水", "test_user")
        print(f"Result: {result}")
    except Exception as e:
        print(f"identify_complex_task failed: {e}")

    print("\nTesting memory session...")
    try:
        # 测试 memory.session 是否可用
        if hasattr(agent.memory, 'session'):
            print("agent.memory.session exists.")
        else:
            print("agent.memory.session MISSING!")
    except Exception as e:
        print(f"Memory check failed: {e}")


if __name__ == "__main__":
    test_agent()
