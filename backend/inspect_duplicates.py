from db_setup import SessionLocal, Message
import sys
import os

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def inspect_duplicates(session_id):
    session = SessionLocal()
    try:
        messages = session.query(Message).filter(
            Message.session_id == session_id).order_by(Message.id).all()

        # We expect 8 messages now. Let's look at the last 4.
        if len(messages) >= 8:
            last_4 = messages[-4:]
            for msg in last_4:
                print(f"--- Message {msg.id} ({msg.role}) ---")
                print(msg.content[:100] + "...")
        else:
            print(f"Only found {len(messages)} messages.")

    finally:
        session.close()


if __name__ == "__main__":
    session_id = "50ca2114-edcb-4f9a-a979-d4e3455a4c4a"
    inspect_duplicates(session_id)
