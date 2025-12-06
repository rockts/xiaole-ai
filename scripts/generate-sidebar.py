#!/usr/bin/env python3
"""自动生成 _sidebar.md 导航栏"""

import os
from pathlib import Path
from typing import Dict, List

# 配置
ROOT_DIR = Path(__file__).parent.parent
CATEGORIES = {
    'backend': {'icon': '🔧', 'name': '后端开发'},
    'frontend': {'icon': '🎨', 'name': '前端开发'},
    'architecture': {'icon': '🏗️', 'name': '系统架构'},
    'product': {'icon': '📱', 'name': '产品文档'},
    'dev': {'icon': '🛠️', 'name': '开发运维'},
    'roadmap': {'icon': '🗺️', 'name': '规划与发布'},
}

# 忽略的文件和目录
IGNORE = {'.git', 'node_modules', 'scripts', '__pycache__', '.DS_Store'}
IGNORE_FILES = {'README.md', '_sidebar.md', 'index.html'}

# 文件名到显示名称的映射
def format_title(filename: str) -> str:
    """从文件名生成显示标题"""
    name = filename.replace('.md', '').replace('_', ' ').replace('-', ' ')
    # 保留中文,首字母大写
    return name if any('\u4e00' <= c <= '\u9fff' for c in name) else name.title()

def scan_directory(path: Path, relative_to: Path) -> List[Dict]:
    """递归扫描目录,返回文档树"""
    items = []
    
    if not path.is_dir():
        return items
    
    # 获取所有 md 文件和子目录
    entries = sorted(path.iterdir(), key=lambda x: (x.is_file(), x.name))
    
    for entry in entries:
        if entry.name in IGNORE or entry.name.startswith('.'):
            continue
            
        if entry.is_file() and entry.suffix == '.md' and entry.name not in IGNORE_FILES:
            rel_path = entry.relative_to(relative_to)
            title = format_title(entry.stem)
            items.append({
                'type': 'file',
                'title': title,
                'path': str(rel_path)
            })
        elif entry.is_dir():
            sub_items = scan_directory(entry, relative_to)
            if sub_items:
                items.append({
                    'type': 'dir',
                    'title': format_title(entry.name),
                    'items': sub_items
                })
    
    return items

def generate_sidebar_section(items: List[Dict], indent: int = 2) -> List[str]:
    """生成侧边栏内容"""
    lines = []
    prefix = ' ' * indent
    
    for item in items:
        if item['type'] == 'file':
            lines.append(f"{prefix}* [{item['title']}]({item['path']})")
        elif item['type'] == 'dir':
            lines.append(f"{prefix}* **{item['title']}**")
            lines.extend(generate_sidebar_section(item['items'], indent + 2))
    
    return lines

def main():
    """主函数"""
    output = ['<!-- _sidebar.md -->', '']
    
    # 顶部导航
    output.extend([
        '* [🏠 首页](/)',
        '* [📖 快速参考](QUICK_REFERENCE.md)',
        '* [📋 完整索引](INDEX.md)',
        ''
    ])
    
    # 遍历各个分类
    for category, config in CATEGORIES.items():
        category_path = ROOT_DIR / category
        if not category_path.exists():
            continue
        
        output.append(f"* **{config['icon']} {config['name']}**")
        items = scan_directory(category_path, ROOT_DIR)
        output.extend(generate_sidebar_section(items, indent=2))
        output.append('')
    
    # 其他文档
    other_files = []
    for file in ROOT_DIR.glob('*.md'):
        if file.name not in IGNORE_FILES and not file.name.startswith('_'):
            other_files.append(file)
    
    if other_files:
        output.append('* **📚 其他**')
        for file in sorted(other_files):
            title = format_title(file.stem)
            output.append(f"  * [{title}]({file.name})")
    
    # 写入文件
    sidebar_path = ROOT_DIR / '_sidebar.md'
    with open(sidebar_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(output))
    
    print(f"✅ 已生成 _sidebar.md ({len(output)} 行)")

if __name__ == '__main__':
    main()
