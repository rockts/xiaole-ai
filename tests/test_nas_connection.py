#!/usr/bin/env python3
"""测试NAS PostgreSQL连接"""
import psycopg2
import sys

try:
    print("🔄 正在连接到 192.168.88.188:5432...")
    conn = psycopg2.connect(
        host='192.168.88.188',
        port=5432,
        database='xiaole_ai',
        user='xiaole_user',
        password='Xiaole2025User',
        connect_timeout=5
    )

    print("✅ 连接成功!")

    cur = conn.cursor()
    cur.execute('SELECT version()')
    version = cur.fetchone()[0]
    print(f"📊 PostgreSQL版本: {version}")

    # 测试表是否存在
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
    """)
    tables = cur.fetchall()
    print(f"\n📋 数据库中的表: {len(tables)}个")
    for table in tables:
        print(f"  - {table[0]}")

    cur.close()
    conn.close()
    print("\n✅ 测试完成!")
    sys.exit(0)

except psycopg2.OperationalError as e:
    print(f"❌ 连接失败: {e}")
    print("\n可能的原因:")
    print("  1. NAS防火墙阻止了5432端口")
    print("  2. PostgreSQL没有监听外部连接(check listen_addresses)")
    print("  3. pg_hba.conf配置未生效")
    sys.exit(1)

except Exception as e:
    print(f"❌ 错误: {e}")
    sys.exit(1)
