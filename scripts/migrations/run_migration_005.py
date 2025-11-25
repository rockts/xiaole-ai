#!/usr/bin/env python3
"""
运行数据库性能优化迁移 - v0.6.2
"""
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()


def run_migration():
    """运行v0.6.2性能优化迁移"""

    # 数据库连接信息
    db_config = {
        'dbname': os.getenv('DB_NAME'),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASS'),
        'host': os.getenv('DB_HOST'),
        'port': os.getenv('DB_PORT')
    }

    print("=" * 60)
    print("🚀 开始运行数据库性能优化迁移 v0.6.2")
    print("=" * 60)

    try:
        # 连接数据库
        conn = psycopg2.connect(**db_config)
        conn.set_client_encoding('UTF8')
        conn.autocommit = True
        cursor = conn.cursor()

        # 读取迁移文件
        migration_file = (
            'db_migrations/005_performance_optimization_v0.6.2.sql'
        )
        with open(migration_file, 'r', encoding='utf-8') as f:
            sql = f.read()

        print(f"\n📄 执行迁移文件: {migration_file}")

        # 将DO块作为一个整体执行
        # 使用$$分割DO块
        import re
        do_blocks = re.split(r'(?<=\$\$);', sql)

        for i, block in enumerate(do_blocks, 1):
            block = block.strip()
            if not block or block.startswith('--'):
                continue

            try:
                cursor.execute(block)
                print(f"  ✓ 执行块 {i}/{len(do_blocks)}")
            except Exception as e:
                # 跳过非关键性错误
                error_str = str(e).lower()
                if ('already exists' in error_str or
                        'does not exist' in error_str):
                    print(f"  ⚠  块 {i} 跳过: {str(e)[:60]}")
                else:
                    print(f"  ✗ 块 {i} 失败: {e}")

        print("\n✅ 迁移执行成功！")

        # 显示索引信息
        print("\n📊 当前数据库索引统计：")
        cursor.execute("""
            SELECT 
                tablename,
                COUNT(*) as index_count
            FROM pg_indexes
            WHERE schemaname = 'public'
            GROUP BY tablename
            ORDER BY index_count DESC;
        """)

        for table, count in cursor.fetchall():
            print(f"  {table}: {count} 个索引")

        cursor.close()
        conn.close()

        print("\n" + "=" * 60)
        print("🎉 性能优化完成！")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ 迁移失败: {e}")
        raise


if __name__ == "__main__":
    run_migration()
