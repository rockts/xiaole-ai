"""
API测试脚本
使用方法: python test_api.py
"""
import requests
import json

BASE_URL = "http://localhost:8000"


def test_home():
    """测试首页"""
    print("=" * 50)
    print("测试 1: 首页")
    print("=" * 50)
    response = requests.get(f"{BASE_URL}/")
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    print()


def test_think():
    """测试思考功能"""
    print("=" * 50)
    print("测试 2: 思考功能 (Claude API)")
    print("=" * 50)
    prompts = [
        "你好，小乐！",
        "你能做什么？",
        "帮我分析一下今天的天气适合做什么"
    ]

    for prompt in prompts:
        response = requests.post(
            f"{BASE_URL}/think",
            params={"prompt": prompt}
        )
        print(f"\n用户: {prompt}")
        print(f"状态码: {response.status_code}")
        result = response.json().get("result", "")
        print(f"小乐: {result}")
        print("-" * 50)


def test_act():
    """测试执行任务"""
    print("=" * 50)
    print("测试 3: 执行任务")
    print("=" * 50)
    commands = [
        "记住我喜欢喝咖啡",
        "帮我记录今天学习了Python",
        "记住我的生日是1月1日"
    ]

    for cmd in commands:
        response = requests.post(f"{BASE_URL}/act", params={"command": cmd})
        print(f"命令: {cmd}")
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
        print()


def test_memory():
    """测试查看记忆"""
    print("=" * 50)
    print("测试 4: 查看记忆")
    print("=" * 50)
    response = requests.get(f"{BASE_URL}/memory", params={"tag": "task"})
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    print()


def main():
    print("\n🚀 开始测试小乐AI API\n")

    try:
        test_home()
        test_think()
        test_act()
        test_memory()

        print("=" * 50)
        print("✅ 所有测试完成！")
        print("=" * 50)

    except requests.exceptions.ConnectionError:
        print("❌ 错误: 无法连接到服务器")
        print("请确保服务器正在运行: uvicorn main:app --reload")
    except Exception as e:
        print(f"❌ 错误: {e}")


if __name__ == "__main__":
    main()
