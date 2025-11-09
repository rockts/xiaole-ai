#!/usr/bin/env python3
"""
记忆冲突检测演示 - v0.3.0
展示如何自动发现矛盾的记忆信息
"""

from conflict_detector import ConflictDetector


def demo():
    print("\n" + "="*70)
    print("🔍 小乐AI v0.3.0 - 记忆冲突检测演示")
    print("="*70)

    detector = ConflictDetector()

    # 演示：提取关键信息
    print("\n【功能1】从对话中提取关键信息")
    print("-"*70)

    examples = [
        "你好，我叫张三，今年28岁",
        "我的生日是5月20日，住在上海",
        "我是男生，喜欢打篮球"
    ]

    for text in examples:
        info = detector.extract_key_info(text)
        print(f"\n对话: {text}")
        if info:
            print(f"提取: {', '.join([f'{k}={v}' for k, v in info.items()])}")
        else:
            print("提取: (无关键信息)")

    # 演示：检测冲突
    print("\n\n【功能2】检测记忆库中的冲突")
    print("-"*70)

    conflicts = detector.detect_conflicts(tag='facts', limit=100)

    if not conflicts:
        print("\n✅ 记忆库健康，未发现冲突")
        print("\n💡 提示：当系统记录了矛盾的信息时（如不同的生日、年龄），")
        print("   冲突检测器会自动发现并提醒你。")
    else:
        print(f"\n⚠️  发现 {len(conflicts)} 个冲突：\n")

        for i, c in enumerate(conflicts[:5], 1):  # 最多显示5个
            print(f"【冲突 {i}】{c['type_cn']}")
            print(f"  旧值: {c['old_value']}")
            print(f"  新值: {c['new_value']}")
            print(f"  旧记忆: {c['old_memory'][:50]}")
            print(f"  新记忆: {c['new_memory'][:50]}")
            print(f"  时间: {c['old_time'].strftime('%m-%d')} "
                  f"→ {c['new_time'].strftime('%m-%d')}\n")

        if len(conflicts) > 5:
            print(f"... 还有 {len(conflicts)-5} 个冲突")

    # 演示：生成报告
    print("\n【功能3】生成冲突摘要")
    print("-"*70)

    summary = detector.get_conflict_summary()
    print(f"\n{summary['message']}")

    if summary['has_conflicts']:
        print("\n按类型统计:")
        for type_cn, conflicts in summary['conflicts_by_type'].items():
            print(f"  • {type_cn}: {len(conflicts)} 个冲突")

        print("\n💡 建议：访问 http://localhost:8000/memory/conflicts/report")
        print("   获取完整的冲突分析报告")

    print("\n" + "="*70)
    print("✨ v0.3.0 Learning层功能：")
    print("   1. ✅ 用户行为分析（对话模式、话题偏好）")
    print("   2. ✅ 记忆冲突检测（自动发现矛盾信息）")
    print("   3. 🚧 主动问答（开发中...）")
    print("="*70 + "\n")


if __name__ == "__main__":
    try:
        demo()
    except KeyboardInterrupt:
        print("\n\n👋 退出演示")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
