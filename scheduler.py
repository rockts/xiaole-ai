"""
定时任务调度器 - v0.5.0
功能：
1. 定期检查提醒触发条件
2. 后台任务队列
3. 任务执行历史
"""
import asyncio
import logging
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger

from reminder_manager import get_reminder_manager
from proactive_chat import get_proactive_chat

logger = logging.getLogger(__name__)


class ReminderScheduler:
    """
    提醒调度器
    功能：
    1. 定期检查时间提醒（每分钟）
    2. 定期检查行为提醒（每5分钟）
    3. 支持手动触发检查
    """

    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.reminder_manager = get_reminder_manager()
        self.proactive_chat = get_proactive_chat()
        self.is_running = False

    def start(self):
        """启动调度器"""
        if self.is_running:
            logger.warning("Scheduler is already running")
            return

        # 任务1: 每分钟检查时间提醒
        self.scheduler.add_job(
            self.check_time_reminders,
            trigger=IntervalTrigger(minutes=1),
            id='check_time_reminders',
            name='检查时间提醒',
            replace_existing=True
        )

        # 任务2: 每5分钟检查行为提醒
        self.scheduler.add_job(
            self.check_behavior_reminders,
            trigger=IntervalTrigger(minutes=5),
            id='check_behavior_reminders',
            name='检查行为提醒',
            replace_existing=True
        )

        # 任务3: 每天凌晨3点清理过期提醒
        self.scheduler.add_job(
            self.cleanup_expired_reminders,
            trigger=CronTrigger(hour=3, minute=0),
            id='cleanup_expired',
            name='清理过期提醒',
            replace_existing=True
        )

        # 任务4: 每小时检查是否需要主动对话
        self.scheduler.add_job(
            self.check_proactive_chat,
            trigger=IntervalTrigger(hours=1),
            id='check_proactive_chat',
            name='检查主动对话',
            replace_existing=True
        )

        self.scheduler.start()
        self.is_running = True
        logger.info("Reminder scheduler started")

    def stop(self):
        """停止调度器"""
        if not self.is_running:
            return

        self.scheduler.shutdown()
        self.is_running = False
        logger.info("Reminder scheduler stopped")

    async def check_time_reminders(self):
        """检查所有用户的时间提醒"""
        try:
            logger.info("Checking time reminders...")

            # TODO: 获取所有活跃用户列表
            # 目前先检查默认用户
            users = ["default_user"]

            total_triggered = 0
            for user_id in users:
                triggered = await self.reminder_manager.check_time_reminders(
                    user_id
                )

                for reminder in triggered:
                    success = await self.reminder_manager.trigger_reminder(
                        reminder['reminder_id']
                    )
                    if success:
                        total_triggered += 1
                        logger.info(
                            f"Triggered time reminder: "
                            f"{reminder.get('title', 'Untitled')} "
                            f"for user {user_id}"
                        )

            if total_triggered > 0:
                logger.info(
                    f"Time reminder check complete: "
                    f"{total_triggered} reminders triggered"
                )

        except Exception as e:
            logger.error(f"Error checking time reminders: {e}")

    async def check_behavior_reminders(self):
        """检查所有用户的行为提醒"""
        try:
            logger.info("Checking behavior reminders...")

            # TODO: 获取所有活跃用户列表
            users = ["default_user"]

            total_triggered = 0
            for user_id in users:
                triggered = await self.reminder_manager.check_behavior_reminders(
                    user_id
                )

                for reminder in triggered:
                    success = await self.reminder_manager.trigger_reminder(
                        reminder['reminder_id']
                    )
                    if success:
                        total_triggered += 1
                        logger.info(
                            f"Triggered behavior reminder: "
                            f"{reminder.get('title', 'Untitled')} "
                            f"for user {user_id}"
                        )

            if total_triggered > 0:
                logger.info(
                    f"Behavior reminder check complete: "
                    f"{total_triggered} reminders triggered"
                )

        except Exception as e:
            logger.error(f"Error checking behavior reminders: {e}")

    async def cleanup_expired_reminders(self):
        """清理过期的非重复提醒"""
        try:
            logger.info("Cleaning up expired reminders...")

            # TODO: 实现清理逻辑
            # 删除已触发且非重复的提醒（保留最近30天）

            logger.info("Cleanup complete")

        except Exception as e:
            logger.error(f"Error cleaning up reminders: {e}")

    async def check_proactive_chat(self):
        """检查是否需要发起主动对话"""
        try:
            logger.info("Checking proactive chat conditions...")

            # TODO: 获取所有活跃用户列表
            users = ["default_user"]

            for user_id in users:
                result = self.proactive_chat.should_initiate_chat(user_id)
                
                if result["should_chat"]:
                    logger.info(
                        f"Proactive chat triggered for {user_id}: "
                        f"{result['reason']} (priority: {result['priority']})"
                    )
                    
                    # 通过WebSocket推送主动对话
                    if self.reminder_manager.websocket_callback:
                        await self.reminder_manager.websocket_callback({
                            "type": "proactive_chat",
                            "user_id": user_id,
                            "reason": result["reason"],
                            "message": result["message"],
                            "priority": result["priority"],
                            "metadata": result.get("metadata", {})
                        })
                        
                        # 标记已发起
                        self.proactive_chat.mark_chat_initiated(
                            user_id,
                            result["reason"],
                            result["message"]
                        )
                        
                        logger.info(f"Proactive chat sent to {user_id}")

        except Exception as e:
            logger.error(f"Error checking proactive chat: {e}")

    def get_jobs(self):
        """获取所有任务信息"""
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                "id": job.id,
                "name": job.name,
                "next_run_time": job.next_run_time.isoformat()
                if job.next_run_time else None,
                "trigger": str(job.trigger)
            })
        return jobs

    def get_status(self):
        """获取调度器状态"""
        return {
            "running": self.is_running,
            "total_jobs": len(self.scheduler.get_jobs()),
            "jobs": self.get_jobs()
        }


# 全局单例
_scheduler = None


def get_scheduler() -> ReminderScheduler:
    """获取调度器单例"""
    global _scheduler
    if _scheduler is None:
        _scheduler = ReminderScheduler()
    return _scheduler
