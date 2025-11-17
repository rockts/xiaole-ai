#!/usr/bin/env python3
"""
运行数据库迁移 010: 添加会话置顶字段
"""
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()


def run_migration():
    # 连接数据库
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASS'),
        client_encoding='utf8'
    )

    try:
        cursor = conn.cursor()

        # 读取SQL文件
        with open('db_migrations/010_add_conversation_pinned.sql', 'r', encoding='utf-8') as f:
            sql = f.read()

        # 执行迁移
        cursor.execute(sql)
        conn.commit()

        print("✅ 迁移 010 执行成功: 添加会话置顶字段")

    except Exception as e:
        conn.rollback()
        print(f"❌ 迁移失败: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    run_migration()
