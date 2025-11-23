from db_setup import Memory, DB_URL
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# Setup DB connection
engine = create_engine(DB_URL)
SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()


def add_schedule_memory():
    print("🧠 正在修复记忆库...")

    # Define the schedule based on historical chat analysis
    schedule_content = """用户课程表（周一至周五）：
- 周一：第3节 科学(6年级)、第4节 科学(4年级)、第5节 音乐(1年级)
- 周二：第2节 科学(5年级)、第5节 音乐(1年级)
- 周三：第4节 科学(5年级)、第6节 科学(4年级)
- 周四：第3节 科学(6年级)、第4节 健康(5年级)、第6节 体育(1年级)
- 周五：第4节 体育(1年级)
(注：括号内为年级，晨读课程不计入正式课表)"""

    # Check if already exists to avoid duplicates
    existing = session.query(Memory).filter(
        Memory.content.like("%用户课程表%")).first()

    if existing:
        print("⚠️ 发现已存在类似的课程表记忆，正在更新...")
        existing.content = schedule_content
        existing.created_at = datetime.now()
    else:
        print("➕ 正在插入新的课程表记忆...")
        new_memory = Memory(
            content=schedule_content,
            tag="schedule",
            created_at=datetime.now()
        )
        session.add(new_memory)

    # Add specific rule about morning reading
    rule_content = "用户偏好：统计课程数量时不要算晨读，晨读不计入正式课程。"
    existing_rule = session.query(Memory).filter(
        Memory.content.like("%晨读%")).first()
    if not existing_rule:
        print("➕ 正在插入晨读规则记忆...")
        session.add(Memory(content=rule_content, tag="preference"))

    session.commit()
    print("✅ 记忆修复完成！小乐现在应该能记住您的课表了。")


if __name__ == "__main__":
    add_schedule_memory()
