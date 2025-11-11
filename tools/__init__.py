"""
小乐AI工具模块

包含各种外部服务和系统操作工具
"""
from .weather_tool import weather_tool
from .system_tool import system_info_tool, time_tool, calculator_tool
from .reminder_tool import ReminderTool
from .search_tool import search_tool
from .file_tool import file_tool

# 创建提醒工具实例
reminder_tool = ReminderTool()

# 导出所有工具
__all__ = [
    'weather_tool',
    'system_info_tool',
    'time_tool',
    'calculator_tool',
    'reminder_tool',
    'search_tool',
    'file_tool'
]
