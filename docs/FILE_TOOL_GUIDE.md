# 文件操作工具使用指南

## 🎯 功能概述

文件工具 (FileTool) 提供安全的文件操作功能，支持读取、写入、列表和搜索文件。

## 🔒 安全限制

### 1. 路径白名单
只能操作以下目录：
- `/tmp/xiaole_files/` （默认工作目录）

**注意**: 这是系统临时目录，重启后可能清空。如需持久化文件，建议后续配置其他目录。

### 2. 文件类型白名单
支持的文件类型：
- **文本**: txt, md, log
- **配置**: json, yaml, yml, xml, toml, ini, conf
- **代码**: py, js, ts, jsx, tsx, html, css, sh
- **数据**: csv, tsv

### 3. 文件大小限制
- 最大 5MB

## 📝 使用方法

### 方法1: 通过聊天界面（推荐）

直接告诉小乐你想做什么：

#### 读取文件
```
"帮我读取test.txt文件"
"打开notes.md看看内容"
"查看config.json"
```

#### 写入文件
```
"帮我在test.txt写入：Hello, World!"
"创建一个notes.md文件，内容是今天的学习笔记"
"把这段JSON保存到config.json"
```

#### 列出文件
```
"列出所有文件"
"文件夹里有什么文件？"
```

#### 搜索文件
```
"搜索包含'Python'的文件"
"找出包含'TODO'的文件"
```

### 方法2: 直接测试（开发用）

```bash
# 进入项目目录
cd /Users/rockts/Dev/xiaole-ai

# 激活虚拟环境
source .venv/bin/activate

# 运行Python测试
python3 -c "
import sys
import asyncio
sys.path.insert(0, '/Users/rockts/Dev/xiaole-ai')

from tools.file_tool import FileTool

async def test():
    tool = FileTool()
    
    # 1. 创建测试文件
    print('1. 写入文件...')
    result = await tool.execute(
        operation='write',
        path='workspace/test.txt',
        content='Hello from 小乐AI!'
    )
    print(f'结果: {result}')
    
    # 2. 读取文件
    print('\n2. 读取文件...')
    result = await tool.execute(
        operation='read',
        path='workspace/test.txt'
    )
    print(f'内容: {result.get(\"data\")}')
    
    # 3. 列出文件
    print('\n3. 列出文件...')
    result = await tool.execute(
        operation='list',
        path='workspace'
    )
    print(f'文件列表: {result.get(\"data\")}')

asyncio.run(test())
"
```

## 📚 API参数说明

### read_file - 读取文件
```python
operation: "read"
path: "workspace/test.txt"  # 相对于白名单目录的路径
```

### write_file - 写入文件
```python
operation: "write"
path: "workspace/test.txt"
content: "文件内容"  # 要写入的内容
```

### list_files - 列出文件
```python
operation: "list"
path: "workspace"  # 要列出的目录
```

### search_files - 搜索文件
```python
operation: "search"
path: "workspace"  # 搜索目录
pattern: "Python"  # 搜索关键词
```

## ⚠️ 常见错误

### 1. 路径不在白名单
```
错误: 文件路径不在允许的目录中
解决: 确保文件在 workspace/ 目录下
```

### 2. 文件类型不支持
```
错误: 不支持的文件类型
解决: 只能操作txt, md, json等支持的类型
```

### 3. 文件太大
```
错误: 文件大小超过限制
解决: 文件必须小于5MB
```

### 4. 目录不存在
```
错误: 目录不存在
解决: 工具会自动创建workspace目录
```

## 💡 实用示例

### 示例1: 创建学习笔记
```
对小乐说: "帮我创建workspace/python_notes.md，内容是：
# Python学习笔记
- 今天学了列表推导式
- 明天要学装饰器
"
```

### 示例2: 保存代码片段
```
对小乐说: "把这段代码保存到workspace/example.py：
def hello():
    print('Hello, World!')
"
```

### 示例3: 整理待办事项
```
对小乐说: "在workspace/todo.txt写入我今天的任务清单：
1. 完成项目报告
2. 复习Python
3. 锻炼30分钟
"
```

### 示例4: 查看配置文件
```
对小乐说: "帮我读取workspace/config.json看看配置对不对"
```

## 🔍 调试技巧

如果文件操作失败：

1. **检查路径**
   ```bash
   ls -la /Users/rockts/Dev/xiaole-ai/workspace/
   ```

2. **检查权限**
   ```bash
   chmod 755 /Users/rockts/Dev/xiaole-ai/workspace/
   ```

3. **查看日志**
   ```bash
   tail -f /Users/rockts/Dev/xiaole-ai/logs/xiaole_ai.log
   ```

4. **手动测试**
   ```bash
   cd /Users/rockts/Dev/xiaole-ai
   mkdir -p workspace
   echo "test" > workspace/test.txt
   cat workspace/test.txt
   ```

## 📊 使用统计

你可以在"工具管理"标签页查看：
- 文件操作次数
- 最近操作记录
- 操作成功率
- 平均执行时间

---

**创建时间**: 2025-11-10  
**版本**: v0.5.0  
**状态**: ✅ 已实现并测试通过
