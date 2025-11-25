#!/usr/bin/env python3
"""使用postgres超级用户执行数据库迁移"""
from dotenv import load_dotenv
import os
import sys
from pathlib import Path
import psycopg2
import getpass

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

load_dotenv()


def run_migration_as_postgres():
    """使用postgres用户执行迁移"""
    # 使用postgres超级用户
    print("🔐 需要PostgreSQL超级用户权限来执行迁移")
    postgres_password = getpass.getpass("请输入postgres用户密码: ")

    db_config = {
        'host': os.getenv('DB_HOST', '192.168.88.188'),
        'port': int(os.getenv('DB_PORT', 5432)),
        'user': 'postgres',  # 使用postgres超级用户
        'password': postgres_password,
        'database': os.getenv('DB_NAME', 'xiaole_ai')
    }

    # 读取迁移脚本
    migration_file = (project_root / 'db_migrations' /
                      '003_add_memory_importance_fields.sql')
    print(f"\n📖 读取迁移文件: {migration_file}")

    with open(migration_file, 'r', encoding='utf-8') as f:
        sql_script = f.read()

    # 连接数据库并执行
    print(f"🔌 连接数据库: {db_config['host']}:{db_config['port']}/")
    print(f"   {db_config['database']} (用户: {db_config['user']})")

    try:
        conn = psycopg2.connect(**db_config)
        conn.autocommit = True
        conn.set_client_encoding('UTF8')
        cursor = conn.cursor()

        print("\n⚙️  执行迁移脚本...")

        # 解析并执行SQL语句
        statements = []
        current_statement = []
        in_do_block = False

        for line in sql_script.split('\n'):
            line_stripped = line.strip()
            if not line_stripped:
                continue
            if line_stripped.startswith('--') and not in_do_block:
                continue
            if 'DO $$' in line_stripped or 'DO $' in line_stripped:
                in_do_block = True

            current_statement.append(line)

            if in_do_block and ('$$;' in line_stripped or '$;' in line_stripped):
                in_do_block = False
                statements.append('\n'.join(current_statement))
                current_statement = []
            elif not in_do_block and line_stripped.endswith(';'):
                statements.append('\n'.join(current_statement))
                current_statement = []

        # 执行每条语句
        for i, stmt in enumerate(statements, 1):
            stmt = stmt.strip()
            if stmt and not stmt.startswith('--'):
                # 只显示语句的第一行作为提示
                first_line = stmt.split('\n')[0][:60]
                print(f"  [{i}/{len(statements)}] {first_line}...")
                try:
                    cursor.execute(stmt)
                    print(f"      ✓ 成功")
                except Exception as e:
                    print(f"      ✗ 失败: {e}")
                    raise

        print("\n✅ 迁移成功！")
        print("\n📋 验证新字段:")

        # 验证表结构
        cursor.execute("""
            SELECT column_name, data_type, column_default
            FROM information_schema.columns
            WHERE table_name = 'memories'
            AND column_name IN (
                'importance_score',
                'access_count',
                'last_accessed_at',
                'is_archived'
            )
            ORDER BY ordinal_position;
        """)

        results = cursor.fetchall()
        if results:
            for col_name, data_type, default_val in results:
                default_str = str(default_val)[:40] if default_val else 'NULL'
                print(f"  ✓ {col_name}: {data_type} (默认: {default_str})")
        else:
            print("  ⚠️  未找到新字段！")

        # 将表所有权转给xiaole_user
        app_user = os.getenv('DB_USER', 'xiaole_user')
        print(f"\n🔄 将表所有权转移给应用用户 '{app_user}'...")

        cursor.execute(f"ALTER TABLE memories OWNER TO {app_user};")
        cursor.execute(f"ALTER TABLE conversations OWNER TO {app_user};")
        cursor.execute(f"ALTER TABLE proactive_qa OWNER TO {app_user};")
        cursor.execute(f"ALTER TABLE behavior_analytics OWNER TO {app_user};")
        cursor.execute(f"ALTER TABLE pattern_learning OWNER TO {app_user};")

        print("  ✓ 所有权转移完成")

        cursor.close()
        conn.close()
        print("\n🎉 数据库迁移完成！可以重启服务器了")

    except psycopg2.OperationalError as e:
        print(f"\n❌ 连接失败: {e}")
        print("\n💡 提示:")
        print("  1. 确认postgres用户密码正确")
        print("  2. 确认PostgreSQL允许postgres用户远程连接")
        print("  3. 检查 pg_hba.conf 配置")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 迁移失败: {e}")
        sys.exit(1)


if __name__ == '__main__':
    run_migration_as_postgres()
