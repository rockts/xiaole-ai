"""
任务管理工具
支持查询和删除任务
"""
from tool_manager import Tool, ToolParameter
import logging

logger = logging.getLogger(__name__)


class TaskTool(Tool):
    """任务管理工具 - 查询、删除任务"""

    def __init__(self):
        super().__init__()
        self.name = "task"
        self.description = "任务管理工具（查询、删除）"
        self.category = "task"
        self.enabled = True
        self.parameters = [
            ToolParameter(
                name="operation",
                param_type="string",
                description="操作类型：list(查询), delete(删除)",
                required=True,
                default="list",
                enum=["list", "delete"]
            ),
            ToolParameter(
                name="task_id",
                param_type="number",
                description="任务ID（删除时必填）",
                required=False
            ),
            ToolParameter(
                name="status",
                param_type="string",
                description="状态过滤（查询时可选）：pending, in_progress, completed, failed",
                required=False,
                enum=["pending", "in_progress", "completed", "failed"]
            )
        ]

    async def execute(self, **kwargs) -> dict:
        """
        执行任务操作

        Args:
            **kwargs: 包含 operation, task_id, status, user_id
        """
        try:
            operation = kwargs.get("operation", "list")
            user_id = kwargs.get("user_id", "default_user")

            # 延迟导入避免循环依赖
            from task_manager import get_task_manager
            task_mgr = get_task_manager()

            if operation == "list":
                return await self._handle_list(task_mgr, user_id, kwargs)
            elif operation == "delete":
                return await self._handle_delete(task_mgr, kwargs)
            else:
                return {
                    "success": False,
                    "data": f"❌ 不支持的操作类型: {operation}"
                }

        except Exception as e:
            logger.error(f"任务操作失败: {e}")
            return {
                "success": False,
                "data": f"❌ 操作失败: {str(e)}"
            }

    async def _handle_list(self, mgr, user_id: str, kwargs) -> dict:
        """处理查询请求"""
        status = kwargs.get("status")
        tasks = mgr.get_tasks_by_user(user_id, status=status, limit=10)

        if not tasks:
            status_text = f"({status})" if status else ""
            return {
                "success": True,
                "data": f"📭 你目前没有任务{status_text}。"
            }

        # 格式化任务列表
        lines = ["📋 **当前的列表**："]
        for t in tasks:
            status_emoji = {
                'pending': '⏳',
                'in_progress': '▶️',
                'completed': '✅',
                'failed': '❌',
                'waiting': '⏸️'
            }.get(t['status'], '❓')

            lines.append(
                f"- ID:{t['id']} | {status_emoji} {t['status']} | {t['title']}"
            )

        return {
            "success": True,
            "data": "\n".join(lines)
        }

    async def _handle_delete(self, mgr, kwargs) -> dict:
        """处理删除请求"""
        task_id = kwargs.get("task_id")
        if not task_id:
            return {"success": False, "data": "❌ 删除任务需要提供 task_id"}

        success = mgr.delete_task(int(task_id))

        if success:
            return {"success": True, "data": f"✅ 任务已删除 (ID: {task_id})"}
        else:
            return {
                "success": False,
                "data": f"❌ 删除失败，未找到任务 ID: {task_id}"
            }
