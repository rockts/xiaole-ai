#!/usr/bin/env python3
"""
测试v0.6.0主动问答优化

测试内容:
1. 置信度计算优化（基础分40，更细致的评分）
2. 完整回答识别（减少误判）
3. 追问生成多样化
4. 可配置阈值
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from proactive_qa import ProactiveQA  # noqa: E402


def test_confidence_calculation():
    """测试置信度计算优化"""
    print("=" * 70)
    print("📊 测试置信度计算优化")
    print("=" * 70)

    qa = ProactiveQA()

    test_cases = [
        {
            "name": "极短回答",
            "question": "什么是Docker？",
            "answer": "容器",
            "missing": ["具体名称"],
            "expected_range": (80, 100)
        },
        {
            "name": "带标记词的短回答",
            "question": "Python好用吗？",
            "answer": "不知道",
            "missing": ["完整回答"],
            "expected_range": (80, 100)
        },
        {
            "name": "较完整但有'可能'",
            "question": "怎么学Python？",
            "answer": "可能需要先学基础语法，然后做项目练习",
            "missing": ["操作方法"],
            "expected_range": (60, 80)
        },
        {
            "name": "详细完整回答",
            "question": "什么是Python？",
            "answer": "Python是一种编程语言，具体来说是解释型、高级、面向对象的语言。例如可以用来做数据分析、Web开发等。",
            "missing": [],
            "expected_range": (0, 50)  # 应该很低，因为有完整性指示词
        },
        {
            "name": "长问题短回答",
            "question": "能详细说说Python的异步编程、协程机制、以及如何在实际项目中应用吗？",
            "answer": "可以用async/await",
            "missing": ["操作方法"],
            "expected_range": (70, 100)
        }
    ]

    for case in test_cases:
        confidence = qa._calculate_confidence(
            case["question"],
            case["answer"],
            case["missing"]
        )

        min_exp, max_exp = case["expected_range"]
        status = "✅" if min_exp <= confidence <= max_exp else "❌"

        print(f"\n{status} {case['name']}")
        print(f"   问题: {case['question']}")
        print(f"   回答: {case['answer']}")
        print(f"   置信度: {confidence}% (预期: {min_exp}-{max_exp}%)")


def test_incomplete_detection():
    """测试不完整回答识别优化"""
    print("\n" + "=" * 70)
    print("🔍 测试不完整回答识别优化")
    print("=" * 70)

    qa = ProactiveQA()

    test_cases = [
        ("不知道", True, "明显不完整"),
        ("可能是这样吧", True, "有标记词"),
        ("容器", True, "极短"),
        (
            "Python是一种编程语言，具体来说包括解释器、标准库等组件。"
            "例如CPython是最常用的实现。总之，它是很强大的工具。",
            False,
            "详细完整回答，有'具体来说'、'例如'、'总之'"
        ),
        (
            "首先安装Python，其次学习基础语法，最后通过项目实践提升。",
            False,
            "结构化回答，有'首先'、'其次'、'最后'"
        ),
        ("这个问题比较复杂，建议你先了解基础概念", False, "有'建议'指示词"),
    ]

    for text, expected, reason in test_cases:
        result = qa.is_incomplete_answer(text)
        status = "✅" if result == expected else "❌"

        print(f"\n{status} {reason}")
        print(f"   文本: {text[:50]}{'...' if len(text) > 50 else ''}")
        print(f"   判断: {result} (预期: {expected})")


def test_followup_generation():
    """测试追问生成多样化"""
    print("\n" + "=" * 70)
    print("💬 测试追问生成多样化")
    print("=" * 70)

    qa = ProactiveQA()

    # 生成同一问题的多个追问，验证多样性
    question = "什么是微服务架构？"
    missing_info = ["具体名称"]
    ai_response = "不太清楚"

    print(f"\n原始问题: {question}")
    print(f"AI回答: {ai_response}\n")
    print("生成5个追问（验证多样性）:")

    followups = set()
    for i in range(10):
        followup = qa.generate_followup_question(
            question, missing_info, ai_response
        )
        followups.add(followup)

    for idx, followup in enumerate(sorted(followups), 1):
        print(f"  {idx}. {followup}")

    print(f"\n✅ 生成了 {len(followups)} 种不同的追问表达")


def test_configurable_threshold():
    """测试可配置阈值"""
    print("\n" + "=" * 70)
    print("⚙️  测试可配置阈值")
    print("=" * 70)

    # 测试默认阈值
    qa_default = ProactiveQA()
    print(f"\n默认阈值: {qa_default.confidence_threshold}%")

    # 测试自定义阈值
    qa_custom = ProactiveQA(confidence_threshold=80)
    print(f"自定义阈值: {qa_custom.confidence_threshold}%")

    # 模拟置信度检查
    test_confidences = [50, 65, 70, 80, 90]

    print("\n置信度检查模拟:")
    for conf in test_confidences:
        default_pass = conf >= qa_default.confidence_threshold
        custom_pass = conf >= qa_custom.confidence_threshold

        print(f"  置信度 {conf}%:")
        print(f"    默认阈值(65%): {'✅ 通过' if default_pass else '❌ 不通过'}")
        print(f"    自定义(80%): {'✅ 通过' if custom_pass else '❌ 不通过'}")


def main():
    """运行所有测试"""
    print("\n🧪 v0.6.0 主动问答优化测试\n")

    test_confidence_calculation()
    test_incomplete_detection()
    test_followup_generation()
    test_configurable_threshold()

    print("\n" + "=" * 70)
    print("✅ 所有测试完成！")
    print("=" * 70)
    print("\n💡 优化要点:")
    print("1. 基础置信度从50降到40，减少误触发")
    print("2. 识别完整回答的指示词（例如、总之、首先等）")
    print("3. 追问表达多样化，更自然")
    print("4. 支持环境变量配置阈值: PROACTIVE_QA_THRESHOLD")
    print("\n📝 环境变量配置示例:")
    print("  export PROACTIVE_QA_THRESHOLD=70  # 设置为70%")
    print()


if __name__ == "__main__":
    main()
