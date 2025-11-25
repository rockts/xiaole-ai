from db_setup import SessionLocal, Message
import sys
import os

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def delete_last_round(session_id):
    session = SessionLocal()
    try:
        messages = session.query(Message).filter(
            Message.session_id == session_id).order_by(Message.id).all()

        if len(messages) < 8:
            print("Not enough messages to delete.")
            return

        # Delete the last 2 messages (Round 4)
        msg_user = messages[-2]
        msg_assistant = messages[-1]

        print(f"Deleting Last Round:")
        print(f"User Message ID: {msg_user.id}")
        print(f"Assistant Message ID: {msg_assistant.id}")

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
    delete_last_round(session_id)
