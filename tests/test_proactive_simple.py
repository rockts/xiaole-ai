#!/usr/bin/env python3
"""简单测试主动问答"""
from proactive_qa import ProactiveQA
import os
import sys

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend"))


def main():
    print("=" * 60)
    print("测试主动问答")
    print("=" * 60)

    qa = ProactiveQA()
    print("✅ 初始化成功")

    # 测试1: 问题识别
    print("\n1. 测试问题识别")
    test_cases = [
        ("什么是Python？", True),
        ("Python很好用", False),
        ("你觉得呢？", True),
    ]

    for text, expected in test_cases:
        result = qa.is_question(text)
        status = "✅" if result == expected else "❌"
        print(f"  {status} \"{text}\" -> {result} (期望: {expected})")

    # 测试2: 不完整回答识别
    print("\n2. 测试不完整回答识别")
    answer_cases = [
        ("不知道", True),
        ("我不太清楚", True),
        ("Python是一种编程语言，广泛用于数据科学", False),
        ("啊", True),  # 太短
    ]

    for text, expected in answer_cases:
        result = qa.is_incomplete_answer(text)
        status = "✅" if result == expected else "❌"
        print(f"  {status} \"{text}\" -> {result} (期望: {expected})")

    # 测试3: 置信度计算
    print("\n3. 测试置信度计算")
    conf_cases = [
        ("什么是Docker？", "不知道", ["具体名称"]),
        ("什么是Docker？", "啊", ["具体名称"]),
        ("怎么用Python？", "可能需要安装", ["操作方法"]),
    ]

    for question, answer, missing in conf_cases:
        confidence = qa._calculate_confidence(question, answer, missing)
        print(f"  Q: {question}")
        print(f"  A: {answer}")
        print(f"  置信度: {confidence}%")

    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)


if __name__ == "__main__":
    main()
