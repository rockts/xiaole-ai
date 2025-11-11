"""
测试文件工具在对话中的集成
"""
import requests
import time


def chat(prompt):
    """发送聊天请求"""
    print(f"\n👤 用户: {prompt}")
    print("🤖 小乐: ", end="", flush=True)

    try:
        response = requests.post(
            "http://localhost:8000/chat",
            params={"prompt": prompt},
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            reply = data.get("reply", "")  # 改为reply字段
            print(reply)

            # 显示工具调用信息
            if data.get("tool_used"):
                print(f"\n  💡 使用了工具: {data.get('tool_used')}")

            return reply
        else:
            print(f"❌ 错误: {response.status_code}")
            return None

    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return None


def main():
    """测试文件工具对话"""
    print("="*60)
    print("测试文件工具在对话中的集成")
    print("="*60)

    # 测试1: 写入文件
    chat("帮我创建一个文件叫 shopping.txt，内容是：牛奶、鸡蛋、面包、水果")
    time.sleep(2)

    # 测试2: 读取文件
    chat("读取 shopping.txt 文件，看看里面有什么")
    time.sleep(2)

    # 测试3: 列出文件
    chat("列出所有文件")
    time.sleep(2)

    # 测试4: 写入JSON
    chat(
        "创建一个 user.json 文件，内容是：{\"name\": \"小明\", \"age\": 25, \"city\": \"深圳\"}")
    time.sleep(2)

    # 测试5: 搜索txt文件
    chat("搜索所有txt文件")
    time.sleep(2)

    print("\n" + "="*60)
    print("测试完成")
    print("="*60)


if __name__ == "__main__":
    main()
