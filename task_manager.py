"""
任务管理器模块 - v0.8.0
负责任务的创建、查询、更新、删除和执行管理
"""
import logging
import json
from datetime import datetime
from typing import Optional, List, Dict, Any
import psycopg2
from psycopg2.extras import RealDictCursor

logger = logging.getLogger(__name__)


class TaskManager:
    """任务管理器类"""

    def __init__(self, db_config: dict):
        """
        初始化任务管理器

        Args:
            db_config: 数据库配置字典
        """
        self.db_config = db_config
        logger.info("✅ 任务管理器初始化完成")

    def _get_connection(self):
        """获取数据库连接"""
        conn = psycopg2.connect(**self.db_config, client_encoding='utf8')
        return conn

    # ==================== 任务 CRUD ====================

    def create_task(
        self,
        user_id: str,
        session_id: str,
        title: str,
        description: str = None,
        parent_id: int = None,
        priority: int = 0
    ) -> Optional[int]:
        """
        创建新任务

        Args:
            user_id: 用户ID
            session_id: 会话ID
            title: 任务标题
            description: 任务描述
            parent_id: 父任务ID（用于子任务）
            priority: 优先级 (0-正常, 1-高, 2-紧急)

        Returns:
            任务ID，失败返回None
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO tasks (
                    user_id, session_id, title, description, 
                    parent_id, priority, status
                )
                VALUES (%s, %s, %s, %s, %s, %s, 'pending')
                RETURNING id
            """, (user_id, session_id, title, description, parent_id, priority))

            task_id = cursor.fetchone()[0]
            conn.commit()
            cursor.close()
            conn.close()

            logger.info(f"📝 创建任务成功: ID={task_id}, 标题={title}")
            return task_id

        except Exception as e:
            logger.error(f"❌ 创建任务失败: {e}")
            return None

    def get_task(self, task_id: int) -> Optional[Dict[str, Any]]:
        """
        获取任务详情

        Args:
            task_id: 任务ID

        Returns:
            任务信息字典，失败返回None
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            cursor.execute("""
                SELECT * FROM tasks WHERE id = %s
            """, (task_id,))

            task = cursor.fetchone()
            cursor.close()
            conn.close()

            if task:
                return dict(task)
            return None

        except Exception as e:
            logger.error(f"❌ 获取任务失败: {e}")
            return None

    def get_tasks_by_session(
        self,
        session_id: str,
        status: str = None
    ) -> List[Dict[str, Any]]:
        """
        获取会话的所有任务

        Args:
            session_id: 会话ID
            status: 任务状态过滤（可选）

        Returns:
            任务列表
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            if status:
                cursor.execute("""
                    SELECT * FROM tasks 
                    WHERE session_id = %s AND status = %s
                    ORDER BY created_at DESC
                """, (session_id, status))
            else:
                cursor.execute("""
                    SELECT * FROM tasks 
                    WHERE session_id = %s
                    ORDER BY created_at DESC
                """, (session_id,))

            tasks = cursor.fetchall()
            cursor.close()
            conn.close()

            return [dict(task) for task in tasks]

        except Exception as e:
            logger.error(f"❌ 获取任务列表失败: {e}")
            return []

    def get_tasks_by_user(
        self,
        user_id: str,
        status: str = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        获取用户的所有任务

        Args:
            user_id: 用户ID
            status: 任务状态过滤（可选）
            limit: 返回数量限制

        Returns:
            任务列表
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            if status:
                cursor.execute("""
                    SELECT * FROM tasks 
                    WHERE user_id = %s AND status = %s
                    ORDER BY created_at DESC
                    LIMIT %s
                """, (user_id, status, limit))
            else:
                cursor.execute("""
                    SELECT * FROM tasks 
                    WHERE user_id = %s
                    ORDER BY created_at DESC
                    LIMIT %s
                """, (user_id, limit))

            tasks = cursor.fetchall()
            cursor.close()
            conn.close()

            return [dict(task) for task in tasks]

        except Exception as e:
            logger.error(f"❌ 获取用户任务列表失败: {e}")
            return []

    def update_task_status(
        self,
        task_id: int,
        status: str,
        result: str = None,
        error_message: str = None
    ) -> bool:
        """
        更新任务状态

        Args:
            task_id: 任务ID
            status: 新状态 (pending, in_progress, waiting, completed, failed, cancelled)
            result: 执行结果（可选）
            error_message: 错误信息（可选）

        Returns:
            是否成功
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            # 构建更新SQL
            update_fields = ["status = %s"]
            params = [status]

            if status == 'in_progress':
                update_fields.append("started_at = CURRENT_TIMESTAMP")
            elif status in ['completed', 'failed', 'cancelled']:
                update_fields.append("completed_at = CURRENT_TIMESTAMP")

            if result is not None:
                update_fields.append("result = %s")
                params.append(result)

            if error_message is not None:
                update_fields.append("error_message = %s")
                params.append(error_message)

            params.append(task_id)

            sql = f"""
                UPDATE tasks 
                SET {', '.join(update_fields)}
                WHERE id = %s
            """

            cursor.execute(sql, params)
            conn.commit()
            cursor.close()
            conn.close()

            logger.info(f"✅ 更新任务状态: ID={task_id}, 状态={status}")
            return True

        except Exception as e:
            logger.error(f"❌ 更新任务状态失败: {e}")
            return False

    def delete_task(self, task_id: int) -> bool:
        """
        删除任务（同时删除所有步骤和子任务）

        Args:
            task_id: 任务ID

        Returns:
            是否成功
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            # 由于设置了ON DELETE CASCADE，删除任务会自动删除步骤和子任务
            cursor.execute("DELETE FROM tasks WHERE id = %s", (task_id,))

            conn.commit()
            cursor.close()
            conn.close()

            logger.info(f"🗑️ 删除任务成功: ID={task_id}")
            return True

        except Exception as e:
            logger.error(f"❌ 删除任务失败: {e}")
            return False

    # ==================== 任务步骤管理 ====================

    def create_step(
        self,
        task_id: int,
        step_num: int,
        description: str,
        action_type: str = None,
        action_params: Dict = None
    ) -> Optional[int]:
        """
        创建任务步骤

        Args:
            task_id: 任务ID
            step_num: 步骤序号
            description: 步骤描述
            action_type: 操作类型 (tool_call, user_confirm, wait等)
            action_params: 操作参数（字典）

        Returns:
            步骤ID，失败返回None
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            # 将参数字典转换为JSON字符串
            params_json = json.dumps(action_params) if action_params else None

            cursor.execute("""
                INSERT INTO task_steps (
                    task_id, step_num, description, 
                    action_type, action_params, status
                )
                VALUES (%s, %s, %s, %s, %s, 'pending')
                RETURNING id
            """, (task_id, step_num, description, action_type, params_json))

            step_id = cursor.fetchone()[0]
            conn.commit()
            cursor.close()
            conn.close()

            logger.info(f"📋 创建步骤成功: TaskID={task_id}, StepNum={step_num}")
            return step_id

        except Exception as e:
            logger.error(f"❌ 创建步骤失败: {e}")
            return None

    def get_task_steps(self, task_id: int) -> List[Dict[str, Any]]:
        """
        获取任务的所有步骤

        Args:
            task_id: 任务ID

        Returns:
            步骤列表（按step_num排序）
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            cursor.execute("""
                SELECT * FROM task_steps 
                WHERE task_id = %s
                ORDER BY step_num
            """, (task_id,))

            steps = cursor.fetchall()
            cursor.close()
            conn.close()

            # 解析JSON参数
            result = []
            for step in steps:
                step_dict = dict(step)
                if step_dict.get('action_params'):
                    try:
                        step_dict['action_params'] = json.loads(
                            step_dict['action_params'])
                    except:
                        pass
                result.append(step_dict)

            return result

        except Exception as e:
            logger.error(f"❌ 获取任务步骤失败: {e}")
            return []

    def update_step_status(
        self,
        step_id: int,
        status: str,
        result: str = None,
        error_message: str = None
    ) -> bool:
        """
        更新步骤状态

        Args:
            step_id: 步骤ID
            status: 新状态
            result: 执行结果（可选）
            error_message: 错误信息（可选）

        Returns:
            是否成功
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            update_fields = ["status = %s"]
            params = [status]

            if status == 'in_progress':
                update_fields.append("started_at = CURRENT_TIMESTAMP")
            elif status in ['completed', 'failed']:
                update_fields.append("completed_at = CURRENT_TIMESTAMP")

            if result is not None:
                update_fields.append("result = %s")
                params.append(result)

            if error_message is not None:
                update_fields.append("error_message = %s")
                params.append(error_message)

            params.append(step_id)

            sql = f"""
                UPDATE task_steps 
                SET {', '.join(update_fields)}
                WHERE id = %s
            """

            cursor.execute(sql, params)
            conn.commit()
            cursor.close()
            conn.close()

            return True

        except Exception as e:
            logger.error(f"❌ 更新步骤状态失败: {e}")
            return False

    # ==================== 统计和查询 ====================

    def get_task_statistics(self, user_id: str) -> Dict[str, int]:
        """
        获取用户的任务统计信息

        Args:
            user_id: 用户ID

        Returns:
            统计信息字典
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending,
                    SUM(CASE WHEN status = 'in_progress' THEN 1 ELSE 0 END) as in_progress,
                    SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed,
                    SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed
                FROM tasks
                WHERE user_id = %s
            """, (user_id,))

            row = cursor.fetchone()
            cursor.close()
            conn.close()

            return {
                'total': row[0] or 0,
                'pending': row[1] or 0,
                'in_progress': row[2] or 0,
                'completed': row[3] or 0,
                'failed': row[4] or 0
            }

        except Exception as e:
            logger.error(f"❌ 获取任务统计失败: {e}")
            return {
                'total': 0,
                'pending': 0,
                'in_progress': 0,
                'completed': 0,
                'failed': 0
            }
