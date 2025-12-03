#!/usr/bin/env python3
"""
图片识别调试脚本 - 直接测试Qwen API和路径解析逻辑
"""
import os
import sys
import base64
import requests
import json
from pathlib import Path

# 添加backend目录到sys.path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

# 配置
QWEN_API_KEY = "sk-69ef2e83e8f44fb58d35911b9ae51091"
QWEN_API_URL = "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation"
TEST_IMAGE = "/Users/rockts/Dev/xiaole-ai/backend/uploads/images/1764132998_c86e07e7-27c5-4d2b-99d4-03c58e82e83e.png"


def test_path_resolution():
    """测试路径解析逻辑"""
    print("=" * 60)
    print("🔍 测试1: 路径解析")
    print("=" * 60)

    test_paths = [
        "/uploads/images/1764132998_c86e07e7-27c5-4d2b-99d4-03c58e82e83e.png",
        "uploads/images/1764132998_c86e07e7-27c5-4d2b-99d4-03c58e82e83e.png",
        "/Users/rockts/Dev/xiaole-ai/backend/uploads/images/1764132998_c86e07e7-27c5-4d2b-99d4-03c58e82e83e.png"
    ]

    uploads_dir = Path(__file__).parent / "backend" / "uploads"
    print(f"UPLOADS_DIR: {uploads_dir}")
    print(f"UPLOADS_DIR exists: {uploads_dir.exists()}")
    print()

    for test_path in test_paths:
        print(f"输入路径: {test_path}")

        # 模拟vision_tool的_resolve_path逻辑
        if test_path.startswith("/uploads/") or test_path.startswith("uploads/"):
            clean_path = test_path.lstrip("/").replace("uploads/", "", 1)
            potential_path = uploads_dir / clean_path
            print(f"  → 清理后: {clean_path}")
            print(f"  → 解析为: {potential_path}")
            print(f"  → 文件存在: {potential_path.exists()}")
        else:
            print(f"  → 绝对路径，直接检查")
            print(f"  → 文件存在: {Path(test_path).exists()}")
        print()


def test_qwen_api():
    """测试Qwen API调用"""
    print("=" * 60)
    print("🤖 测试2: Qwen API调用")
    print("=" * 60)

    # 检查测试图片
    if not os.path.exists(TEST_IMAGE):
        print(f"❌ 测试图片不存在: {TEST_IMAGE}")
        return False

    print(f"✅ 测试图片: {TEST_IMAGE}")
    print(f"   文件大小: {os.path.getsize(TEST_IMAGE)} bytes")
    print()

    try:
        # 读取并编码图片
        with open(TEST_IMAGE, "rb") as f:
            base64_image = base64.b64encode(f.read()).decode('utf-8')

        print(f"✅ 图片Base64编码完成 (长度: {len(base64_image)})")
        print()

        # 构造请求
        data_uri = f"data:image/png;base64,{base64_image}"
        headers = {
            "Authorization": f"Bearer {QWEN_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "qwen-vl-plus",
            "input": {
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"image": data_uri},
                            {"text": "请详细描述这张图片的内容。"}
                        ]
                    }
                ]
            }
        }

        print("📤 发送API请求...")
        print(f"   URL: {QWEN_API_URL}")
        print(f"   Model: qwen-vl-plus")
        print(f"   API Key: {QWEN_API_KEY[:20]}...")
        print()

        response = requests.post(
            QWEN_API_URL, headers=headers, json=payload, timeout=60)

        print(f"📥 收到响应: HTTP {response.status_code}")
        print()

        if response.status_code == 200:
            result = response.json()
            print("✅ API调用成功!")
            print()
            print("完整响应:")
            print(json.dumps(result, ensure_ascii=False, indent=2))
            print()

            # 提取描述
            if "output" in result and "choices" in result["output"]:
                content = result["output"]["choices"][0]["message"]["content"][0]["text"]
                print("=" * 60)
                print("🎯 图片描述:")
                print("=" * 60)
                print(content)
                return True
            else:
                print("❌ 响应格式异常，无法提取描述")
                return False
        else:
            print(f"❌ API调用失败: {response.status_code}")
            print(f"响应内容: {response.text}")
            return False

    except Exception as e:
        print(f"❌ 异常: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_vision_tool_import():
    """测试vision_tool模块导入"""
    print("=" * 60)
    print("📦 测试3: vision_tool模块导入")
    print("=" * 60)

    try:
        from tools.vision_tool import VisionTool
        print("✅ VisionTool导入成功")

        tool = VisionTool()
        print(f"   工具名称: {tool.name}")
        print(f"   工具描述: {tool.description}")
        print(f"   Qwen Key 已配置: {bool(tool.qwen_key)}")
        print()

        return True
    except Exception as e:
        print(f"❌ 导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("🚀 小乐AI - 图片识别调试工具")
    print()

    # 运行所有测试
    test_path_resolution()
    test_qwen_api()
    test_vision_tool_import()

    print()
    print("=" * 60)
    print("✅ 调试完成")
    print("=" * 60)
