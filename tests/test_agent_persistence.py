import sys
import os
import time

# Add project root to sys.path BEFORE importing backend modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.agent import XiaoLeAgent
from backend.db_setup import SessionLocal, Message

def test_agent_chat_persistence():
    agent = XiaoLeAgent()

    # 1. Start a new chat
    print("--- Round 1 ---")
    result1 = agent.chat("Hello, this is a test message.",
                         user_id="test_user_persist")
    session_id = result1['session_id']
    print(f"Session ID: {session_id}")
    print(f"Reply: {result1['reply'][:50]}...")

    # Verify messages in DB
    session = SessionLocal()
    msgs = session.query(Message).filter(
        Message.session_id == session_id).all()
    print(f"Messages in DB after Round 1: {len(msgs)}")
    for m in msgs:
        print(f" - [{m.role}] {m.content[:20]}...")
    session.close()

    if len(msgs) != 2:
        print("❌ Round 1 failed: Expected 2 messages")
        return

    # 2. Continue chat
    print("\n--- Round 2 ---")
    result2 = agent.chat(
        "What is 1+1?", session_id=session_id, user_id="test_user_persist")
    print(f"Reply: {result2['reply'][:50]}...")

    # Verify messages in DB
    session = SessionLocal()
    # Force expire to ensure fresh data
    session.expire_all()
    msgs = session.query(Message).filter(
        Message.session_id == session_id).order_by(Message.created_at).all()
    print(f"Messages in DB after Round 2: {len(msgs)}")
    for m in msgs:
        print(f" - [{m.role}] {m.content[:20]}...")
    session.close()

    if len(msgs) != 4:
        print("❌ Round 2 failed: Expected 4 messages")
    else:
        print("✅ Persistence test passed!")


if __name__ == "__main__":
    test_agent_chat_persistence()
