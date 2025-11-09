"""
测试记忆冲突检测功能 - v0.3.0
"""

from conflict_detector import ConflictDetector


def test_conflict_detector():
    """测试冲突检测器"""
    print("="*60)
    print("🔍 测试记忆冲突检测功能")
    print("="*60)

    detector = ConflictDetector()

    # 1. 测试关键信息提取
    print("\n📝 Step 1: 测试信息提取...")
    test_texts = [
        "你好，我叫小明，今年25岁",
        "我的生日是3月15日",
        "我是男生，住在北京",
    ]

    for text in test_texts:
        info = detector.extract_key_info(text)
        print(f"  '{text}'")
        print(f"    提取: {info}")

    # 2. 检测记忆冲突
    print("\n🔍 Step 2: 检测记忆库中的冲突...")
    conflicts = detector.detect_conflicts(tag='facts', limit=100)

    if conflicts:
        print(f"\n  ⚠️  发现 {len(conflicts)} 个冲突:")
        for i, c in enumerate(conflicts, 1):
            print(f"\n  【冲突 {i}】{c['type_cn']}")
            print(f"    旧值: {c['old_value']}")
            print(f"    新值: {c['new_value']}")
            print(f"    旧记忆: {c['old_memory'][:40]}...")
            print(f"    新记忆: {c['new_memory'][:40]}...")
    else:
        print("  ✅ 未发现冲突")

    # 3. 获取冲突摘要
    print("\n📊 Step 3: 生成冲突摘要...")
    summary = detector.get_conflict_summary()
    print(f"  {summary['message']}")

    if summary['has_conflicts']:
        print(f"\n  按类型统计:")
        for type_cn, conflicts in summary['conflicts_by_type'].items():
            print(f"    {type_cn}: {len(conflicts)} 个")

    # 4. 生成完整报告
    print("\n📄 Step 4: 生成冲突报告...")
    report = detector.generate_conflict_report()
    print("\n" + report)

    print("\n" + "="*60)
    print("✅ 测试完成!")
    print("="*60)


def test_with_api():
    """通过API测试冲突检测"""
    import requests

    BASE_URL = "http://localhost:8000"

    print("\n" + "="*60)
    print("🌐 测试冲突检测 API")
    print("="*60)

    try:
        # 检测冲突
        print("\n1. GET /memory/conflicts")
        resp = requests.get(f"{BASE_URL}/memory/conflicts")
        if resp.status_code == 200:
            data = resp.json()
            print(f"   总冲突数: {data['total']}")
            print(f"   有冲突: {data['has_conflicts']}")
        else:
            print(f"   ❌ 失败: {resp.status_code}")

        # 获取摘要
        print("\n2. GET /memory/conflicts/summary")
        resp = requests.get(f"{BASE_URL}/memory/conflicts/summary")
        if resp.status_code == 200:
            data = resp.json()
            print(f"   {data['message']}")
        else:
            print(f"   ❌ 失败: {resp.status_code}")

        # 获取报告
        print("\n3. GET /memory/conflicts/report")
        resp = requests.get(f"{BASE_URL}/memory/conflicts/report")
        if resp.status_code == 200:
            data = resp.json()
            print(data['report'])
        else:
            print(f"   ❌ 失败: {resp.status_code}")

    except Exception as e:
        print(f"❌ API测试失败: {e}")

    print("\n" + "="*60)


if __name__ == "__main__":
    # 本地测试
    test_conflict_detector()

    # API测试
    print("\n")
    test_with_api()
