from db_setup import SessionLocal, Message
import sys
import os
import re

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def fix_latex(session_id):
    session = SessionLocal()
    try:
        messages = session.query(Message).filter(
            Message.session_id == session_id).all()

        print(f"Found {len(messages)} messages to check.")

        for msg in messages:
            original_content = msg.content
            new_content = original_content

            # Replace block math \[ ... \] with $$ ... $$
            # We use regex to ensure we match the pair
            new_content = re.sub(
                r'\\\[(.*?)\\\]', r'$$\1$$', new_content, flags=re.DOTALL)

            # Replace inline math \( ... \) with $ ... $
            new_content = re.sub(r'\\\((.*?)\\\)', r'$\1$', new_content)

            if original_content != new_content:
                print(f"Updating message {msg.id}...")
                msg.content = new_content
                session.add(msg)
            else:
                print(f"Message {msg.id} needs no changes.")

        session.commit()
        print("All updates committed.")

    except Exception as e:
        session.rollback()
        print(f"Error: {e}")
    finally:
        session.close()


if __name__ == "__main__":
    session_id = "50ca2114-edcb-4f9a-a979-d4e3455a4c4a"
    fix_latex(session_id)
