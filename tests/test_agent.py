#!/usr/bin/env python3
"""
小乐 AI Agent 综合测试脚本
测试记忆、对话、上下文理解等功能
"""
import requests
import json
import time
from datetime import datetime


BASE_URL = "http://localhost:8000"


def print_section(title):
    """打印测试章节标题"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def test_think(prompt, description=""):
    """测试 think 接口"""
    if description:
        print(f"📝 {description}")
    print(f"👤 用户: {prompt}")

    try:
        response = requests.post(
            f"{BASE_URL}/think",
            params={"prompt": prompt},
            timeout=20
        )
        response.raise_for_status()
        result = response.json()

        reply = result.get("result", "无响应")
        print(f"🤖 小乐: {reply}\n")
        return reply

    except Exception as e:
        print(f"❌ 错误: {e}\n")
        return None


def test_memory(tag="general", limit=5):
    """测试 memory 接口"""
    try:
        response = requests.get(
            f"{BASE_URL}/memory",
            params={"tag": tag, "limit": limit},
            timeout=10
        )
        response.raise_for_status()
        result = response.json()

        memories = result.get("memory", [])
        print(f"📚 记忆库 ({tag}) - 共 {len(memories)} 条:")
        for i, mem in enumerate(memories, 1):
            print(f"  {i}. {mem[:80]}..." if len(
                mem) > 80 else f"  {i}. {mem}")
        print()
        return memories

    except Exception as e:
        print(f"❌ 错误: {e}\n")
        return []


def test_act(command):
    """测试 act 接口"""
    print(f"⚡ 执行任务: {command}")

    try:
        response = requests.post(
            f"{BASE_URL}/act",
            params={"command": command},
            timeout=20
        )
        response.raise_for_status()
        result = response.json()

        reply = result.get("result", "无响应")
        print(f"✅ 结果: {reply}\n")
        return reply

    except Exception as e:
        print(f"❌ 错误: {e}\n")
        return None


def run_comprehensive_test():
    """运行综合测试"""
    print(f"\n🚀 小乐 AI Agent 综合测试")
    print(f"⏰ 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 API 地址: {BASE_URL}")

    # 测试 1: 基本对话
    print_section("测试 1: 基本对话能力")
    test_think("你好，小乐！", "初次问候")
    time.sleep(1)

    # 测试 2: 记忆存储
    print_section("测试 2: 记忆存储")
    test_think("我叫高鹏", "告诉小乐名字")
    time.sleep(1)
    test_think("我今年35岁", "告诉小乐年龄")
    time.sleep(1)
    test_think("我喜欢跑步和篮球", "告诉小乐爱好")
    time.sleep(1)

    # 测试 3: 记忆检索
    print_section("测试 3: 记忆检索能力")
    test_think("我叫什么名字？", "测试名字记忆")
    time.sleep(1)
    test_think("我多大了？", "测试年龄记忆")
    time.sleep(1)
    test_think("我喜欢什么运动？", "测试爱好记忆")
    time.sleep(1)

    # 测试 4: 上下文理解
    print_section("测试 4: 上下文理解")
    test_think("今天天气怎么样？", "询问天气（测试未知信息处理）")
    time.sleep(1)
    test_think("你能帮我做什么？", "询问能力")
    time.sleep(1)

    # 测试 5: 任务执行
    print_section("测试 5: 任务执行 (act)")
    test_act("总结一下你对我的了解")
    time.sleep(1)

    # 测试 6: 查看记忆库
    print_section("测试 6: 查看记忆库")
    test_memory(tag="general", limit=10)

    # 测试 7: 复杂对话
    print_section("测试 7: 复杂对话场景")
    test_think("根据我的爱好，推荐一个周末活动", "基于记忆的推荐")
    time.sleep(1)
    test_think("为什么推荐这个？", "测试上下文连贯性")
    time.sleep(1)

    # 总结
    print_section("测试完成")
    print("✅ 综合测试已完成")
    print("📊 建议查看:")
    print("   1. 小乐的回答是否准确")
    print("   2. 记忆是否正确存储和检索")
    print("   3. 上下文理解是否连贯")
    print("   4. 未知信息处理是否诚实")
    print("\n💡 下一步:")
    print("   - 根据测试结果优化提示词")
    print("   - 改进记忆检索策略")
    print("   - 增强上下文理解能力\n")


if __name__ == "__main__":
    try:
        # 检查服务是否运行
        response = requests.get(f"{BASE_URL}/", timeout=5)
        if response.status_code == 200:
            run_comprehensive_test()
        else:
            print(f"❌ 服务未正常响应: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print(f"❌ 无法连接到 {BASE_URL}")
        print("请先启动服务: .venv/bin/uvicorn main:app --reload")
    except KeyboardInterrupt:
        print("\n\n⚠️  测试被用户中断")
    except Exception as e:
        print(f"❌ 测试失败: {e}")
