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
        pass

    def create_session(self, user_id="default_user", title=None):
        """创建新的对话会话"""
        if not title:
            title = f"对话 {datetime.now().strftime('%Y-%m-%d %H:%M')}"

        # 移除会话去重逻辑，确保每次都创建新会话
        # 之前的逻辑会导致10分钟内相同标题的会话被合并，用户体验不佳

        # 创建新会话
        session_id = str(uuid.uuid4())
        conversation = Conversation(
            session_id=session_id,
            user_id=user_id,
            title=title
        )

        session = Session()
        try:
            session.add(conversation)
            session.commit()
            print(f"✅ 会话已创建: {session_id} - {title}")
            return session_id
        except Exception as e:
            session.rollback()
            print(f"❌ 会话创建失败: {e}")
            raise
        finally:
            session.close()

    def add_message(self, session_id, role, content, image_path=None):
        """添加消息到对话会话"""
        session = Session()
        try:
            message = Message(
                session_id=session_id,
                role=role,
                content=content,
                image_path=image_path
            )
            session.add(message)
            session.commit()

            # 更新会话的最后更新时间
            conversation = session.query(Conversation).filter(
                Conversation.session_id == session_id
            ).first()
            if conversation:
                conversation.updated_at = datetime.now()
                session.commit()

            return message.id
        finally:
            session.close()

    def get_history(self, session_id, limit=10):
        """获取对话历史"""
        session = Session()
        try:
            messages = session.query(Message).filter(
                Message.session_id == session_id
            ).order_by(Message.created_at.desc()).limit(limit).all()

            # 反转顺序，使最早的消息在前
            messages.reverse()

            return [
                {
                    "id": m.id,
                    "role": m.role,
                    "content": m.content,
                    "timestamp": m.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    "created_at": m.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    "image_path": (m.image_path if hasattr(m, 'image_path')
                                   else None)
                }
                for m in messages
            ]
        finally:
            session.close()

    def delete_message_and_following(self, message_id):
        """删除指定消息及其之后的所有消息"""
        session = Session()
        try:
            # 查找目标消息
            target_msg = session.query(Message).filter(
                Message.id == message_id
            ).first()

            if not target_msg:
                return False

            # 删除该会话中，创建时间晚于等于该消息的所有消息
            # 注意：使用 >= 包含目标消息本身
            session.query(Message).filter(
                Message.session_id == target_msg.session_id,
                Message.created_at >= target_msg.created_at
            ).delete(synchronize_session=False)

            session.commit()
            return True
        except Exception as e:
            print(f"删除消息失败: {e}")
            session.rollback()
            return False
        finally:
            session.close()

    def get_recent_sessions(self, user_id="default_user", limit=None):
        """获取最近的对话会话"""
        session = Session()
        try:
            query = session.query(Conversation).filter(
                Conversation.user_id == user_id
            ).order_by(Conversation.updated_at.desc())

            if limit is not None:
                query = query.limit(limit)

            sessions = query.all()

            return [
                {
                    "session_id": s.session_id,
                    "title": s.title,
                    "pinned": getattr(s, 'pinned', False),  # v0.8.1
                    "created_at": s.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    "updated_at": s.updated_at.strftime('%Y-%m-%d %H:%M:%S')
                }
                for s in sessions
            ]
        except Exception as e:
            print(f"获取会话列表失败: {e}")
            session.rollback()
            return []
        finally:
            session.close()

    def delete_session(self, session_id):
        """删除对话会话及其消息"""
        session = Session()
        try:
            # 删除消息
            session.query(Message).filter(
                Message.session_id == session_id
            ).delete()

            # 删除会话
            session.query(Conversation).filter(
                Conversation.session_id == session_id
            ).delete()

            session.commit()
        finally:
            session.close()

    def update_session_title(self, session_id, new_title):
        """更新会话标题"""
        session = Session()
        try:
            conversation = session.query(Conversation).filter(
                Conversation.session_id == session_id
            ).first()

            if conversation:
                conversation.title = new_title
                conversation.updated_at = datetime.now()
                session.commit()
                return True
            return False
        finally:
            session.close()

    def update_session_pinned(self, session_id, pinned):
        """更新会话置顶状态"""
        session = Session()
        try:
            conversation = session.query(Conversation).filter(
                Conversation.session_id == session_id
            ).first()

            if conversation:
                conversation.pinned = pinned
                conversation.updated_at = datetime.now()
                session.commit()
                return True
            return False
        finally:
            session.close()

    def get_session_stats(self, session_id):
        """获取会话统计信息"""
        from sqlalchemy import func
        session = Session()
        try:
            conversation = session.query(Conversation).filter(
                Conversation.session_id == session_id
            ).first()

            if not conversation:
                return None

            message_count = session.query(func.count(Message.id)).filter(
                Message.session_id == session_id
            ).scalar()

            return {
                "session_id": session_id,
                "title": conversation.title,
                "message_count": message_count,
                "created_at": conversation.created_at.strftime(
                    '%Y-%m-%d %H:%M:%S'
                ),
                "updated_at": conversation.updated_at.strftime(
                    '%Y-%m-%d %H:%M:%S'
                )
            }
        finally:
            session.close()
