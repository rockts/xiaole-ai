#!/usr/bin/env python3
"""执行数据库迁移脚本 012"""
from dotenv import load_dotenv
import os
import sys
import psycopg2
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 从.env加载配置
load_dotenv()


def run_migration():
    """执行数据库迁移"""
    # 数据库连接配置
    db_config = {
        'host': os.getenv('DB_HOST', '192.168.88.188'),
        'port': int(os.getenv('DB_PORT', 5432)),
        'user': os.getenv('DB_USER', 'xiaole_user'),
        'password': os.getenv('DB_PASS', 'Xiaole2025User'),
        'database': os.getenv('DB_NAME', 'xiaole_ai')
    }

    # 读取迁移脚本
    migration_file = project_root / 'backend' / 'db_migrations' / \
        '012_add_user_behavior_fields.sql'
    print(f"📖 读取迁移文件: {migration_file}")

    with open(migration_file, 'r', encoding='utf-8') as f:
        sql_script = f.read()

    # 连接数据库并执行
    print(
        f"🔌 连接数据库: {db_config['host']}:{db_config['port']}/{db_config['database']}")

    try:
        conn = psycopg2.connect(**db_config)
        conn.autocommit = True  # 自动提交,支持DDL语句
        conn.set_client_encoding('UTF8')  # 设置客户端编码
        cursor = conn.cursor()

        print("⚙️  执行迁移脚本...")

        # 直接执行整个脚本
        try:
            cursor.execute(sql_script)
            print(f"    ✓ 成功")
        except Exception as e:
            print(f"    ✗ 失败: {e}")
            raise

        print("✅ 迁移成功！")
        print("\n📋 验证新字段:")

        # 验证表结构
        cursor.execute("""
            SELECT column_name, data_type, column_default
            FROM information_schema.columns
            WHERE table_name = 'user_behaviors'
            AND column_name IN ('sentiment_score', 'interaction_type')
            ORDER BY ordinal_position;
        """)

        results = cursor.fetchall()
        for col_name, data_type, default_val in results:
            print(f"  ✓ {col_name}: {data_type} (默认值: {default_val})")

        cursor.close()
        conn.close()
        print("\n🎉 数据库迁移完成！")

    except Exception as e:
        print(f"❌ 迁移失败: {e}")
        sys.exit(1)


if __name__ == '__main__':
    run_migration()
