"""快速清理测试数据"""
from memory import MemoryManager
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

DB_URL = (
    f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASS')}"
    f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}"
    f"/{os.getenv('DB_NAME')}"
)

engine = create_engine(DB_URL)
Session = sessionmaker(bind=engine)
db = Session()

print("清理测试数据...")

# 删除test用户数据
db.execute(text("DELETE FROM user_behaviors WHERE user_id LIKE '%test%'"))
db.execute(text("DELETE FROM messages WHERE session_id IN (SELECT session_id FROM conversations WHERE user_id LIKE '%test%')"))
db.execute(text("DELETE FROM conversations WHERE user_id LIKE '%test%'"))

# 删除测试记忆
db.execute(text("DELETE FROM memories WHERE content LIKE '%小明%' OR content LIKE '%test%' OR content LIKE '%测试%'"))

db.commit()
print("✅ 清理完成")

# 显示统计
result = db.execute(text("SELECT COUNT(*) FROM memories"))
print(f"剩余记忆: {result.scalar()}")

result = db.execute(text("SELECT COUNT(*) FROM conversations"))
print(f"剩余会话: {result.scalar()}")

db.close()
