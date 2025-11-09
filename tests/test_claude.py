#!/usr/bin/env python3
"""
快速测试 Claude API 配置
"""
import os
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()


def test_claude_api():
    """测试 Claude API 是否配置正确"""
    print("🔍 检查 Claude API 配置...\n")

    # 检查 API Key
    api_key = os.getenv("CLAUDE_API_KEY")
    if not api_key:
        print("❌ 错误: 未找到 CLAUDE_API_KEY")
        print("请在 .env 文件中配置 CLAUDE_API_KEY")
        return False

    if api_key == "your_claude_api_key_here":
        print("❌ 错误: CLAUDE_API_KEY 未配置")
        print("请将 .env 文件中的 CLAUDE_API_KEY 替换为你的实际 API Key")
        return False

    print(f"✅ API Key 已配置: {api_key[:15]}...{api_key[-4:]}")

    # 检查模型配置
    model = os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-20241022")
    print(f"✅ 使用模型: {model}\n")

    # 测试 API 调用
    print("🚀 测试 API 调用...")
    try:
        client = Anthropic(api_key=api_key)

        response = client.messages.create(
            model=model,
            max_tokens=100,
            messages=[
                {
                    "role": "user",
                    "content": "你好！请用一句话简短地介绍你自己。"
                }
            ]
        )

        reply = response.content[0].text
        print("✅ API 调用成功！\n")
        print("=" * 50)
        print("Claude 的回复:")
        print("=" * 50)
        print(reply)
        print("=" * 50)

        return True

    except Exception as e:
        print(f"❌ API 调用失败: {str(e)}")
        return False


def main():
    print("\n" + "=" * 50)
    print("   Claude API 配置测试")
    print("=" * 50 + "\n")

    success = test_claude_api()

    print("\n" + "=" * 50)
    if success:
        print("✅ 测试通过！Claude API 配置正确！")
        print("\n你现在可以：")
        print("1. 启动服务: uvicorn main:app --reload")
        print("2. 运行测试: python test_api.py")
        print("3. 访问文档: http://localhost:8000/docs")
    else:
        print("❌ 测试失败！请检查配置。")
        print("\n请参考 SETUP_CLAUDE.md 文件进行配置")
    print("=" * 50 + "\n")


if __name__ == "__main__":
    main()
