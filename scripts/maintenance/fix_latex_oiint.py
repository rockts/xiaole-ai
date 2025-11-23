from db_setup import SessionLocal, Message
import sys
import os
import re

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def fix_oiint(session_id):
    session = SessionLocal()
    try:
        messages = session.query(Message).filter(
            Message.session_id == session_id).all()

        print(f"Found {len(messages)} messages to check.")

        for msg in messages:
            original_content = msg.content
            new_content = original_content

            # Replace \oiint with \oint
            # We use simple string replacement as it's safer than regex for this specific symbol
            if "\\oiint" in new_content:
                print(
                    f"Found \\oiint in message {msg.id}, replacing with \\oint...")
                new_content = new_content.replace("\\oiint", "\\oint")

            if original_content != new_content:
                msg.content = new_content
                session.add(msg)
                print(f"Message {msg.id} updated.")
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
    fix_oiint(session_id)
