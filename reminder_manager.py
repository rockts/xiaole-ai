"""
主动提醒系统
支持时间、天气、行为、习惯等多种触发类型
"""
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import json
import logging

import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

load_dotenv()


def get_db_connection():
    """获取数据库连接"""
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST', '192.168.88.188'),
        port=os.getenv('DB_PORT', '5432'),
        database=os.getenv('DB_NAME', 'xiaole_ai'),
        user=os.getenv('DB_USER', 'xiaole_user'),
        password=os.getenv('DB_PASS', 'Xiaole2025User'),
        client_encoding='UTF8'
    )
    return conn


logger = logging.getLogger(__name__)


class ReminderType:
    """提醒类型常量"""
    TIME = "time"           # 时间提醒（生日、纪念日、定时任务）
    WEATHER = "weather"     # 天气提醒（下雨带伞、温度变化）
    BEHAVIOR = "behavior"   # 行为提醒（长时间未聊天）
    HABIT = "habit"         # 习惯提醒（基于行为模式）


class ReminderStatus:
    """提醒状态"""
    ENABLED = "enabled"
    DISABLED = "disabled"
    TRIGGERED = "triggered"
    EXPIRED = "expired"


class ReminderManager:
    """
    主动提醒管理器
    功能：
    1. 创建、查询、更新、删除提醒
    2. 检查触发条件
    3. 发送提醒通知
    4. 记录提醒历史
    """

    def __init__(self, websocket_broadcast_callback=None):
        self.reminders_cache: Dict[str, List[Dict]] = {}  # 用户提醒缓存
        self.last_cache_update = None
        self.cache_ttl = 300  # 缓存5分钟
        self.websocket_broadcast = websocket_broadcast_callback  # WebSocket推送回调

    async def create_reminder(
        self,
        user_id: str,
        reminder_type: str,
        trigger_condition: Dict[str, Any],
        content: str,
        title: Optional[str] = None,
        priority: int = 1,
        repeat: bool = False,
        repeat_interval: Optional[int] = None  # 秒
    ) -> Dict[str, Any]:
        """
        创建提醒

        Args:
            user_id: 用户ID
            reminder_type: 提醒类型（time/weather/behavior/habit）
            trigger_condition: 触发条件JSON
                time类型: {"datetime": "2025-12-25 10:00:00"}
                weather类型: {"condition": "rain", "location": "天水"}
                behavior类型: {"inactive_hours": 24}
                habit类型: {"pattern": "morning_greeting", "time": "08:00"}
            content: 提醒内容
            title: 提醒标题
            priority: 优先级（1-5，1最高）
            repeat: 是否重复
            repeat_interval: 重复间隔（秒）

        Returns:
            创建的提醒信息
        """
        conn = get_db_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    INSERT INTO reminders (
                        user_id, reminder_type, trigger_condition,
                        content, title, priority, repeat, repeat_interval,
                        enabled, created_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
                    RETURNING reminder_id, user_id, reminder_type, trigger_condition,
                              content, title, priority, repeat, repeat_interval,
                              enabled, created_at
                """, (
                    user_id, reminder_type, json.dumps(trigger_condition),
                    content, title, priority, repeat, repeat_interval, True
                ))
                reminder = dict(cur.fetchone())
                conn.commit()

                # 清除缓存
                self._clear_user_cache(user_id)

                logger.info(
                    f"Created reminder {reminder['reminder_id']} for user {user_id}")
                return reminder

        except Exception as e:
            conn.rollback()
            logger.error(f"Failed to create reminder: {e}")
            raise
        finally:
            conn.close()

    async def get_user_reminders(
        self,
        user_id: str,
        enabled_only: bool = True,
        reminder_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        获取用户的提醒列表

        Args:
            user_id: 用户ID
            enabled_only: 是否只返回启用的提醒
            reminder_type: 提醒类型过滤

        Returns:
            提醒列表
        """
        # 检查缓存
        cache_key = f"{user_id}_{enabled_only}_{reminder_type}"
        if self._is_cache_valid() and cache_key in self.reminders_cache:
            return self.reminders_cache[cache_key]

        conn = get_db_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                query = "SELECT * FROM reminders WHERE user_id = %s"
                params = [user_id]

                if enabled_only:
                    query += " AND enabled = true"

                if reminder_type:
                    query += " AND reminder_type = %s"
                    params.append(reminder_type)

                query += " ORDER BY priority ASC, created_at DESC"

                cur.execute(query, params)
                reminders = [dict(row) for row in cur.fetchall()]

                # 更新缓存
                self.reminders_cache[cache_key] = reminders
                self.last_cache_update = datetime.now()

                return reminders

        except Exception as e:
            logger.error(f"Failed to get user reminders: {e}")
            return []
        finally:
            conn.close()

    async def update_reminder(
        self,
        reminder_id: int,
        **updates
    ) -> bool:
        """
        更新提醒

        Args:
            reminder_id: 提醒ID
            **updates: 要更新的字段

        Returns:
            是否成功
        """
        if not updates:
            return False

        # 构建更新SQL
        set_clause = ", ".join([f"{k} = %s" for k in updates.keys()])
        values = list(updates.values())
        values.append(reminder_id)

        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(f"""
                    UPDATE reminders
                    SET {set_clause}, updated_at = CURRENT_TIMESTAMP
                    WHERE reminder_id = %s
                """, values)
                conn.commit()

                # 清除所有缓存
                self.reminders_cache.clear()

                logger.info(f"Updated reminder {reminder_id}")
                return True

        except Exception as e:
            conn.rollback()
            logger.error(f"Failed to update reminder: {e}")
            return False
        finally:
            conn.close()

    async def delete_reminder(self, reminder_id: int) -> bool:
        """删除提醒"""
        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM reminders WHERE reminder_id = %s", (reminder_id,))
                conn.commit()

                # 清除缓存
                self.reminders_cache.clear()

                logger.info(f"Deleted reminder {reminder_id}")
                return True

        except Exception as e:
            conn.rollback()
            logger.error(f"Failed to delete reminder: {e}")
            return False
        finally:
            conn.close()

    async def check_time_reminders(self, user_id: str) -> List[Dict[str, Any]]:
        """
        检查时间类型的提醒

        Returns:
            需要触发的提醒列表
        """
        reminders = await self.get_user_reminders(
            user_id,
            enabled_only=True,
            reminder_type=ReminderType.TIME
        )

        triggered = []
        now = datetime.now()

        for reminder in reminders:
            try:
                condition = reminder['trigger_condition']
                if isinstance(condition, str):
                    condition = json.loads(condition)

                # 解析触发时间
                trigger_time_str = condition.get('datetime')
                if not trigger_time_str:
                    continue

                trigger_time = datetime.fromisoformat(trigger_time_str)

                # 检查是否到时间
                if now >= trigger_time:
                    # 检查是否最近已触发（避免重复）
                    last_triggered = reminder.get('last_triggered')
                    if last_triggered:
                        # 如果是重复提醒，检查间隔
                        if reminder.get('repeat'):
                            interval = reminder.get(
                                'repeat_interval', 86400)  # 默认1天
                            if (now - last_triggered).total_seconds() < interval:
                                continue
                        else:
                            # 非重复提醒已触发过，跳过
                            continue

                    triggered.append(reminder)

            except Exception as e:
                logger.error(
                    f"Failed to check time reminder {reminder['reminder_id']}: {e}")

        return triggered

    async def check_behavior_reminders(self, user_id: str) -> List[Dict[str, Any]]:
        """
        检查行为类型的提醒（如长时间未聊天）

        Returns:
            需要触发的提醒列表
        """
        reminders = await self.get_user_reminders(
            user_id,
            enabled_only=True,
            reminder_type=ReminderType.BEHAVIOR
        )

        triggered = []

        # 获取用户最后活跃时间
        last_active = await self._get_user_last_active(user_id)
        if not last_active:
            return triggered

        now = datetime.now()
        inactive_hours = (now - last_active).total_seconds() / 3600

        for reminder in reminders:
            try:
                condition = reminder['trigger_condition']
                if isinstance(condition, str):
                    condition = json.loads(condition)

                # 检查不活跃时间
                required_hours = condition.get('inactive_hours', 24)
                if inactive_hours >= required_hours:
                    # 检查是否最近已触发
                    last_triggered = reminder.get('last_triggered')
                    if last_triggered:
                        hours_since_last = (
                            now - last_triggered).total_seconds() / 3600
                        if hours_since_last < required_hours:
                            continue

                    triggered.append(reminder)

            except Exception as e:
                logger.error(
                    f"Failed to check behavior reminder {reminder['reminder_id']}: {e}")

        return triggered

    async def check_and_notify_reminder(self, reminder_id: int) -> bool:
        """
        检查提醒并通过WebSocket推送通知（不写入历史）
        
        Args:
            reminder_id: 提醒ID
            
        Returns:
            是否成功推送
        """
        conn = get_db_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # 获取提醒信息
                cur.execute("""
                    SELECT * FROM reminders WHERE reminder_id = %s
                """, (reminder_id,))
                reminder = cur.fetchone()
                
                if not reminder:
                    logger.error(f"Reminder {reminder_id} not found")
                    return False
                
                reminder = dict(reminder)

                # 更新last_triggered（标记为已通知但未确认）
                cur.execute("""
                    UPDATE reminders
                    SET last_triggered = CURRENT_TIMESTAMP,
                        trigger_count = COALESCE(trigger_count, 0) + 1
                    WHERE reminder_id = %s
                """, (reminder_id,))
                
                conn.commit()

                logger.info(
                    f"Notified reminder {reminder_id} (not confirmed yet)"
                )

                # WebSocket实时推送提醒（用户需要确认）
                if self.websocket_broadcast:
                    try:
                        await self.websocket_broadcast({
                            "type": "reminder",
                            "data": {
                                "reminder_id": reminder_id,
                                "title": reminder.get('title', '提醒'),
                                "content": reminder['content'],
                                "priority": reminder.get('priority', 3),
                                "reminder_type": reminder.get('reminder_type'),
                                "triggered_at": datetime.now().isoformat()
                            }
                        })
                        logger.info(f"WebSocket推送提醒 {reminder_id}")
                        return True
                    except Exception as ws_error:
                        logger.error(f"WebSocket推送失败: {ws_error}")
                        return False
                else:
                    logger.warning("No WebSocket broadcast callback available")
                    return False

        except Exception as e:
            conn.rollback()
            logger.error(f"Failed to notify reminder: {e}")
            return False
        finally:
            conn.close()

    async def confirm_reminder(self, reminder_id: int) -> bool:
        """
        用户确认提醒（点击"已知道"），记录历史并禁用
        
        Args:
            reminder_id: 提醒ID
            
        Returns:
            是否成功
        """
        conn = get_db_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # 获取提醒信息
                cur.execute("""
                    SELECT * FROM reminders WHERE reminder_id = %s
                """, (reminder_id,))
                reminder = cur.fetchone()
                
                if not reminder:
                    logger.error(f"Reminder {reminder_id} not found")
                    return False
                
                reminder = dict(reminder)

                # 记录提醒历史（用户已确认）
                cur.execute("""
                    INSERT INTO reminder_history (
                        reminder_id, user_id, content, triggered_at
                    ) VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
                """, (
                    reminder_id,
                    reminder['user_id'],
                    reminder['content']
                ))

                # 如果是非重复提醒，禁用它
                if not reminder.get('repeat'):
                    cur.execute("""
                        UPDATE reminders
                        SET enabled = false
                        WHERE reminder_id = %s
                    """, (reminder_id,))

                conn.commit()

                logger.info(
                    f"Confirmed reminder {reminder_id} (written to history)"
                )
                return True

        except Exception as e:
            conn.rollback()
            logger.error(f"Failed to confirm reminder: {e}")
            return False
        finally:
            conn.close()

    async def get_reminder_history(
        self,
        user_id: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """获取提醒历史"""
        conn = get_db_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT h.*, r.title, r.reminder_type
                    FROM reminder_history h
                    LEFT JOIN reminders r ON h.reminder_id = r.reminder_id
                    WHERE h.user_id = %s
                    ORDER BY h.triggered_at DESC
                    LIMIT %s
                """, (user_id, limit))
                return [dict(row) for row in cur.fetchall()]

        except Exception as e:
            logger.error(f"Failed to get reminder history: {e}")
            return []
        finally:
            conn.close()

    async def get_pending_reminders(self, user_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        获取用户未读的提醒（最近触发但未确认的）

        Args:
            user_id: 用户ID
            limit: 返回数量限制

        Returns:
            未读提醒列表
        """
        conn = get_db_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # 获取最近5分钟内触发的提醒
                cur.execute("""
                    SELECT h.*, r.title, r.reminder_type, r.priority
                    FROM reminder_history h
                    LEFT JOIN reminders r ON h.reminder_id = r.reminder_id
                    WHERE h.user_id = %s
                    AND h.triggered_at > NOW() - INTERVAL '5 minutes'
                    ORDER BY r.priority ASC, h.triggered_at DESC
                    LIMIT %s
                """, (user_id, limit))
                return [dict(row) for row in cur.fetchall()]

        except Exception as e:
            logger.error(f"Failed to get pending reminders: {e}")
            return []
        finally:
            conn.close()

    def _clear_user_cache(self, user_id: str):
        """清除用户相关的缓存"""
        keys_to_remove = [
            k for k in self.reminders_cache.keys() if k.startswith(user_id)]
        for key in keys_to_remove:
            self.reminders_cache.pop(key, None)

    def _is_cache_valid(self) -> bool:
        """检查缓存是否有效"""
        if not self.last_cache_update:
            return False
        return (datetime.now() - self.last_cache_update).total_seconds() < self.cache_ttl

    async def _get_user_last_active(self, user_id: str) -> Optional[datetime]:
        """获取用户最后活跃时间"""
        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT MAX(created_at) as last_active
                    FROM conversation_history
                    WHERE user_id = %s
                """, (user_id,))
                result = cur.fetchone()
                return result[0] if result and result[0] else None

        except Exception as e:
            logger.error(f"Failed to get user last active: {e}")
            return None
        finally:
            conn.close()


# 全局单例
_reminder_manager = None


def get_reminder_manager(
    websocket_broadcast_callback=None
) -> ReminderManager:
    """获取提醒管理器单例"""
    global _reminder_manager
    if _reminder_manager is None:
        _reminder_manager = ReminderManager(websocket_broadcast_callback)
    elif websocket_broadcast_callback is not None:
        # 更新WebSocket回调
        _reminder_manager.websocket_broadcast = websocket_broadcast_callback
    return _reminder_manager
