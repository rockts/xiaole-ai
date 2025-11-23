#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
运行第8个数据库迁移: 创建用户反馈表
v0.8.1: 添加message_feedback表用于存储用户对AI回复的评价
"""

import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()


def run_migration():
    """执行数据库迁移"""
    try:
        # 连接数据库
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST'),
            port=int(os.getenv('DB_PORT', 5432)),
            database=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASS')
        )
        conn.autocommit = False
        cursor = conn.cursor()

        print("📖 读取迁移脚本...")
        with open('db_migrations/008_create_feedback_table.sql', 'r',
                  encoding='utf-8') as f:
            migration_sql = f.read()

        print("🚀 执行迁移...")
        cursor.execute(migration_sql)

        conn.commit()
        print("✅ 迁移执行成功！")

        # 验证表是否创建
        cursor.execute("""
            SELECT COUNT(*) FROM information_schema.tables 
            WHERE table_name = 'message_feedback'
        """)
        count = cursor.fetchone()[0]

        if count > 0:
            print(f"✅ message_feedback 表已创建")
        else:
            print(f"⚠️  message_feedback 表未找到")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"❌ 迁移失败: {e}")
        if conn:
            conn.rollback()
        raise


if __name__ == "__main__":
    run_migration()
