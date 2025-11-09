"""
提醒工具 - v0.5.0
支持智能创建时间提醒
"""
from datetime import datetime, timedelta
import re
from tool_manager import Tool, ToolParameter


class ReminderTool(Tool):
    """提醒工具 - 创建时间提醒"""
    
    def __init__(self):
        super().__init__()
        self.name = "reminder"
        self.description = "创建时间提醒（支持：明天/后天/X小时后/X分钟后/具体时间）"
        self.category = "reminder"
        self.enabled = True
        self.parameters = [
            ToolParameter(
                name="content",
                param_type="string",
                description="提醒内容",
                required=True
            ),
            ToolParameter(
                name="time_desc",
                param_type="string",
                description="时间描述（如：明天下午3点、2小时后、后天早上9点）",
                required=True
            ),
            ToolParameter(
                name="title",
                param_type="string",
                description="提醒标题（可选）",
                required=False
            )
        ]
    
    async def execute(self, **kwargs) -> dict:
        """
        执行提醒创建
        
        Args:
            **kwargs: 包含 content, time_desc, title(可选), user_id, session_id
        
        Returns:
            {"success": bool, "data": str, "reminder_id": int}
        """
        try:
            content = kwargs.get("content", "")
            time_desc = kwargs.get("time_desc", "")
            title = kwargs.get("title") or self._extract_title(content)
            user_id = kwargs.get("user_id", "default_user")
            
            if not content or not time_desc:
                return {
                    "success": False,
                    "data": "❌ 提醒内容和时间不能为空"
                }
            
            # 解析时间描述，转换为具体时间
            trigger_time = self._parse_time(time_desc)
            
            if not trigger_time:
                return {
                    "success": False,
                    "data": f"❌ 无法识别时间：{time_desc}\n支持格式：明天/后天/X小时后/X分钟后/具体时间"
                }
            
            # 创建提醒
            from reminder_manager import get_reminder_manager
            reminder_mgr = get_reminder_manager()
            
            reminder = await reminder_mgr.create_reminder(
                user_id=user_id,
                reminder_type="time",
                trigger_condition={"datetime": trigger_time.strftime("%Y-%m-%d %H:%M:%S")},
                content=content,
                title=title,
                priority=2,  # 对话创建的提醒默认中等优先级
                repeat=False
            )
            
            # 格式化时间显示
            time_str = self._format_time_display(trigger_time)
            
            return {
                "success": True,
                "data": f"✅ 提醒已创建：{title}\n⏰ 触发时间：{time_str}\n📝 内容：{content}",
                "reminder_id": reminder['reminder_id']
            }
            
        except Exception as e:
            import logging
            logging.error(f"创建提醒失败: {e}")
            return {
                "success": False,
                "data": f"❌ 创建提醒失败: {str(e)}"
            }
    
    def _extract_title(self, content: str) -> str:
        """从内容中提取标题（前20个字）"""
        title = content[:20]
        if len(content) > 20:
            title += "..."
        return title
    
    def _parse_time(self, time_desc: str) -> datetime:
        """
        解析时间描述，返回具体时间
        
        支持格式：
        - 明天/后天 + 时间（如：明天下午3点、后天早上9点）
        - X小时后/X分钟后
        - 具体时间（如：2025-11-11 15:00）
        """
        now = datetime.now()
        time_desc = time_desc.strip()
        
        # 1. 处理"X小时后"
        match = re.search(r'(\d+)\s*小时后', time_desc)
        if match:
            hours = int(match.group(1))
            return now + timedelta(hours=hours)
        
        # 2. 处理"X分钟后"
        match = re.search(r'(\d+)\s*分钟后', time_desc)
        if match:
            minutes = int(match.group(1))
            return now + timedelta(minutes=minutes)
        
        # 3. 处理"明天"
        if '明天' in time_desc or '明日' in time_desc:
            target_date = now + timedelta(days=1)
            time_part = self._extract_time_part(time_desc)
            if time_part:
                return target_date.replace(
                    hour=time_part['hour'],
                    minute=time_part.get('minute', 0),
                    second=0,
                    microsecond=0
                )
            else:
                # 默认明天上午9点
                return target_date.replace(hour=9, minute=0, second=0, microsecond=0)
        
        # 4. 处理"后天"
        if '后天' in time_desc:
            target_date = now + timedelta(days=2)
            time_part = self._extract_time_part(time_desc)
            if time_part:
                return target_date.replace(
                    hour=time_part['hour'],
                    minute=time_part.get('minute', 0),
                    second=0,
                    microsecond=0
                )
            else:
                return target_date.replace(hour=9, minute=0, second=0, microsecond=0)
        
        # 5. 处理"今天"
        if '今天' in time_desc or '今日' in time_desc:
            time_part = self._extract_time_part(time_desc)
            if time_part:
                return now.replace(
                    hour=time_part['hour'],
                    minute=time_part.get('minute', 0),
                    second=0,
                    microsecond=0
                )
        
        # 6. 处理具体时间格式：YYYY-MM-DD HH:MM
        try:
            return datetime.strptime(time_desc, "%Y-%m-%d %H:%M")
        except:
            pass
        
        # 7. 处理相对时间（如：下午3点、晚上8点）
        time_part = self._extract_time_part(time_desc)
        if time_part:
            target = now.replace(
                hour=time_part['hour'],
                minute=time_part.get('minute', 0),
                second=0,
                microsecond=0
            )
            # 如果时间已过，设置为明天
            if target <= now:
                target += timedelta(days=1)
            return target
        
        return None
    
    def _extract_time_part(self, text: str) -> dict:
        """
        从文本中提取时间部分
        返回: {"hour": int, "minute": int} 或 None
        """
        # 匹配 "下午3点"、"晚上8点"、"早上9点"
        match = re.search(r'(早上|上午|中午|下午|晚上|凌晨)?(\d{1,2})点(\d{1,2}分)?', text)
        if match:
            period = match.group(1) or ""
            hour = int(match.group(2))
            minute_str = match.group(3)
            minute = int(minute_str[:-1]) if minute_str else 0
            
            # 调整小时（12小时制转24小时制）
            if period in ['下午', '晚上'] and hour < 12:
                hour += 12
            elif period == '凌晨' and hour == 12:
                hour = 0
            
            return {"hour": hour, "minute": minute}
        
        # 匹配 "15:30"、"3:00"
        match = re.search(r'(\d{1,2}):(\d{2})', text)
        if match:
            return {
                "hour": int(match.group(1)),
                "minute": int(match.group(2))
            }
        
        return None
    
    def _format_time_display(self, dt: datetime) -> str:
        """格式化时间显示"""
        now = datetime.now()
        delta = dt - now
        
        if delta.days == 0:
            if delta.seconds < 3600:
                minutes = delta.seconds // 60
                return f"今天 {dt.strftime('%H:%M')} ({minutes}分钟后)"
            else:
                hours = delta.seconds // 3600
                return f"今天 {dt.strftime('%H:%M')} ({hours}小时后)"
        elif delta.days == 1:
            return f"明天 {dt.strftime('%H:%M')}"
        elif delta.days == 2:
            return f"后天 {dt.strftime('%H:%M')}"
        else:
            return dt.strftime("%Y-%m-%d %H:%M")
