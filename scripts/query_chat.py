from db_setup import Conversation, Message, DB_URL
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import sys
import os

# Add parent directory to path to import db_setup
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# Setup DB connection
engine = create_engine(DB_URL)
SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()


def get_chat_history(title_query):
    print(f"正在查找标题包含 '{title_query}' 的会话...")
    # Fetch all conversations and filter in Python to avoid encoding issues with some drivers
    all_conversations = session.query(Conversation).all()
    conversations = [
        c for c in all_conversations if c.title and title_query in c.title]

    if not conversations:
        print(f"❌ 未找到标题包含 '{title_query}' 的会话。")
        return

    for conv in conversations:
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
        query = sys.argv[1]
    else:
        query = "小乐猜猜我在哪里"
    get_chat_history(query)
