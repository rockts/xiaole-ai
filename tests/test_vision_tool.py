#!/usr/bin/env python3
"""
测试图片识别工具

v0.6.0 Phase 4 - 多模态支持
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vision_tool import VisionTool
from pathlib import Path


def test_initialization():
    """测试初始化"""
    print("=" * 60)
    print("测试1: Vision Tool初始化")
    print("=" * 60)
    
    tool = VisionTool()
    
    print(f"API类型: {tool.api_type}")
    print(f"Claude可用: {'✅' if tool.claude_key else '❌'}")
    print(f"GPT-4V可用: {'✅' if tool.openai_key else '❌'}")
    print(f"支持格式: {', '.join(tool.supported_formats)}")
    print(f"上传目录: {tool.upload_dir}")
    
    # 检查上传目录是否创建
    assert tool.upload_dir.exists(), "上传目录应该存在"
    
    print("\n✅ 初始化测试通过")


def test_image_validation():
    """测试图片验证"""
    print("\n" + "=" * 60)
    print("测试2: 图片验证")
    print("=" * 60)
    
    tool = VisionTool()
    
    # 测试不存在的文件
    print("\n测试不存在的文件:")
    valid, error = tool.validate_image("nonexistent.jpg")
    print(f"  结果: {'✅ 有效' if valid else f'❌ {error}'}")
    assert not valid, "不存在的文件应该无效"
    assert "不存在" in error, "错误信息应该包含'不存在'"
    
    # 测试不支持的格式
    print("\n测试不支持的格式:")
    # 创建临时文件
    test_file = Path("test.txt")
    test_file.write_text("test")
    
    valid, error = tool.validate_image(str(test_file))
    print(f"  结果: {'✅ 有效' if valid else f'❌ {error}'}")
    assert not valid, "不支持的格式应该无效"
    assert "不支持" in error, "错误信息应该包含'不支持'"
    
    # 清理
    test_file.unlink()
    
    print("\n✅ 图片验证测试通过")


def test_file_save():
    """测试文件保存"""
    print("\n" + "=" * 60)
    print("测试3: 文件保存")
    print("=" * 60)
    
    tool = VisionTool()
    
    # 模拟文件数据
    file_data = b"fake image data"
    filename = "test_image.jpg"
    
    print(f"\n保存文件: {filename}")
    print(f"文件大小: {len(file_data)} bytes")
    
    success, result = tool.save_upload(file_data, filename)
    
    print(f"结果: {'✅ 成功' if success else f'❌ 失败'}")
    
    if success:
        print(f"保存路径: {result}")
        saved_path = Path(result)
        assert saved_path.exists(), "文件应该存在"
        assert saved_path.read_bytes() == file_data, "文件内容应该匹配"
        
        # 清理
        saved_path.unlink()
        print("✅ 文件已保存并验证")
    else:
        print(f"错误: {result}")
        assert False, f"保存应该成功，但失败了: {result}"
    
    print("\n✅ 文件保存测试通过")


def test_analyze_without_api():
    """测试没有API密钥的情况"""
    print("\n" + "=" * 60)
    print("测试4: 无API密钥时的行为")
    print("=" * 60)
    
    # 临时清除API密钥
    original_claude = os.environ.get('CLAUDE_API_KEY')
    original_openai = os.environ.get('OPENAI_API_KEY')
    
    if 'CLAUDE_API_KEY' in os.environ:
        del os.environ['CLAUDE_API_KEY']
    if 'OPENAI_API_KEY' in os.environ:
        del os.environ['OPENAI_API_KEY']
    
    tool = VisionTool()
    
    # 创建临时测试图片
    test_image = Path("test_img.jpg")
    test_image.write_bytes(b"fake image")
    
    print("\n测试分析图片（无API密钥）:")
    result = tool.analyze_image(str(test_image))
    
    print(f"成功: {result.get('success')}")
    print(f"错误: {result.get('error', 'N/A')}")
    
    assert not result['success'], "没有API密钥应该失败"
    assert 'API密钥' in result['error'] or '配置' in result['error'], \
        "错误信息应该提示API密钥问题"
    
    # 恢复API密钥
    if original_claude:
        os.environ['CLAUDE_API_KEY'] = original_claude
    if original_openai:
        os.environ['OPENAI_API_KEY'] = original_openai
    
    # 清理
    test_image.unlink()
    
    print("\n✅ 无API密钥测试通过")


def test_tool_interface():
    """测试工具接口"""
    print("\n" + "=" * 60)
    print("测试5: 工具接口")
    print("=" * 60)
    
    from vision_tool import vision_tool_interface, VISION_TOOL_META
    
    # 测试元数据
    print("\n工具元数据:")
    print(f"  名称: {VISION_TOOL_META['name']}")
    print(f"  描述: {VISION_TOOL_META['description']}")
    print(f"  类别: {VISION_TOOL_META['category']}")
    print(f"  参数: {list(VISION_TOOL_META['parameters'].keys())}")
    
    assert VISION_TOOL_META['name'] == 'vision', "工具名称应该是vision"
    assert 'image_path' in VISION_TOOL_META['parameters'], \
        "应该有image_path参数"
    
    # 测试缺少参数的情况
    print("\n测试缺少必需参数:")
    result = vision_tool_interface({})
    print(f"  成功: {result.get('success')}")
    print(f"  错误: {result.get('error', 'N/A')}")
    
    assert not result['success'], "缺少参数应该失败"
    assert 'image_path' in result['error'], "错误应该提示缺少image_path"
    
    print("\n✅ 工具接口测试通过")


def run_all_tests():
    """运行所有测试"""
    print("\n🧪 开始测试 Vision Tool 模块")
    print("=" * 60)
    
    try:
        test_initialization()
        test_image_validation()
        test_file_save()
        test_analyze_without_api()
        test_tool_interface()
        
        print("\n" + "=" * 60)
        print("🎉 所有测试通过！")
        print("=" * 60)
        print("\n💡 提示: 要测试实际的图片识别功能，请:")
        print("  1. 配置CLAUDE_API_KEY或OPENAI_API_KEY")
        print("  2. 准备一张测试图片")
        print("  3. 运行: python vision_tool.py")
        return True
        
    except AssertionError as e:
        print(f"\n❌ 测试失败: {e}")
        return False
    except Exception as e:
        print(f"\n💥 测试异常: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
