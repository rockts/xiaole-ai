#!/usr/bin/env python3
"""检查PostgreSQL数据库权限和表所有者"""
from dotenv import load_dotenv
import os
import sys
from pathlib import Path
import psycopg2

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

load_dotenv()


def check_permissions():
    db_config = {
        'host': os.getenv('DB_HOST', '192.168.88.188'),
        'port': int(os.getenv('DB_PORT', 5432)),
        'user': os.getenv('DB_USER', 'xiaole_user'),
        'password': os.getenv('DB_PASS', 'Xiaole2025User'),
        'database': os.getenv('DB_NAME', 'xiaole_ai')
    }

    try:
        conn = psycopg2.connect(**db_config)
        conn.set_client_encoding('UTF8')
        cursor = conn.cursor()

        print(f"🔌 连接用户: {db_config['user']}")
        print(f"📊 数据库: {db_config['database']}\n")

        # 检查当前用户
        cursor.execute("SELECT current_user, current_database();")
        current_user, current_db = cursor.fetchone()
        print(f"当前用户: {current_user}")
        print(f"当前数据库: {current_db}\n")

        # 检查memories表的所有者
        cursor.execute("""
            SELECT tablename, tableowner 
            FROM pg_tables 
            WHERE tablename = 'memories';
        """)
        result = cursor.fetchone()
        if result:
            table_name, owner = result
            print(f"📋 表 '{table_name}' 的所有者: {owner}")

            if owner != current_user:
                print(f"\n⚠️  权限问题:")
                print(f"  当前用户 '{current_user}' 不是表所有者")
                print(f"  表所有者是 '{owner}'")
                print(f"\n💡 解决方案:")
                print(f"  1. 使用 '{owner}' 用户执行迁移")
                print(f"  2. 或将表所有权转移给 '{current_user}':")
                print(f"     ALTER TABLE memories OWNER TO {current_user};")

        # 检查当前用户的权限
        print(f"\n🔑 用户 '{current_user}' 的权限:")
        cursor.execute("""
            SELECT has_table_privilege(%s, 'memories', 'SELECT'),
                   has_table_privilege(%s, 'memories', 'INSERT'),
                   has_table_privilege(%s, 'memories', 'UPDATE'),
                   has_table_privilege(%s, 'memories', 'DELETE');
        """, (current_user, current_user, current_user, current_user))

        can_select, can_insert, can_update, can_delete = cursor.fetchone()
        print(f"  SELECT: {'✓' if can_select else '✗'}")
        print(f"  INSERT: {'✓' if can_insert else '✗'}")
        print(f"  UPDATE: {'✓' if can_update else '✗'}")
        print(f"  DELETE: {'✓' if can_delete else '✗'}")

        # 检查表结构
        print(f"\n📊 memories 表当前字段:")
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'memories'
            ORDER BY ordinal_position;
        """)

        for col_name, data_type in cursor.fetchall():
            mark = "✓" if col_name in [
                'importance_score', 'access_count', 'last_accessed_at', 'is_archived'] else " "
            print(f"  {mark} {col_name}: {data_type}")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"❌ 错误: {e}")
        sys.exit(1)


if __name__ == '__main__':
    check_permissions()
