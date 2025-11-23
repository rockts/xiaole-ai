
from backend.db_setup import Memory, SessionLocal
import sys
import os
# Add the project root to sys.path
sys.path.append(os.getcwd())


def check_memories():
    session = SessionLocal()
    try:
        # Check for document memories
        docs = session.query(Memory).filter(
            Memory.tag.like('document:%')).all()
        print(f"Found {len(docs)} document memories:")
        for doc in docs:
            print(f"  Tag: {doc.tag}")
            print(f"  Content Preview: {doc.content[:50]}...")
            print("-" * 20)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        session.close()


if __name__ == "__main__":
    check_memories()
