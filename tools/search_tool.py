"""
网络搜索工具 (v0.6.0 优化版)
使用 DuckDuckGo 进行网络搜索
新增功能：错误重试、结果缓存、搜索历史
"""
from tool_manager import Tool, ToolParameter
from ddgs import DDGS
import asyncio
import time
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
        self.parameters = [
            ToolParameter(
                name="query",
                param_type="string",
                description="搜索关键词或问题",
                required=True
            ),
            ToolParameter(
                name="max_results",
                param_type="integer",
                description="最大返回结果数量，默认5条",
                required=False,
                default=5
            )
        ]

        # === v0.6.0 新增：结果缓存 ===
        self.cache = {}  # {query: (result, timestamp)}
        self.cache_ttl = 300  # 5分钟缓存

        # === v0.6.0 新增：搜索历史 ===
        self.search_history = []  # [(query, timestamp, success)]
        self.max_history = 50

        # === v0.6.0 新增：重试配置 ===
        self.max_retries = 3
        self.retry_delay = 1  # 秒

    async def execute(self, **kwargs) -> Dict:
        """
        执行搜索 (v0.6.0 优化版：带缓存和重试)

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

        # === v0.6.0 新增：检查缓存 ===
        cached_result = self._get_cached_result(query)
        if cached_result:
            print(f"✅ 使用缓存结果: {query}")
            return cached_result

        # === v0.6.0 新增：带重试的搜索 ===
        for attempt in range(self.max_retries):
            try:
                # 使用 DuckDuckGo 搜索
                results = await self._search_ddg(query, max_results)

                if not results:
                    result = {
                        "success": True,
                        "data": "未找到相关结果",
                        "results": [],
                        "count": 0
                    }
                else:
                    # 格式化结果
                    formatted_results = self._format_results(results)
                    result = {
                        "success": True,
                        "data": formatted_results,
                        "results": results,
                        "count": len(results)
                    }

                # === v0.6.0 新增：缓存结果 ===
                self._cache_result(query, result)

                # === v0.6.0 新增：记录历史 ===
                self._add_to_history(query, True)

                return result

            except Exception as e:
                error_msg = str(e)

                # 最后一次尝试失败
                if attempt == self.max_retries - 1:
                    print(f"❌ 搜索失败（已重试{self.max_retries}次）: {error_msg}")

                    # === v0.6.0 新增：记录失败历史 ===
                    self._add_to_history(query, False)

                    return {
                        "success": False,
                        "error": f"搜索失败（已重试{self.max_retries}次）: {error_msg}",
                        "suggestion": "请检查网络连接或稍后再试"
                    }

                # 还有重试机会
                retry_msg = (
                    f"⚠️  搜索失败，{self.retry_delay}秒后重试 "
                    f"({attempt + 1}/{self.max_retries}): {error_msg}"
                )
                print(retry_msg)
                await asyncio.sleep(self.retry_delay)

    def _get_cached_result(self, query: str) -> Dict:
        """
        获取缓存的搜索结果

        Args:
            query: 搜索关键词

        Returns:
            Dict: 缓存的结果，如果无效则返回None
        """
        if query in self.cache:
            result, timestamp = self.cache[query]
            # 检查是否过期
            if time.time() - timestamp < self.cache_ttl:
                return result
            else:
                # 清除过期缓存
                del self.cache[query]
        return None

    def _cache_result(self, query: str, result: Dict):
        """
        缓存搜索结果

        Args:
            query: 搜索关键词
            result: 搜索结果
        """
        self.cache[query] = (result, time.time())

        # 限制缓存大小（最多100条）
        if len(self.cache) > 100:
            # 删除最旧的缓存
            oldest_query = min(
                self.cache.keys(),
                key=lambda k: self.cache[k][1]
            )
            del self.cache[oldest_query]

    def _add_to_history(self, query: str, success: bool):
        """
        添加搜索历史

        Args:
            query: 搜索关键词
            success: 是否成功
        """
        self.search_history.append({
            'query': query,
            'timestamp': time.time(),
            'success': success
        })

        # 限制历史记录数量
        if len(self.search_history) > self.max_history:
            self.search_history.pop(0)

    def get_search_stats(self) -> Dict:
        """
        获取搜索统计信息

        Returns:
            Dict: 统计信息
        """
        total = len(self.search_history)
        if total == 0:
            return {
                'total_searches': 0,
                'success_rate': 0,
                'cache_size': len(self.cache)
            }

        success_count = sum(
            1 for h in self.search_history if h['success']
        )

        return {
            'total_searches': total,
            'successful': success_count,
            'failed': total - success_count,
            'success_rate': f"{success_count / total * 100:.1f}%",
            'cache_size': len(self.cache),
            'recent_searches': [
                h['query'] for h in self.search_history[-5:]
            ]
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
