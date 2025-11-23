from db_setup import SessionLocal, Message
import sys
import os

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def get_second_round(session_id):
    session = SessionLocal()
    try:
        messages = session.query(Message).filter(
            Message.session_id == session_id).order_by(Message.id).all()

        if len(messages) < 4:
            print("Not enough messages for a second round.")
            return

        # Assuming standard User -> Assistant flow
        # Round 1: Index 0 (User), Index 1 (Assistant)
        # Round 2: Index 2 (User), Index 3 (Assistant)

        user_msg = messages[2]
        assistant_msg = messages[3]

        print(f"--- Second Round ---")
        print(f"User ({user_msg.role}): {user_msg.content}")
        print(f"Assistant ({assistant_msg.role}): {assistant_msg.content}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        session.close()


if __name__ == "__main__":
    session_id = "50ca2114-edcb-4f9a-a979-d4e3455a4c4a"
    get_second_round(session_id)
