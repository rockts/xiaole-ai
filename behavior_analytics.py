"""
用户行为分析模块 - v0.3.0 Learning层
功能：
1. 收集用户对话行为数据
2. 分析对话模式（活跃时间、话题偏好）
3. 生成行为统计报告
"""

from sqlalchemy import create_engine, func, desc
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
from collections import Counter
import json
import os
from dotenv import load_dotenv

load_dotenv()

# 数据库连接
if os.getenv('DATABASE_URL'):
    DB_URL = os.getenv('DATABASE_URL')
else:
    DB_URL = (
        f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASS')}"
        f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}"
        f"/{os.getenv('DB_NAME')}"
    )

engine = create_engine(DB_URL)
SessionLocal = sessionmaker(bind=engine)


class BehaviorAnalyzer:
    """用户行为分析器"""

    def __init__(self):
        self.session = SessionLocal()

    def record_session_behavior(self, user_id, session_id):
        """
        记录单次会话的行为数据
        
        Args:
            user_id: 用户ID
            session_id: 会话ID
        """
        from db_setup import Message, Memory, UserBehavior

        # 查询会话消息
        messages = self.session.query(Message).filter(
            Message.session_id == session_id
        ).all()

        if not messages:
            return None

        # 统计数据
        user_messages = [m for m in messages if m.role == "user"]
        message_count = len(messages)
        user_message_count = len(user_messages)

        # 计算平均消息长度
        if user_messages:
            total_length = sum(len(m.content) for m in user_messages)
            avg_length = total_length // user_message_count
        else:
            avg_length = 0

        # 计算会话时长
        start_time = messages[0].created_at
        end_time = messages[-1].created_at
        duration = int((end_time - start_time).total_seconds())

        # 提取话题（从记忆标签中获取）
        # 简化版：从会话中提取关键词作为话题
        topics = self._extract_topics(user_messages)

        # 检查是否已存在记录
        existing = self.session.query(UserBehavior).filter(
            UserBehavior.session_id == session_id
        ).first()

        if existing:
            # 更新现有记录
            existing.message_count = message_count
            existing.user_message_count = user_message_count
            existing.avg_message_length = avg_length
            existing.end_time = end_time
            existing.duration_seconds = duration
            existing.topics = json.dumps(topics, ensure_ascii=False)
        else:
            # 创建新记录
            behavior = UserBehavior(
                user_id=user_id,
                session_id=session_id,
                message_count=message_count,
                user_message_count=user_message_count,
                avg_message_length=avg_length,
                start_time=start_time,
                end_time=end_time,
                duration_seconds=duration,
                topics=json.dumps(topics, ensure_ascii=False)
            )
            self.session.add(behavior)

        self.session.commit()
        return {
            "session_id": session_id,
            "message_count": message_count,
            "duration": duration,
            "topics": topics
        }

    def _extract_topics(self, messages, top_n=5):
        """
        从消息中提取话题关键词
        
        Args:
            messages: 消息列表
            top_n: 返回前N个高频词
        
        Returns:
            话题列表
        """
        try:
            import jieba
            import jieba.analyse
        except ImportError:
            # 如果jieba未安装，返回空列表
            return []

        # 合并所有用户消息
        text = " ".join([m.content for m in messages])

        # 提取关键词
        keywords = jieba.analyse.extract_tags(text, topK=top_n)
        return keywords

    def get_user_activity_pattern(self, user_id, days=30):
        """
        获取用户活跃时间模式
        
        Args:
            user_id: 用户ID
            days: 统计最近N天
        
        Returns:
            {
                "hourly_distribution": {0: 5, 1: 2, ...},  # 按小时统计
                "daily_distribution": {0: 10, 1: 8, ...},  # 按星期统计
                "most_active_hour": 14,
                "most_active_day": "周三"
            }
        """
        from db_setup import UserBehavior

        # 查询最近N天的行为记录
        since = datetime.now() - timedelta(days=days)
        behaviors = self.session.query(UserBehavior).filter(
            UserBehavior.user_id == user_id,
            UserBehavior.created_at >= since
        ).all()

        if not behaviors:
            return None

        # 按小时统计
        hourly = Counter()
        daily = Counter()

        for b in behaviors:
            hour = b.start_time.hour
            day = b.start_time.weekday()
            hourly[hour] += 1
            daily[day] += 1

        # 找出最活跃时段
        most_active_hour = hourly.most_common(1)[0][0] if hourly else None
        most_active_day = daily.most_common(1)[0][0] if daily else None

        day_names = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]

        return {
            "hourly_distribution": dict(hourly),
            "daily_distribution": dict(daily),
            "most_active_hour": most_active_hour,
            "most_active_day": day_names[most_active_day]
            if most_active_day is not None else None,
            "total_sessions": len(behaviors),
            "period_days": days
        }

    def get_topic_preferences(self, user_id, days=30, top_n=10):
        """
        获取用户话题偏好
        
        Args:
            user_id: 用户ID
            days: 统计最近N天
            top_n: 返回前N个高频话题
        
        Returns:
            {
                "top_topics": [("话题1", 10), ("话题2", 8), ...],
                "total_topics": 50
            }
        """
        from db_setup import UserBehavior

        # 查询最近N天的行为记录
        since = datetime.now() - timedelta(days=days)
        behaviors = self.session.query(UserBehavior).filter(
            UserBehavior.user_id == user_id,
            UserBehavior.created_at >= since
        ).all()

        if not behaviors:
            return None

        # 统计所有话题
        all_topics = []
        for b in behaviors:
            if b.topics:
                try:
                    topics = json.loads(b.topics)
                    all_topics.extend(topics)
                except json.JSONDecodeError:
                    continue

        topic_counts = Counter(all_topics)

        return {
            "top_topics": topic_counts.most_common(top_n),
            "total_topics": len(topic_counts),
            "period_days": days
        }

    def get_conversation_stats(self, user_id, days=30):
        """
        获取对话统计数据
        
        Args:
            user_id: 用户ID
            days: 统计最近N天
        
        Returns:
            对话统计信息
        """
        from db_setup import UserBehavior

        # 查询最近N天的行为记录
        since = datetime.now() - timedelta(days=days)
        behaviors = self.session.query(UserBehavior).filter(
            UserBehavior.user_id == user_id,
            UserBehavior.created_at >= since
        ).all()

        if not behaviors:
            return None

        total_sessions = len(behaviors)
        total_messages = sum(b.message_count for b in behaviors)
        total_user_messages = sum(b.user_message_count for b in behaviors)
        total_duration = sum(b.duration_seconds for b in behaviors)

        avg_messages_per_session = (
            total_messages // total_sessions if total_sessions > 0 else 0
        )
        avg_duration_per_session = (
            total_duration // total_sessions if total_sessions > 0 else 0
        )

        # 计算平均消息长度
        avg_lengths = [
            b.avg_message_length for b in behaviors
            if b.avg_message_length > 0
        ]
        overall_avg_length = (
            sum(avg_lengths) // len(avg_lengths) if avg_lengths else 0
        )

        return {
            "total_sessions": total_sessions,
            "total_messages": total_messages,
            "total_user_messages": total_user_messages,
            "avg_messages_per_session": avg_messages_per_session,
            "total_duration_minutes": total_duration // 60,
            "avg_duration_per_session_minutes": avg_duration_per_session // 60,
            "avg_message_length": overall_avg_length,
            "period_days": days
        }

    def generate_behavior_report(self, user_id, days=30):
        """
        生成用户行为分析报告
        
        Args:
            user_id: 用户ID
            days: 统计最近N天
        
        Returns:
            完整的行为分析报告
        """
        return {
            "user_id": user_id,
            "report_date": datetime.now().isoformat(),
            "activity_pattern": self.get_user_activity_pattern(user_id, days),
            "topic_preferences": self.get_topic_preferences(user_id, days),
            "conversation_stats": self.get_conversation_stats(user_id, days)
        }

    def __del__(self):
        """清理数据库连接"""
        if hasattr(self, 'session'):
            self.session.close()
