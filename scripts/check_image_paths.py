from backend.db_setup import SessionLocal, Message
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def check_images():
    session = SessionLocal()
    try:
        messages = session.query(Message).filter(
            Message.image_path.isnot(None)).all()
        print(f"Found {len(messages)} messages with images.")
        for msg in messages:
            print(
                f"ID: {msg.id}, Role: {msg.role}, Image Path: {msg.image_path}")
    finally:
        session.close()


if __name__ == "__main__":
    check_images()
