from db_setup import Memory, SessionLocal as Session
import sys
import os

# Add backend to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))


def fix_family_names():
    session = Session()
    try:
        # 1. Check for any other conflicting memories and delete them
        conflicting_keywords = ['女儿姓名：高艺篪', '儿子姓名：高艺瑄']
        for kw in conflicting_keywords:
            bad_mems = session.query(Memory).filter(
                Memory.content.like(f'%{kw}%')).all()
            for mem in bad_mems:
                print(
                    f"Deleting conflicting memory ID {mem.id}: {mem.content}")
                session.delete(mem)

        # 2. Add the correct, definitive memory
        correct_content = "【家庭成员档案】\n女儿姓名：高艺瑄 (Gao Yixuan)\n儿子姓名：高艺篪 (Gao Yichi)\n关系：龙凤胎\n学校：天水市秦州区逸夫中学"

        # Check if this already exists to avoid duplicates
        existing = session.query(Memory).filter(
            Memory.tag == 'facts',
            Memory.content == correct_content
        ).first()

        if not existing:
            new_memory = Memory(
                content=correct_content,
                tag='facts'
            )
            session.add(new_memory)
            print("✅ Added definitive family memory.")
        else:
            print("ℹ️ Definitive memory already exists.")

        session.commit()

    finally:
        session.close()


if __name__ == "__main__":
    fix_family_names()
