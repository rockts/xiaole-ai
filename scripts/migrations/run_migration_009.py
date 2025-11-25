#!/usr/bin/env python3
"""
Database Migration 009: Add image_path to messages table
运行此脚本以在messages表中添加image_path字段
"""
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()


def run_migration():
    """执行数据库迁移"""
    try:
        print('🔌 正在连接数据库...')
        # 连接数据库（添加连接超时）
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST', '192.168.88.188'),
            port=os.getenv('DB_PORT', '5432'),
            database=os.getenv('DB_NAME', 'xiaole_ai'),
            user=os.getenv('DB_USER', 'xiaole_user'),
            password=os.getenv('DB_PASS', 'Xiaole2025User'),
            client_encoding='UTF8',
            connect_timeout=10  # 10秒连接超时
        )
        conn.autocommit = False
        cursor = conn.cursor()
        print('✅ 数据库连接成功')

        # 先检查数据量
        print('📊 检查数据表大小...')
        cursor.execute("SELECT COUNT(*) FROM messages")
        count = cursor.fetchone()[0]
        print(f'   messages表记录数: {count:,} 条')

        # 检查字段是否已存在
        cursor.execute("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'messages' AND column_name = 'image_path'
        """)
        if cursor.fetchone():
            print('✅ image_path 字段已存在，无需迁移')
            cursor.close()
            conn.close()
            return

        print('📖 读取迁移脚本...')
        with open('db_migrations/009_add_message_image_path.sql', 'r',
                  encoding='utf-8') as f:
            migration_sql = f.read()

        print('🚀 执行迁移（数据量大，可能需要5-10分钟，请耐心等待）...')
        # 设置语句超时为10分钟
        cursor.execute("SET statement_timeout = '600s'")
        cursor.execute(migration_sql)
        conn.commit()

        print('✅ 迁移执行成功!')

        # 验证字段已添加
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'messages' 
            AND column_name = 'image_path'
        """)
        result = cursor.fetchone()

        if result:
            print(f'✅ image_path 字段已添加: {result[0]} ({result[1]})')
        else:
            print('⚠️ 警告：无法验证字段是否添加成功')

        cursor.close()
        conn.close()

    except Exception as e:
        print(f'❌ 迁移失败: {e}')
        raise


if __name__ == '__main__':
    run_migration()
