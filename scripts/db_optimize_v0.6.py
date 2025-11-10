#!/usr/bin/env python3
"""
执行数据库优化迁移 - v0.6.0

添加索引以提升常用查询性能
"""
import psycopg2
import os
from dotenv import load_dotenv
import time

load_dotenv()


def main():
    print("=" * 70)
    print("🗄️  数据库性能优化 - v0.6.0")
    print("=" * 70)

    # 连接数据库
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", 5432)),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS")
    )

    cursor = conn.cursor()

    try:
        # 读取迁移SQL
        sql_file = os.path.join(
            os.path.dirname(__file__),
            "..",
            "db_migrations",
            "002_add_indexes_v0.6.0.sql"
        )

        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()

        # 按语句分割（跳过注释）
        statements = []
        for stmt in sql_content.split(';'):
            stmt = stmt.strip()
            if stmt and not stmt.startswith('--'):
                statements.append(stmt)

        print(f"\n📝 准备执行 {len(statements)} 条SQL语句...\n")

        # 执行每条语句
        success_count = 0
        for i, stmt in enumerate(statements, 1):
            try:
                start_time = time.time()
                cursor.execute(stmt)
                duration = time.time() - start_time

                # 提取索引名称
                if 'CREATE INDEX' in stmt:
                    index_name = stmt.split('idx_')[1].split()[0]
                    print(
                        f"  ✅ [{i}/{len(statements)}] "
                        f"创建索引: idx_{index_name} ({duration:.2f}s)"
                    )
                elif 'SELECT' in stmt:
                    print(f"  📊 [{i}/{len(statements)}] 验证索引...")
                else:
                    print(
                        f"  ✅ [{i}/{len(statements)}] "
                        f"执行完成 ({duration:.2f}s)"
                    )

                success_count += 1
            except psycopg2.Error as e:
                print(f"  ⚠️  [{i}/{len(statements)}] 跳过: {e.pgerror}")

        # 提交更改
        conn.commit()

        print(f"\n✅ 成功执行 {success_count}/{len(statements)} 条语句")

        # 显示当前索引
        print("\n" + "=" * 70)
        print("📊 当前索引列表")
        print("=" * 70)

        cursor.execute("""
            SELECT
                tablename,
                indexname
            FROM pg_indexes
            WHERE schemaname = 'public'
            AND indexname LIKE 'idx_%'
            ORDER BY tablename, indexname;
        """)

        current_table = None
        for table, index in cursor.fetchall():
            if table != current_table:
                print(f"\n📁 {table}:")
                current_table = table
            print(f"  - {index}")

        print("\n" + "=" * 70)
        print("✅ 数据库优化完成！")
        print("=" * 70)

    except Exception as e:
        conn.rollback()
        print(f"\n❌ 错误: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    main()
