"""
网络搜索工具
使用 DuckDuckGo 进行网络搜索
"""
from tool_manager import Tool
from duckduckgo_search import DDGS
import asyncio
from typing import List, Dict


class SearchTool(Tool):
    """网络搜索工具"""

    def __init__(self):
        super().__init__()
        self.name = "search"
        self.description = (
            "在互联网上搜索信息。"
            "适用场景：查询实时信息、新闻、百科知识等。"
            "返回搜索结果的标题、摘要和链接。"
        )
        self.parameters = {
            "query": {
                "type": "string",
                "description": "搜索关键词或问题",
                "required": True
            },
            "max_results": {
                "type": "integer",
                "description": "最大返回结果数量，默认5条",
                "required": False,
                "default": 5
            }
        }

    async def execute(self, **kwargs) -> Dict:
        """
        执行搜索

        Args:
            query: 搜索关键词
            max_results: 最大结果数，默认5

        Returns:
            Dict: 包含搜索结果的字典
        """
        query = kwargs.get("query")
        max_results = kwargs.get("max_results", 5)

        if not query:
            return {
                "success": False,
                "error": "搜索关键词不能为空"
            }

        try:
            # 使用 DuckDuckGo 搜索
            results = await self._search_ddg(query, max_results)

            if not results:
                return {
                    "success": True,
                    "data": "未找到相关结果",
                    "results": [],
                    "count": 0
                }

            # 格式化结果
            formatted_results = self._format_results(results)

            return {
                "success": True,
                "data": formatted_results,
                "results": results,
                "count": len(results)
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"搜索失败: {str(e)}"
            }

    async def _search_ddg(
        self,
        query: str,
        max_results: int = 5
    ) -> List[Dict]:
        """
        使用 DuckDuckGo 搜索

        Args:
            query: 搜索关键词
            max_results: 最大结果数

        Returns:
            List[Dict]: 搜索结果列表
        """
        try:
            # 在线程池中执行同步的搜索操作
            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(
                None,
                self._do_search,
                query,
                max_results
            )
            return results
        except Exception as e:
            print(f"搜索出错: {e}")
            return []

    def _do_search(self, query: str, max_results: int) -> List[Dict]:
        """
        执行实际的搜索（同步方法）

        Args:
            query: 搜索关键词
            max_results: 最大结果数

        Returns:
            List[Dict]: 搜索结果
        """
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(
                    query,
                    max_results=max_results
                ))
                return results
        except Exception as e:
            print(f"DuckDuckGo 搜索失败: {e}")
            return []

    def _format_results(self, results: List[Dict]) -> str:
        """
        格式化搜索结果为可读文本

        Args:
            results: 搜索结果列表

        Returns:
            str: 格式化后的文本
        """
        if not results:
            return "未找到相关结果"

        formatted = f"找到 {len(results)} 条相关结果：\n\n"

        for i, result in enumerate(results, 1):
            title = result.get('title', '无标题')
            body = result.get('body', '无摘要')
            href = result.get('href', '无链接')

            formatted += f"{i}. **{title}**\n"
            formatted += f"   {body}\n"
            formatted += f"   🔗 {href}\n\n"

        return formatted.strip()


# 创建搜索工具实例
search_tool = SearchTool()
