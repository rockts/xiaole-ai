#!/usr/bin/env python3
"""
修复历史图片路径
从memory表的tag中提取图片文件名，匹配到messages表中
"""
import psycopg2
import os
from dotenv import load_dotenv
import re

load_dotenv()


def fix_historical_images():
    """修复历史消息中的图片路径"""
    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST'),
            port=int(os.getenv('DB_PORT', 5432)),
            database=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASS'),
            client_encoding='UTF8'
        )
        cursor = conn.cursor()

        print('🔍 查找带图片标签的记忆记录...')

        # 查找所有image:开头的记忆
        cursor.execute("""
            SELECT id, content, tag, created_at
            FROM memories
            WHERE tag LIKE 'image:%'
            ORDER BY created_at DESC
        """)

        image_memories = cursor.fetchall()
        print(f'📊 找到 {len(image_memories)} 条图片记忆记录')

        if not image_memories:
            print('✅ 没有需要修复的历史图片')
            cursor.close()
            conn.close()
            return

        updated_count = 0

        for memory_id, content, tag, created_at in image_memories:
            # 从tag中提取文件名: image:20251113_202028_IMG_0034.jpeg
            match = re.match(r'image:(.+)', tag)
            if not match:
                continue

            filename = match.group(1)
            print(f'\n📷 处理图片: {filename}')
            print(f'   时间: {created_at}')
            print(f'   内容预览: {content[:80]}...')

            # 在uploads目录中查找匹配的文件
            uploads_dir = '/Users/rockts/Dev/xiaole-ai/uploads'
            possible_paths = []

            # 尝试不同的路径格式
            for root, dirs, files in os.walk(uploads_dir):
                for file in files:
                    if file == filename:
                        rel_path = os.path.relpath(
                            os.path.join(root, file),
                            '/Users/rockts/Dev/xiaole-ai'
                        )
                        possible_paths.append(rel_path)

            if not possible_paths:
                print(f'   ⚠️ 文件未找到: {filename}')
                continue

            image_path = possible_paths[0]
            print(f'   ✓ 找到文件: {image_path}')

            # 在messages表中查找包含这个图片内容的消息
            # 通常图片识别结果会在同一时间段内保存
            cursor.execute("""
                SELECT id, session_id, role, content, created_at
                FROM messages
                WHERE content LIKE %s
                AND created_at >= %s::timestamp - interval '5 minutes'
                AND created_at <= %s::timestamp + interval '5 minutes'
                AND role = 'user'
                AND image_path IS NULL
                ORDER BY ABS(EXTRACT(EPOCH FROM (created_at - %s::timestamp)))
                LIMIT 1
            """, (f'%{content[:50]}%', created_at, created_at, created_at))

            result = cursor.fetchone()

            if result:
                msg_id, session_id, role, msg_content, created_at = result
                print(f'   ✓ 找到匹配的消息 (ID: {msg_id})')
                print(f'   会话: {session_id}')
                print(f'   时间: {created_at}')

                # 更新消息的image_path
                cursor.execute("""
                    UPDATE messages
                    SET image_path = %s
                    WHERE id = %s
                """, (image_path, msg_id))

                updated_count += 1
                print(f'   ✅ 已更新 image_path')
            else:
                # 如果找不到匹配的消息，尝试查找时间最近的用户消息
                cursor.execute("""
                    SELECT id, session_id, created_at
                    FROM messages
                    WHERE created_at >= %s::timestamp - interval '10 minutes'
                    AND created_at <= %s::timestamp + interval '10 minutes'
                    AND role = 'user'
                    AND image_path IS NULL
                    AND LENGTH(content) < 200
                    ORDER BY ABS(EXTRACT(EPOCH FROM (created_at - %s::timestamp)))
                    LIMIT 1
                """, (created_at, created_at, created_at))

                fallback = cursor.fetchone()
                if fallback:
                    msg_id, session_id, created_at = fallback
                    print(f'   ⚠️ 使用时间匹配 (ID: {msg_id})')
                    print(f'   会话: {session_id}')
                    print(
                        f'   时间差: {abs((created_at - created_at).total_seconds())}秒')

                    cursor.execute("""
                        UPDATE messages
                        SET image_path = %s
                        WHERE id = %s
                    """, (image_path, msg_id))

                    updated_count += 1
                    print(f'   ✅ 已更新 image_path (时间匹配)')
                else:
                    print(f'   ❌ 找不到匹配的消息')

        conn.commit()
        print(f'\n🎉 修复完成！')
        print(f'   更新了 {updated_count} 条消息记录')

        cursor.close()
        conn.close()

    except Exception as e:
        print(f'❌ 修复失败: {e}')
        if conn:
            conn.rollback()
        raise


if __name__ == '__main__':
    print('='*60)
    print('修复历史图片路径工具')
    print('='*60)
    fix_historical_images()
