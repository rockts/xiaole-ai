#!/usr/bin/env python3
"""
文件工具完整演示
"""
from tools.file_tool import FileTool
import sys
import os
import asyncio

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


async def demo():
    tool = FileTool()

    print('=' * 70)
    print(' ' * 20 + '✨ 小乐AI文件工具演示')
    print('=' * 70)
    print('\n📍 工作目录: /tmp/xiaole_files/')
    print()

    # 1. 写入示例文件
    print('📝 1. 创建示例文件')
    print('-' * 70)

    examples = {
        'hello.txt': 'Hello from 小乐AI!\n这是一个测试文件。',
        'notes.md': '# 我的笔记\n\n## 学习内容\n- 小乐AI的文件操作\n- Python异步编程',
        'config.json': '{\n  "name": "xiaole",\n  "version": "0.5.0"\n}'
    }

    for filename, content in examples.items():
        result = await tool.execute(operation='write', path=filename, content=content)
        if result['success']:
            print(f'  ✅ {filename} - {result["size"]}字节, {result["lines"]}行')
        else:
            print(f'  ❌ {filename} - {result["error"]}')

    # 2. 读取文件
    print('\n📖 2. 读取文件内容')
    print('-' * 70)
    result = await tool.execute(operation='read', path='hello.txt')
    if result['success']:
        print(f'  文件: {result["path"]}')
        print(f'  大小: {result["size"]}字节')
        print(f'  行数: {result["lines"]}行')
        print(f'  内容:\n{result["content"]}')

    # 3. 列出所有文件
    print('\n📁 3. 列出所有文件')
    print('-' * 70)
    result = await tool.execute(operation='list', path='.')
    if result['success']:
        print(f'  共 {result["file_count"]} 个文件, {result["dir_count"]} 个目录')
        print('\n  文件列表:')
        for f in result['files']:
            size_kb = f['size'] / 1024
            print(
                f'    • {f["name"]:<20} {size_kb:>8.2f} KB  {f["extension"]}')

    # 4. 搜索文件
    print('\n🔍 4. 搜索文件')
    print('-' * 70)
    result = await tool.execute(
        operation='search', path='.', pattern='*.txt'
    )
    if result['success']:
        print(f'  找到 {result["count"]} 个 .txt 文件')
        for file in result['results'][:5]:  # 只显示前5个
            print(f'    • {file["name"]:<20} {file["size"]} 字节')
    else:
        print(f'  ❌ {result["error"]}')

    # 5. JSON文件示例
    print('\n📄 5. 读取JSON配置')
    print('-' * 70)
    result = await tool.execute(operation='read', path='config.json')
    if result['success']:
        print(f'  {result["content"]}')

    print('\n' + '=' * 70)
    print('✅ 演示完成！')
    print('=' * 70)
    print('\n💡 提示:')
    print('  - 所有文件保存在: /tmp/xiaole_files/')
    print('  - 你可以直接对小乐说: "帮我读取hello.txt"')
    print('  - 或者说: "创建一个notes.md，内容是..."')
    print()

if __name__ == '__main__':
    asyncio.run(demo())
