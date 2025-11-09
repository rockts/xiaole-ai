"""
初始化提醒系统数据库表
"""
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()


def init_reminder_tables():
    """创建提醒系统所需的数据库表"""
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST', '192.168.88.188'),
        port=os.getenv('DB_PORT', '5432'),
        database=os.getenv('DB_NAME', 'xiaole_ai'),
        user=os.getenv('DB_USER', 'xiaole_user'),
        password=os.getenv('DB_PASS', 'Xiaole2025User'),
        client_encoding='UTF8'
    )

    try:
        with conn.cursor() as cur:
            # 读取SQL文件
            sql_file = 'db_migrations/001_create_reminders_tables.sql'
            with open(sql_file, 'r', encoding='utf-8') as f:
                sql = f.read()

            # 分步执行SQL（每条语句单独执行）
            statements = sql.split(';')
            for stmt in statements:
                stmt = stmt.strip()
                if stmt and not stmt.startswith('--'):
                    try:
                        cur.execute(stmt)
                        conn.commit()
                    except psycopg2.Error as e:
                        # 表或索引可能已存在，忽略错误
                        if 'already exists' in str(e):
                            print(f"已存在: {stmt[:40]}...")
                            conn.rollback()
                        else:
                            print(f"执行失败: {stmt[:50]}...")
                            print(f"错误: {e}")
                            conn.rollback()

            print("✅ 提醒系统数据库表创建成功！")

            # 检查表
            cur.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema='public' AND table_name LIKE 'reminder%'
                ORDER BY table_name
            """)
            tables = cur.fetchall()
            print("\n📊 创建的表：")
            for table in tables:
                print(f"   - {table[0]}")

            # 检查示例数据
            cur.execute("SELECT COUNT(*) FROM reminders")
            count = cur.fetchone()[0]
            print(f"\n📝 提醒记录数: {count}")

    except Exception as e:
        conn.rollback()
        print(f"❌ 创建失败: {e}")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    init_reminder_tables()
