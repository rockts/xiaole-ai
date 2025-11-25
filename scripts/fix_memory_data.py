from db_setup import Memory, DB_URL
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import sys
import os

# Add parent directory to path to import db_setup
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))), 'backend'))


# Setup DB connection
engine = create_engine(DB_URL, client_encoding='utf8')
SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()


def fix_memory():
    print("正在检查并修复记忆数据...")

    # 1. Find and delete incorrect facts about daughter
    bad_facts = [
        "女儿姓名：高艺篪",
        "女儿姓名：乐儿",
        "女儿名字：高艺篪",
        "女儿名字：乐儿"
    ]

    for bad_fact in bad_facts:
        entries = session.query(Memory).filter(
            Memory.tag == 'facts',
            Memory.content.like(f"%{bad_fact}%")
        ).all()

        for entry in entries:
            print(f"🗑️ 删除错误记忆 (ID: {entry.id}): {entry.content}")
            session.delete(entry)

    # 2. Verify if correct facts exist, if not add them
    correct_facts = [
        "女儿姓名：高艺瑄",
        "女儿小名：可儿",
        "儿子姓名：高艺篪",
        "儿子小名：乐儿"
    ]

    for fact in correct_facts:
        exists = session.query(Memory).filter(
            Memory.tag == 'facts',
            Memory.content.like(f"%{fact}%")
        ).first()

        if exists:
            print(f"✅ 正确记忆已存在: {exists.content}")
        else:
            print(f"➕ 添加缺失记忆: {fact}")
            new_memory = Memory(tag='facts', content=fact)
            session.add(new_memory)

    session.commit()
    print("🎉 记忆修复完成！")


if __name__ == "__main__":
    fix_memory()
