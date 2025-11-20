
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

# Manually set DB URL if not in env correctly for this script context
DB_URL = "postgresql://xiaole_user:Xiaole2025User@192.168.88.188:5432/xiaole_ai"

engine = create_engine(DB_URL)

with engine.connect() as conn:
    # Get the last session ID
    result = conn.execute(
        text("SELECT session_id FROM messages ORDER BY created_at DESC LIMIT 1"))
    last_session_id = result.scalar()

    if last_session_id:
        print(f"Last Session ID: {last_session_id}")
        # Get messages for this session
        msgs = conn.execute(text(
            f"SELECT role, content, created_at FROM messages WHERE session_id = '{last_session_id}' ORDER BY created_at ASC"))
        for row in msgs:
            print(f"[{row.created_at}] {row.role}: {row.content}")
    else:
        print("No messages found.")
