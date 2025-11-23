from db_setup import SessionLocal, Message
import sys
import os

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def count_messages(session_id):
    session = SessionLocal()
    try:
        count = session.query(Message).filter(
            Message.session_id == session_id).count()
        with open("count_result.txt", "w") as f:
            f.write(f"Session ID: {session_id}\n")
            f.write(f"Message Count: {count}\n")
            f.write(f"Rounds: {count // 2}\n")
        print(f"Session ID: {session_id}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        session.close()


if __name__ == "__main__":
    session_id = "50ca2114-edcb-4f9a-a979-d4e3455a4c4a"
    count_messages(session_id)
