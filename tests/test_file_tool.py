"""
测试文件工具功能
"""
from tools.file_tool import file_tool
import asyncio
import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend"))


async def test_write_file():
    """测试写入文件"""
    print("\n=== 测试1: 写入文件 ===")
    result = await file_tool.execute(
        operation="write",
        path="test.txt",
        content="Hello, 小乐AI!\n这是一个测试文件。\n支持多行内容。"
    )
    print(f"写入结果: {result}")
    assert result["success"], "写入文件失败"
    print("✅ 写入文件测试通过")


async def test_read_file():
    """测试读取文件"""
    print("\n=== 测试2: 读取文件 ===")
    result = await file_tool.execute(
        operation="read",
        path="test.txt"
    )
    print(f"读取结果:")
    print(f"  - 成功: {result['success']}")
    print(f"  - 文件大小: {result.get('size')} 字节")
    print(f"  - 行数: {result.get('lines')}")
    print(f"  - 内容预览: {result.get('content', '')[:50]}...")
    assert result["success"], "读取文件失败"
    assert "Hello, 小乐AI!" in result["content"], "文件内容不匹配"
    print("✅ 读取文件测试通过")


async def test_list_files():
    """测试列出文件"""
    print("\n=== 测试3: 列出文件 ===")
    result = await file_tool.execute(
        operation="list",
        path=".",
        recursive=False
    )
    print(f"列表结果:")
    print(f"  - 成功: {result['success']}")
    print(f"  - 文件数: {result.get('file_count')}")
    print(f"  - 目录数: {result.get('dir_count')}")
    if result.get("files"):
        print(f"  - 文件列表: {[f['name'] for f in result['files'][:5]]}")
    assert result["success"], "列出文件失败"
    print("✅ 列出文件测试通过")


async def test_search_files():
    """测试搜索文件"""
    print("\n=== 测试4: 搜索文件 ===")
    result = await file_tool.execute(
        operation="search",
        path=".",
        pattern="*.txt",
        recursive=False
    )
    print(f"搜索结果:")
    print(f"  - 成功: {result['success']}")
    print(f"  - 找到数量: {result.get('count')}")
    if result.get("results"):
        print(f"  - 文件列表: {[f['name'] for f in result['results']]}")
    assert result["success"], "搜索文件失败"
    assert result["count"] > 0, "未找到txt文件"
    print("✅ 搜索文件测试通过")


async def test_json_file():
    """测试JSON文件操作"""
    print("\n=== 测试5: JSON文件 ===")

    # 写入JSON
    json_content = """{
  "name": "小乐AI",
  "version": "0.5.0",
  "features": ["提醒", "搜索", "文件操作"]
}"""

    result = await file_tool.execute(
        operation="write",
        path="config.json",
        content=json_content
    )
    assert result["success"], "写入JSON文件失败"

    # 读取JSON
    result = await file_tool.execute(
        operation="read",
        path="config.json"
    )
    assert result["success"], "读取JSON文件失败"
    assert "小乐AI" in result["content"], "JSON内容不匹配"
    print("✅ JSON文件测试通过")


async def test_security_path():
    """测试路径安全限制"""
    print("\n=== 测试6: 路径安全限制 ===")

    # 尝试访问不允许的路径
    result = await file_tool.execute(
        operation="read",
        path="/etc/passwd"
    )
    print(f"访问/etc/passwd结果: {result}")
    assert not result["success"], "应该拒绝访问系统文件"
    assert "不安全" in result["error"], "应该有安全错误提示"
    print("✅ 路径安全测试通过")


async def test_security_extension():
    """测试文件类型限制"""
    print("\n=== 测试7: 文件类型限制 ===")

    # 尝试写入不支持的文件类型
    result = await file_tool.execute(
        operation="write",
        path="test.exe",
        content="malicious code"
    )
    print(f"写入.exe文件结果: {result}")
    assert not result["success"], "应该拒绝不支持的文件类型"
    assert "不支持" in result["error"], "应该有文件类型错误提示"
    print("✅ 文件类型限制测试通过")


async def test_markdown_file():
    """测试Markdown文件"""
    print("\n=== 测试8: Markdown文件 ===")

    md_content = """# 小乐AI测试文档

## 功能列表
- 文件读取
- 文件写入
- 文件搜索

## 安全特性
- 路径白名单
- 文件类型限制
- 大小限制
"""

    result = await file_tool.execute(
        operation="write",
        path="README.md",
        content=md_content
    )
    assert result["success"], "写入Markdown文件失败"

    result = await file_tool.execute(
        operation="read",
        path="README.md"
    )
    assert result["success"], "读取Markdown文件失败"
    assert "小乐AI测试文档" in result["content"], "Markdown内容不匹配"
    print("✅ Markdown文件测试通过")


async def main():
    """运行所有测试"""
    print("开始测试文件工具...")
    print(f"工作目录: {file_tool.ALLOWED_DIRS[0]}")

    try:
        # 基础功能测试
        await test_write_file()
        await test_read_file()
        await test_list_files()
        await test_search_files()

        # 特定格式测试
        await test_json_file()
        await test_markdown_file()

        # 安全测试
        await test_security_path()
        await test_security_extension()

        print("\n" + "="*50)
        print("✅ 所有测试通过！")
        print("="*50)

    except AssertionError as e:
        print(f"\n❌ 测试失败: {e}")
        return False
    except Exception as e:
        print(f"\n❌ 测试出错: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
