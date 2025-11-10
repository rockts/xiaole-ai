#!/usr/bin/env python3
"""执行数据库迁移脚本"""
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
    migration_file = project_root / 'db_migrations' / \
        '003_add_memory_importance_fields.sql'
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

        # 按分号分割，但保留DO块的完整性
        statements = []
        current_statement = []
        in_do_block = False

        for line in sql_script.split('\n'):
            line_stripped = line.strip()

            # 跳过空行
            if not line_stripped:
                continue

            # 跳过单行注释（但不在DO块内）
            if line_stripped.startswith('--') and not in_do_block:
                continue

            # 检测DO块开始
            if line_stripped.startswith('DO $$') or line_stripped.startswith('DO $'):
                in_do_block = True

            current_statement.append(line)

            # 检测DO块结束
            if in_do_block and (line_stripped.endswith('$$;') or line_stripped.endswith('$;')):
                in_do_block = False
                statements.append('\n'.join(current_statement))
                current_statement = []
            # 普通语句以分号结尾
            elif not in_do_block and line_stripped.endswith(';'):
                statements.append('\n'.join(current_statement))
                current_statement = []

        # 执行每条语句
        for i, stmt in enumerate(statements, 1):
            stmt = stmt.strip()
            if stmt and not stmt.startswith('--'):
                print(f"  执行语句 {i}/{len(statements)}...")
                try:
                    cursor.execute(stmt)
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
            WHERE table_name = 'memories'
            AND column_name IN ('importance_score', 'access_count', 'last_accessed_at', 'is_archived')
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
