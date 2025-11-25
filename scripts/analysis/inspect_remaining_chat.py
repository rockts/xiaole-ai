from db_setup import SessionLocal, Message
import sys
import os

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def inspect_messages(session_id):
    session = SessionLocal()
    try:
        messages = session.query(Message).filter(
            Message.session_id == session_id).order_by(Message.id).all()

        print(f"Found {len(messages)} messages.")
        for i, msg in enumerate(messages):
            print(f"--- Message {i+1} ({msg.role}) ---")
            print(msg.content)
            print("-----------------------------")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        session.close()


if __name__ == "__main__":
    session_id = "50ca2114-edcb-4f9a-a979-d4e3455a4c4a"
    inspect_messages(session_id)
