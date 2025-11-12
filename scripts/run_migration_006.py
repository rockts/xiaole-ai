#!/usr/bin/env python3
"""
运行数据库迁移 - 005_performance_optimization_v0.6.2
"""
import psycopg2
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

load_dotenv()


def main():
    """运行迁移"""
    print("=" * 60)
    print("数据库性能优化迁移 - v0.6.2")
    print("=" * 60)

    # 连接数据库
    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST'),
            port=os.getenv('DB_PORT'),
            database=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASS')
        )
        conn.autocommit = True
        print("✅ 数据库连接成功\n")
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return 1

    # 读取SQL文件
    sql_file = project_root / 'db_migrations' / \
        '005_performance_optimization_v0.6.2.sql'
    try:
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        print(f"✅ 读取SQL文件: {sql_file.name}\n")
    except Exception as e:
        print(f"❌ 读取SQL文件失败: {e}")
        conn.close()
        return 1

    # 分割SQL语句（按DO块）
    sql_blocks = []
    current_block = []
    in_do_block = False

    for line in sql_content.split('\n'):
        line_stripped = line.strip()

        # 跳过注释和空行（在块外）
        if not in_do_block and (line_stripped.startswith('--') or not line_stripped):
            continue

        # 检测DO块开始
        if 'DO $$' in line or line_stripped == 'DO':
            in_do_block = True
            current_block = [line]
        elif in_do_block:
            current_block.append(line)
            # 检测DO块结束
            if '$$;' in line:
                sql_blocks.append('\n'.join(current_block))
                current_block = []
                in_do_block = False
        else:
            # 独立的SQL语句（VACUUM等）
            if line_stripped and not line_stripped.startswith('--'):
                if ';' in line:
                    current_block.append(line)
                    sql_blocks.append('\n'.join(current_block))
                    current_block = []
                elif line_stripped:
                    current_block.append(line)

    # 执行每个SQL块
    cursor = conn.cursor()
    success_count = 0
    skip_count = 0
    vacuum_done = False

    print("开始执行SQL语句...\n")

    for i, sql_block in enumerate(sql_blocks, 1):
        sql_stripped = sql_block.strip()
        if not sql_stripped:
            continue

        # 显示执行的SQL类型
        if 'DO $$' in sql_stripped:
            block_desc = "索引创建块"
        elif 'VACUUM' in sql_stripped.upper():
            block_desc = "数据库维护（VACUUM）"
            if vacuum_done:  # 跳过重复的VACUUM
                continue
            vacuum_done = True
        elif 'SELECT' in sql_stripped.upper():
            block_desc = "查询（仅查看，不执行）"
            skip_count += 1
            continue
        else:
            block_desc = "SQL语句"

        try:
            print(f"执行 #{i}: {block_desc}")
            cursor.execute(sql_block)
            success_count += 1
            print("  ✅ 成功\n")
        except Exception as e:
            error_msg = str(e)
            if 'already exists' in error_msg:
                print(f"  ⚠️  已存在，跳过\n")
            else:
                print(f"  ❌ 失败: {error_msg[:150]}\n")

    cursor.close()
    conn.close()

    print("=" * 60)
    print(f"迁移完成！")
    print(f"  ✅ 成功执行: {success_count} 个语句")
    print(f"  ⚠️  跳过: {skip_count} 个查询")
    print("=" * 60)

    return 0


if __name__ == '__main__':
    exit(main())
