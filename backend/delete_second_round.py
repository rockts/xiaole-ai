from db_setup import SessionLocal, Message
import sys
import os

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def delete_second_round(session_id):
    session = SessionLocal()
    try:
        messages = session.query(Message).filter(
            Message.session_id == session_id).order_by(Message.id).all()

        if len(messages) < 4:
            print("Not enough messages for a second round.")
            return

        # Round 2: Index 2 (User), Index 3 (Assistant)
        msg_user = messages[2]
        msg_assistant = messages[3]

        print(f"Deleting Second Round:")
        print(
            f"User Message ID: {msg_user.id}, Content: {msg_user.content[:50]}...")
        print(
            f"Assistant Message ID: {msg_assistant.id}, Content: {msg_assistant.content[:50]}...")

        session.delete(msg_user)
        session.delete(msg_assistant)
        session.commit()
        print("Deletion successful.")

    except Exception as e:
        session.rollback()
        print(f"Error: {e}")
    finally:
        session.close()


if __name__ == "__main__":
    session_id = "50ca2114-edcb-4f9a-a979-d4e3455a4c4a"
    delete_second_round(session_id)
