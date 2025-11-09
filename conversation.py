"""
对话上下文管理模块
管理多轮对话会话和消息历史
"""
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from db_setup import Conversation, Message
import os
from dotenv import load_dotenv
from datetime import datetime
import uuid

load_dotenv()

# 构建数据库 URL
if os.getenv('DATABASE_URL'):
    DB_URL = os.getenv('DATABASE_URL')
else:
    DB_URL = (
        f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASS')}"
        f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}"
        f"/{os.getenv('DB_NAME')}"
    )

engine = create_engine(
    DB_URL,
    connect_args={'check_same_thread': False} if DB_URL.startswith('sqlite')
    else {'client_encoding': 'utf8'}
)
Session = sessionmaker(bind=engine)


class ConversationManager:
    """对话管理器"""

    def __init__(self):
        self.session = Session()

    def create_session(self, user_id="default_user", title=None):
        """创建新的对话会话"""
        session_id = str(uuid.uuid4())
        if not title:
            title = f"对话 {datetime.now().strftime('%Y-%m-%d %H:%M')}"

        conversation = Conversation(
            session_id=session_id,
            user_id=user_id,
            title=title
        )
        self.session.add(conversation)
        self.session.commit()
        return session_id

    def add_message(self, session_id, role, content):
        """添加消息到对话会话"""
        message = Message(
            session_id=session_id,
            role=role,
            content=content
        )
        self.session.add(message)
        self.session.commit()

        # 更新会话的最后更新时间
        conversation = self.session.query(Conversation).filter(
            Conversation.session_id == session_id
        ).first()
        if conversation:
            conversation.updated_at = datetime.now()
            self.session.commit()

    def get_history(self, session_id, limit=10):
        """获取对话历史"""
        messages = self.session.query(Message).filter(
            Message.session_id == session_id
        ).order_by(Message.created_at.desc()).limit(limit).all()

        # 反转顺序，使最早的消息在前
        messages.reverse()

        return [
            {"role": m.role, "content": m.content}
            for m in messages
        ]

    def get_recent_sessions(self, user_id="default_user", limit=5):
        """获取最近的对话会话"""
        sessions = self.session.query(Conversation).filter(
            Conversation.user_id == user_id
        ).order_by(Conversation.updated_at.desc()).limit(limit).all()

        return [
            {
                "session_id": s.session_id,
                "title": s.title,
                "created_at": s.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                "updated_at": s.updated_at.strftime('%Y-%m-%d %H:%M:%S')
            }
            for s in sessions
        ]

    def delete_session(self, session_id):
        """删除对话会话及其消息"""
        # 删除消息
        self.session.query(Message).filter(
            Message.session_id == session_id
        ).delete()

        # 删除会话
        self.session.query(Conversation).filter(
            Conversation.session_id == session_id
        ).delete()

        self.session.commit()

    def get_session_stats(self, session_id):
        """获取会话统计信息"""
        from sqlalchemy import func

        conversation = self.session.query(Conversation).filter(
            Conversation.session_id == session_id
        ).first()

        if not conversation:
            return None

        message_count = self.session.query(func.count(Message.id)).filter(
            Message.session_id == session_id
        ).scalar()

        return {
            "session_id": session_id,
            "title": conversation.title,
            "message_count": message_count,
            "created_at": conversation.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            "updated_at": conversation.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        }
