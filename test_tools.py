"""
测试v0.4.0工具系统

测试工具注册、调用和API接口
"""
import asyncio
import requests


def test_tools_list():
    """测试工具列表API"""
    print("=" * 60)
    print("测试工具列表API")
    print("=" * 60)

    response = requests.get("http://127.0.0.1:8000/tools/list")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ 成功获取工具列表")
        print(f"工具总数: {data['total']}")
        for tool in data['tools']:
            print(f"\n工具名称: {tool['name']}")
            print(f"  描述: {tool['description']}")
            print(f"  分类: {tool['category']}")
            print(f"  启用: {tool['enabled']}")
    else:
        print(f"❌ 请求失败: {response.status_code}")


def test_time_tool():
    """测试时间工具"""
    print("\n" + "=" * 60)
    print("测试时间工具")
    print("=" * 60)

    response = requests.post(
        "http://127.0.0.1:8000/tools/execute",
        params={
            "tool_name": "time",
            "user_id": "test_user"
        },
        json={"format": "full"}
    )

    if response.status_code == 200:
        data = response.json()
        print(f"✅ 工具执行成功: {data['success']}")
        print(f"结果: {data['result']}")
    else:
        print(f"❌ 请求失败: {response.status_code}")


def test_calculator_tool():
    """测试计算器工具"""
    print("\n" + "=" * 60)
    print("测试计算器工具")
    print("=" * 60)

    test_expressions = [
        "2 + 2",
        "10 * 5",
        "sqrt(16)",
        "pi * 2"
    ]

    for expr in test_expressions:
        response = requests.post(
            "http://127.0.0.1:8000/tools/execute",
            params={
                "tool_name": "calculator",
                "user_id": "test_user"
            },
            json={"expression": expr}
        )

        if response.status_code == 200:
            data = response.json()
            if data['success']:
                print(f"✅ {expr} = {data['result']}")
            else:
                print(f"❌ 计算失败: {data['error']}")
        else:
            print(f"❌ 请求失败: {response.status_code}")


def test_system_info_tool():
    """测试系统信息工具"""
    print("\n" + "=" * 60)
    print("测试系统信息工具")
    print("=" * 60)

    response = requests.post(
        "http://127.0.0.1:8000/tools/execute",
        params={
            "tool_name": "system_info",
            "user_id": "test_user"
        },
        json={"info_type": "cpu"}
    )

    if response.status_code == 200:
        data = response.json()
        if data['success']:
            print(f"✅ 系统信息获取成功")
            print(data['result'])
        else:
            print(f"❌ 获取失败: {data['error']}")
    else:
        print(f"❌ 请求失败: {response.status_code}")


def test_tool_history():
    """测试工具历史API"""
    print("\n" + "=" * 60)
    print("测试工具历史API")
    print("=" * 60)

    response = requests.get(
        "http://127.0.0.1:8000/tools/history",
        params={"user_id": "test_user", "limit": 10}
    )

    if response.status_code == 200:
        data = response.json()
        print(f"✅ 成功获取历史记录")
        print(f"历史记录数: {data['total']}")
        for record in data['history']:
            status = "✅" if record['success'] else "❌"
            print(
                f"{status} {record['tool_name']} - "
                f"{record['execution_time']:.3f}s"
            )
    else:
        print(f"❌ 请求失败: {response.status_code}")


def main():
    """运行所有测试"""
    print("\n🚀 v0.4.0 工具系统测试开始\n")

    try:
        # 测试工具列表
        test_tools_list()

        # 测试时间工具
        test_time_tool()

        # 测试计算器
        test_calculator_tool()

        # 测试系统信息
        test_system_info_tool()

        # 测试历史记录
        test_tool_history()

        print("\n" + "=" * 60)
        print("✅ 所有测试完成！")
        print("=" * 60)

    except requests.exceptions.ConnectionError:
        print("\n❌ 无法连接到服务器，请先启动服务器:")
        print("   source .venv/bin/activate && python main.py")
    except Exception as e:
        print(f"\n❌ 测试异常: {e}")


if __name__ == "__main__":
    main()
