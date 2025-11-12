#!/usr/bin/env python3
"""
执行数据库迁移：007_create_documents_table.sql
创建文档表用于长文本总结功能
"""

import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()


def run_migration():
    """执行数据库迁移"""
    # 数据库连接配置
    db_config = {
        'host': os.getenv('DB_HOST'),
        'port': os.getenv('DB_PORT', 5432),
        'database': os.getenv('DB_NAME'),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASS')  # 注意是DB_PASS不是DB_PASSWORD
    }

    print("🔧 开始执行迁移...")
    print(
        f"📦 数据库: {db_config['host']}:{db_config['port']}/{db_config['database']}")

    try:
        # 连接数据库（指定UTF-8编码）
        conn = psycopg2.connect(**db_config, client_encoding='utf8')
        cur = conn.cursor()

        # 读取SQL文件
        sql_file = 'db_migrations/007_create_documents_table.sql'
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql = f.read()

        # 分批执行SQL（按DO块和语句分隔）
        print("📝 执行SQL语句...")
        statements = []
        current_stmt = []
        in_do_block = False

        for line in sql.split('\n'):
            line_stripped = line.strip()

            # 跳过注释和空行
            if line_stripped.startswith('--') or not line_stripped:
                continue

            current_stmt.append(line)

            # 检测DO块
            if 'DO $$' in line:
                in_do_block = True
            elif in_do_block and 'END $$;' in line:
                in_do_block = False
                statements.append('\n'.join(current_stmt))
                current_stmt = []
            # 普通语句以分号结尾
            elif not in_do_block and line_stripped.endswith(';'):
                statements.append('\n'.join(current_stmt))
                current_stmt = []

        # 执行每条语句
        for i, stmt in enumerate(statements, 1):
            if stmt.strip():
                try:
                    print(f"  [{i}/{len(statements)}] 执行中...")
                    cur.execute(stmt)
                    conn.commit()
                except Exception as e:
                    print(f"  ⚠️ 语句 {i} 执行失败（忽略）: {e}")
                    conn.rollback()

        # 验证表是否创建成功
        cur.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'documents'
            ORDER BY ordinal_position;
        """)
        columns = cur.fetchall()

        print("\n✅ 迁移完成！")
        print(f"\n📊 documents 表结构 ({len(columns)} 列):")
        for col_name, col_type in columns:
            print(f"  - {col_name}: {col_type}")

        # 查询索引
        cur.execute("""
            SELECT indexname 
            FROM pg_indexes 
            WHERE tablename = 'documents';
        """)
        indexes = cur.fetchall()
        print(f"\n📑 索引数量: {len(indexes)}")
        for idx in indexes:
            print(f"  - {idx[0]}")

        cur.close()
        conn.close()

    except Exception as e:
        print(f"\n❌ 迁移失败: {e}")
        raise


if __name__ == "__main__":
    run_migration()
