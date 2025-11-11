"""执行数据库迁移"""
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()

DB_URL = (
    f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASS')}"
    f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)

engine = create_engine(DB_URL, client_encoding='utf8')

with open('db_migrations/004_memory_importance_v0.6.0.sql', encoding='utf-8') as f:
    sql = f.read()
    
with engine.connect() as conn:
    # 分开执行DO块和CREATE INDEX
    parts = sql.split('$$;')
    if len(parts) >= 2:
        # 执行DO块
        conn.execute(text(parts[0] + '$$;'))
        conn.commit()
        # 执行CREATE INDEX
        for stmt in parts[1].strip().split(';'):
            if stmt.strip():
                try:
                    conn.execute(text(stmt + ';'))
                    conn.commit()
                except Exception as e:
                    if 'already exists' in str(e):
                        print(f"索引已存在，跳过")
                    else:
                        raise

print('✅ 数据库迁移完成')
