from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# 优先使用 DATABASE_URL，如果没有则构建PostgreSQL URL
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
Base = declarative_base()


class Memory(Base):
    __tablename__ = "memories"
    id = Column(Integer, primary_key=True)
    content = Column(Text)
    tag = Column(String(50))
    created_at = Column(DateTime, default=datetime.now)


class Conversation(Base):
    """对话会话表"""
    __tablename__ = "conversations"
    id = Column(Integer, primary_key=True)
    session_id = Column(String(100), unique=True, index=True)
    user_id = Column(String(50), default="default_user")
    title = Column(String(200))
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class Message(Base):
    """对话消息表"""
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True)
    session_id = Column(String(100), index=True)
    role = Column(String(20))  # user / assistant
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.now)


Base.metadata.create_all(engine)
print("✅ 数据库初始化完成。")
