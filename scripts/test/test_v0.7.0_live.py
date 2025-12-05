#!/usr/bin/env python3
"""
v0.7.0 实际对话效果测试
测试智能追问、情感感知、冲突检测等功能
"""
import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8000"
SESSION_ID = f"test_v0.7.0_{int(time.time())}"


def chat(message: str, session_id: str = SESSION_ID) -> dict:
    """发送对话请求"""
    response = requests.post(
        f"{BASE_URL}/chat",
        params={
            "prompt": message,
            "session_id": session_id,
            "user_id": "test_user"
        }
    )
    try:
        return response.json()
    except Exception as e:
        return {"response": "解析失败", "error": str(e)}


def print_response(message: str, response: dict):
    """格式化输出响应"""
    print(f"\n{'='*60}")
    print(f"👤 用户: {message}")
    print(f"🤖 回复: {response.get('response', 'N/A')}")

    # 检查是否触发了智能追问
    reply = response.get('response', '')
    if '💭' in reply:
        print("✅ 检测到智能追问标记")
        followup = reply.split('💭')[-1].strip() if '💭' in reply else ''
        if followup:
            print(f"   追问内容: {followup}")

    print(f"{'='*60}\n")
    time.sleep(1)  # 避免请求过快


def test_knowledge_gap():
    """测试1: 知识空白检测"""
    print("\n" + "="*60)
    print("测试1: 知识空白检测（模糊回答触发追问）")
    print("="*60)

    # 场景1: 模糊回答
    response = chat("RAG技术的优势是什么？")
    print_response("RAG技术的优势是什么？", response)

    # 模拟一个模糊回答（通过短回复）
    response = chat("大概就是能检索知识吧")
    print_response("大概就是能检索知识吧", response)

    # 场景2: 回答过短
    response = chat("向量数据库有哪些？")
    print_response("向量数据库有哪些？", response)


def test_memory_conflict():
    """测试2: 信息冲突检测"""
    print("\n" + "="*60)
    print("测试2: 信息冲突检测（前后矛盾触发追问）")
    print("="*60)

    # 先建立一个事实
    response = chat("我喜欢喝咖啡")
    print_response("我喜欢喝咖啡", response)

    time.sleep(2)

    # 再说相反的话
    response = chat("我不喜欢喝咖啡")
    print_response("我不喜欢喝咖啡", response)


def test_task_feedback():
    """测试3: 任务反馈检测"""
    print("\n" + "="*60)
    print("测试3: 任务反馈检测（完成任务但未反馈）")
    print("="*60)

    # 请求创建提醒
    response = chat("帮我设置一个明天下午3点的会议提醒")
    print_response("帮我设置一个明天下午3点的会议提醒", response)

    time.sleep(2)

    # 换个话题（不给反馈）
    response = chat("今天天气怎么样？")
    print_response("今天天气怎么样？", response)


def test_emotion_awareness():
    """测试4: 情感感知（不耐烦检测）"""
    print("\n" + "="*60)
    print("测试4: 情感感知（检测用户不耐烦，停止追问）")
    print("="*60)

    # 先触发一个追问场景
    response = chat("Python有什么特点？")
    print_response("Python有什么特点？", response)

    time.sleep(1)

    # 给一个简短回答（可能触发追问）
    response = chat("就是简单")
    print_response("就是简单", response)

    time.sleep(1)

    # 表达不耐烦
    response = chat("别问了，知道了")
    print_response("别问了，知道了", response)


def test_incomplete_answer():
    """测试5: 不完整回答追问（v0.6.0原有功能）"""
    print("\n" + "="*60)
    print("测试5: 不完整回答追问")
    print("="*60)

    # 问一个可能得到不完整回答的问题
    response = chat("怎么学习机器学习？")
    print_response("怎么学习机器学习？", response)

    time.sleep(1)

    # 给一个很短的回答
    response = chat("看书")
    print_response("看书", response)


def test_complete_flow():
    """测试6: 完整流程（多轮对话）"""
    print("\n" + "="*60)
    print("测试6: 完整对话流程")
    print("="*60)

    session_id = f"test_complete_{int(time.time())}"

    # 第1轮：正常对话
    response = chat("你好", session_id)
    print_response("你好", response)

    # 第2轮：提一个问题
    response = chat("什么是向量数据库？", session_id)
    print_response("什么是向量数据库？", response)

    # 第3轮：给一个模糊回答
    response = chat("不太清楚", session_id)
    print_response("不太清楚", response)

    # 第4轮：正常回答（可能触发追问）
    response = chat("就是存储向量的数据库", session_id)
    print_response("就是存储向量的数据库", response)


def check_server():
    """检查服务器是否运行"""
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("✅ 服务器运行正常")
            return True
    except Exception as e:
        print(f"❌ 服务器未运行: {e}")
        print("请先启动服务: python main.py")
        return False
    return False


def main():
    """主函数"""
    print("\n" + "="*80)
    print(" v0.7.0 实际对话效果测试")
    print("="*80)

    # 检查服务器
    if not check_server():
        return

    print("\n开始测试...")

    try:
        # 运行所有测试
        test_knowledge_gap()
        time.sleep(2)

        test_memory_conflict()
        time.sleep(2)

        test_task_feedback()
        time.sleep(2)

        test_emotion_awareness()
        time.sleep(2)

        test_incomplete_answer()
        time.sleep(2)

        test_complete_flow()

        print("\n" + "="*80)
        print(" 测试完成！")
        print("="*80)
        print("\n总结:")
        print("✅ 已测试所有核心功能场景")
        print("✅ 请检查上述输出中的追问标记（💭）")
        print("✅ 关注智能追问的触发时机和内容质量")
        print("\n建议: 到前端页面进行更自然的对话测试")

    except Exception as e:
        print(f"\n❌ 测试出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
