#!/usr/bin/env python3
"""最终配置验证脚本"""
import sys
import psycopg2
from datetime import datetime

print("=" * 60)
print("🔍 NAS PostgreSQL 配置验证")
print("=" * 60)

# 数据库配置
config = {
    'host': '192.168.88.188',
    'port': 5432,
    'database': 'xiaole_ai',
    'user': 'xiaole_user',
    'password': 'Xiaole2025User'
}

print(f"\n📡 连接信息:")
print(f"   主机: {config['host']}:{config['port']}")
print(f"   数据库: {config['database']}")
print(f"   用户: {config['user']}")

try:
    # 测试连接
    print("\n🔌 测试连接...")
    conn = psycopg2.connect(**config, connect_timeout=5)
    print("   ✅ 连接成功")

    cur = conn.cursor()

    # 测试写入
    print("\n📝 测试写入数据...")
    test_content = f"配置验证 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    cur.execute(
        "INSERT INTO memories (content, tag, created_at) VALUES (%s, %s, %s) RETURNING id",
        (test_content, 'config_test', datetime.now())
    )
    inserted_id = cur.fetchone()[0]
    conn.commit()
    print(f"   ✅ 写入成功 (ID: {inserted_id})")

    # 测试读取
    print("\n📖 测试读取数据...")
    cur.execute(
        "SELECT id, content, tag, created_at FROM memories ORDER BY created_at DESC LIMIT 3"
    )
    rows = cur.fetchall()
    print(f"   ✅ 读取成功，找到 {len(rows)} 条记录:")
    for row in rows:
        print(f"      [{row[0]}] {row[2]}: {row[1][:30]}... ({row[3]})")

    # 统计信息
    print("\n📊 数据库统计:")
    cur.execute("SELECT COUNT(*) FROM memories")
    total = cur.fetchone()[0]
    print(f"   总记录数: {total}")

    cur.execute(
        "SELECT tag, COUNT(*) FROM memories GROUP BY tag ORDER BY COUNT(*) DESC")
    tags = cur.fetchall()
    print(f"   标签分布:")
    for tag, count in tags:
        print(f"      - {tag}: {count} 条")

    # 清理
    cur.close()
    conn.close()

    print("\n" + "=" * 60)
    print("🎉 所有测试通过！NAS PostgreSQL 配置成功！")
    print("=" * 60)
    print("\n✅ xiaole-ai 现在可以使用 NAS 数据库了")
    print("✅ 数据持久化到 192.168.88.188")
    print("✅ 支持多设备访问")
    print("\n💡 下一步:")
    print("   1. 启动服务: uvicorn main:app --reload")
    print("   2. 测试 API: curl http://localhost:8000/memory?tag=test")
    print("   3. 迁移旧数据: 从 SQLite 导入到 NAS PostgreSQL")

    sys.exit(0)

except psycopg2.OperationalError as e:
    print(f"\n❌ 连接失败: {e}")
    print("\n可能的原因:")
    print("   1. NAS PostgreSQL 服务未启动")
    print("   2. 防火墙阻止了 5432 端口")
    print("   3. pg_hba.conf 配置不正确")
    print("   4. listen_addresses 未设置为 '*'")
    sys.exit(1)

except Exception as e:
    print(f"\n❌ 错误: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
