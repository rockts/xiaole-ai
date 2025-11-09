"""
测试在对话中使用搜索功能
"""
import requests
import json
import time

API_BASE = "http://localhost:8000"
session_id = "test-search-session"


def chat(prompt):
    """发送聊天消息"""
    print(f"\n{'='*60}")
    print(f"👤 用户: {prompt}")
    print(f"{'='*60}")

    response = requests.post(
        f"{API_BASE}/chat",
        params={
            "prompt": prompt,
            "session_id": session_id
        }
    )

    if response.status_code == 200:
        data = response.json()
        reply = data.get("reply", "")
        print(f"\n🤖 小乐: {reply}\n")

        # 如果有工具调用信息，显示出来
        if "tool_used" in data:
            print(f"🔧 使用的工具: {data['tool_used']}")
            if "tool_result" in data:
                print(f"📊 工具结果: {data['tool_result'][:200]}...")
    else:
        print(f"❌ 请求失败: {response.status_code}")


def main():
    print("\n" + "="*60)
    print("🧪 搜索功能测试")
    print("="*60)

    # 测试1: 直接搜索请求
    print("\n测试1: 直接搜索请求")
    chat("帮我搜索一下Python编程语言的最新动态")
    time.sleep(2)

    # 测试2: 查询实时信息
    print("\n测试2: 查询实时信息")
    chat("查一下人工智能领域最近有什么新闻")
    time.sleep(2)

    # 测试3: 百科知识查询
    print("\n测试3: 百科知识查询")
    chat("帮我找一下量子计算的相关资料")
    time.sleep(2)

    # 测试4: 搜索关键词
    print("\n测试4: 搜索关键词")
    chat("搜索 FastAPI 框架")
    time.sleep(2)

    print("\n" + "="*60)
    print("✅ 测试完成")
    print("="*60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ 测试被中断")
    except Exception as e:
        print(f"\n❌ 测试出错: {e}")
        import traceback
        traceback.print_exc()
