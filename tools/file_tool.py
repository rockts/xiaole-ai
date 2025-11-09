"""
文件操作工具
支持文件读取、写入、列表、搜索等功能
包含安全限制：路径白名单、文件类型限制、大小限制
"""
import os
import glob
import aiofiles
from pathlib import Path
from typing import Dict, Any, Optional
from tool_manager import Tool


class FileTool(Tool):
    """文件操作工具"""

    # 安全配置
    ALLOWED_DIRS = [
        "/tmp/xiaole_files",  # 默认工作目录
        # 可以通过配置添加更多允许的目录
    ]

    ALLOWED_EXTENSIONS = [
        ".txt", ".md", ".json", ".csv",
        ".log", ".xml", ".yaml", ".yml",
        ".py", ".js", ".html", ".css"
    ]

    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    MAX_SEARCH_RESULTS = 100

    def __init__(self):
        super().__init__()
        self.name = "file"
        self.description = "文件操作工具，支持读取、写入、列表、搜索文件"
        self.parameters = {
            "operation": {
                "type": "string",
                "description": (
                    "操作类型: read(读取), write(写入), "
                    "list(列表), search(搜索)"
                ),
                "required": True
            },
            "path": {
                "type": "string",
                "description": "文件或目录路径（相对于允许的目录）",
                "required": True
            },
            "content": {
                "type": "string",
                "description": "写入的内容（仅用于write操作）",
                "required": False
            },
            "pattern": {
                "type": "string",
                "description": "搜索模式（仅用于search操作，支持通配符如*.txt）",
                "required": False
            },
            "recursive": {
                "type": "boolean",
                "description": "是否递归搜索（仅用于list和search操作）",
                "required": False,
                "default": False
            }
        }

        # 确保默认工作目录存在
        self._ensure_default_dir()

    def _ensure_default_dir(self):
        """确保默认工作目录存在"""
        default_dir = self.ALLOWED_DIRS[0]
        os.makedirs(default_dir, exist_ok=True)

    def _resolve_path(self, path: str) -> Optional[Path]:
        """
        解析并验证路径
        返回绝对路径或None（如果路径不安全）
        """
        # 如果是相对路径，使用默认目录
        if not os.path.isabs(path):
            path = os.path.join(self.ALLOWED_DIRS[0], path)

        # 规范化路径
        resolved = Path(path).resolve()

        # 检查是否在允许的目录内
        for allowed_dir in self.ALLOWED_DIRS:
            allowed_path = Path(allowed_dir).resolve()
            try:
                resolved.relative_to(allowed_path)
                return resolved
            except ValueError:
                continue

        return None

    def _check_extension(self, path: Path) -> bool:
        """检查文件扩展名是否允许"""
        return path.suffix.lower() in self.ALLOWED_EXTENSIONS

    def _check_size(self, path: Path) -> bool:
        """检查文件大小是否超过限制"""
        if not path.exists():
            return True
        return path.stat().st_size <= self.MAX_FILE_SIZE

    async def execute(self, **kwargs) -> Dict[str, Any]:
        """执行文件操作"""
        operation = kwargs.get("operation")
        path_str = kwargs.get("path")

        if not operation or not path_str:
            return {
                "success": False,
                "error": "缺少必要参数: operation 和 path"
            }

        # 验证操作类型
        valid_operations = ["read", "write", "list", "search"]
        if operation not in valid_operations:
            return {
                "success": False,
                "error": (
                    f"无效的操作类型: {operation}，"
                    f"支持: {', '.join(valid_operations)}"
                )
            }

        # 解析路径
        path = self._resolve_path(path_str)
        if not path:
            return {
                "success": False,
                "error": f"路径不安全或不在允许的目录内: {path_str}"
            }

        # 执行对应操作
        try:
            if operation == "read":
                return await self._read_file(path)
            elif operation == "write":
                content = kwargs.get("content", "")
                return await self._write_file(path, content)
            elif operation == "list":
                recursive = kwargs.get("recursive", False)
                return await self._list_files(path, recursive)
            elif operation == "search":
                pattern = kwargs.get("pattern", "*")
                recursive = kwargs.get("recursive", False)
                return await self._search_files(path, pattern, recursive)
        except Exception as e:
            return {
                "success": False,
                "error": f"执行 {operation} 操作时出错: {str(e)}"
            }

    async def _read_file(self, path: Path) -> Dict[str, Any]:
        """读取文件内容"""
        if not path.exists():
            return {
                "success": False,
                "error": f"文件不存在: {path}"
            }

        if not path.is_file():
            return {
                "success": False,
                "error": f"不是文件: {path}"
            }

        if not self._check_extension(path):
            return {
                "success": False,
                "error": f"不支持的文件类型: {path.suffix}"
            }

        if not self._check_size(path):
            return {
                "success": False,
                "error": f"文件过大（超过{self.MAX_FILE_SIZE / 1024 / 1024}MB）"
            }

        try:
            async with aiofiles.open(path, 'r', encoding='utf-8') as f:
                content = await f.read()

            return {
                "success": True,
                "operation": "read",
                "path": str(path),
                "content": content,
                "size": path.stat().st_size,
                "lines": len(content.splitlines())
            }
        except UnicodeDecodeError:
            return {
                "success": False,
                "error": "文件编码错误，仅支持UTF-8编码"
            }

    async def _write_file(self, path: Path, content: str) -> Dict[str, Any]:
        """写入文件内容"""
        if not self._check_extension(path):
            return {
                "success": False,
                "error": f"不支持的文件类型: {path.suffix}"
            }

        # 检查内容大小
        content_size = len(content.encode('utf-8'))
        if content_size > self.MAX_FILE_SIZE:
            return {
                "success": False,
                "error": f"内容过大（超过{self.MAX_FILE_SIZE / 1024 / 1024}MB）"
            }

        # 确保父目录存在
        path.parent.mkdir(parents=True, exist_ok=True)

        try:
            async with aiofiles.open(path, 'w', encoding='utf-8') as f:
                await f.write(content)

            return {
                "success": True,
                "operation": "write",
                "path": str(path),
                "size": path.stat().st_size,
                "lines": len(content.splitlines()),
                "message": f"成功写入文件: {path.name}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"写入文件失败: {str(e)}"
            }

    async def _list_files(
        self, path: Path, recursive: bool = False
    ) -> Dict[str, Any]:
        """列出目录内容"""
        if not path.exists():
            return {
                "success": False,
                "error": f"路径不存在: {path}"
            }

        if not path.is_dir():
            return {
                "success": False,
                "error": f"不是目录: {path}"
            }

        try:
            files = []
            dirs = []

            if recursive:
                # 递归遍历
                for item in path.rglob("*"):
                    if item.is_file():
                        files.append({
                            "name": item.name,
                            "path": str(item.relative_to(path)),
                            "size": item.stat().st_size,
                            "extension": item.suffix
                        })
                    elif item.is_dir():
                        dirs.append({
                            "name": item.name,
                            "path": str(item.relative_to(path))
                        })
            else:
                # 仅列出当前目录
                for item in path.iterdir():
                    if item.is_file():
                        files.append({
                            "name": item.name,
                            "size": item.stat().st_size,
                            "extension": item.suffix
                        })
                    elif item.is_dir():
                        dirs.append({
                            "name": item.name
                        })

            return {
                "success": True,
                "operation": "list",
                "path": str(path),
                "files": files,
                "directories": dirs,
                "file_count": len(files),
                "dir_count": len(dirs)
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"列出目录失败: {str(e)}"
            }

    async def _search_files(
        self, path: Path, pattern: str, recursive: bool = False
    ) -> Dict[str, Any]:
        """搜索文件"""
        if not path.exists():
            return {
                "success": False,
                "error": f"路径不存在: {path}"
            }

        if not path.is_dir():
            return {
                "success": False,
                "error": f"不是目录: {path}"
            }

        try:
            # 构建搜索模式
            if recursive:
                search_pattern = str(path / "**" / pattern)
            else:
                search_pattern = str(path / pattern)

            # 执行搜索
            found_files = []
            for file_path in glob.glob(search_pattern, recursive=recursive):
                file_path = Path(file_path)
                if file_path.is_file():
                    # 计算相对路径
                    rel_path = (
                        str(file_path.relative_to(path))
                        if recursive else file_path.name
                    )
                    found_files.append({
                        "name": file_path.name,
                        "path": rel_path,
                        "size": file_path.stat().st_size,
                        "extension": file_path.suffix
                    })

                    # 限制结果数量
                    if len(found_files) >= self.MAX_SEARCH_RESULTS:
                        break

            return {
                "success": True,
                "operation": "search",
                "path": str(path),
                "pattern": pattern,
                "recursive": recursive,
                "results": found_files,
                "count": len(found_files),
                "truncated": len(found_files) >= self.MAX_SEARCH_RESULTS
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"搜索文件失败: {str(e)}"
            }


# 创建工具实例
file_tool = FileTool()
