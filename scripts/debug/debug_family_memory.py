from sqlalchemy import or_
from db_setup import Memory, SessionLocal as Session
import sys
import os

# Add backend to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))


def check_family_memories():
    session = Session()
    try:
        keywords = ['儿子', '女儿', '高艺瑄', '高艺篪', '孩子', '姑娘']
        filters = [Memory.content.like(f'%{kw}%') for kw in keywords]

        memories = session.query(Memory).filter(
            or_(*filters)).order_by(Memory.created_at.desc()).all()

        print(f"Found {len(memories)} related memories:")
        print("-" * 50)
        for mem in memories:
            print(f"ID: {mem.id}")
            print(f"Tag: {mem.tag}")
            print(f"Time: {mem.created_at}")
            print(f"Content: {mem.content}")
            print("-" * 50)

    finally:
        session.close()


if __name__ == "__main__":
    check_family_memories()
