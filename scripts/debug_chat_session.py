from db_setup import Conversation, Message, DB_URL
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import sys
import os

# Add parent directory to path to import db_setup
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))), 'backend'))

# Setup DB connection
engine = create_engine(DB_URL, client_encoding='utf8')
SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()


def get_chat_by_id(session_id):
    print(f"正在查找 Session ID: {session_id} ...")

    conv = session.query(Conversation).filter(
        Conversation.session_id == session_id).first()

    if not conv:
        print(f"❌ 未找到 Session ID 为 '{session_id}' 的会话。")
        return

    print(f"\n📝 会话标题: {conv.title}")
    print(f"🆔 Session ID: {conv.session_id}")
    print("-" * 50)

    messages = session.query(Message).filter(
        Message.session_id == conv.session_id).order_by(Message.created_at).all()

    for msg in messages:
        role_icon = "👤" if msg.role == "user" else "🤖"
        role_name = "用户" if msg.role == "user" else "小乐"
        print(
            f"{role_icon} {role_name} ({msg.created_at.strftime('%Y-%m-%d %H:%M:%S')}):")
        print(f"   {msg.content}")
        if msg.image_path:
            print(f"   🖼️ [图片]: {msg.image_path}")
        print("")
    print("=" * 50)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        sid = sys.argv[1]
        get_chat_by_id(sid)
    else:
        print("请提供 Session ID")
