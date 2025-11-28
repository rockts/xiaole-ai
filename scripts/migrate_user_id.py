#!/usr/bin/env python3
"""
将历史会话从 default_user 迁移到 admin
确保用户登录后能看到所有历史会话
"""
from backend.db_setup import SessionLocal, Conversation
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))


def migrate_user_sessions():
    """将 default_user 的会话迁移到 admin"""
    session = SessionLocal()
    try:
        # 查询所有 default_user 的会话
        old_sessions = session.query(Conversation).filter(
            Conversation.user_id == 'default_user'
        ).all()

        print(f'📊 找到 {len(old_sessions)} 条 default_user 会话')

        if not old_sessions:
            print('✅ 无需迁移')
            return

        # 询问确认
        confirm = input(f'确认将这些会话迁移到 admin 用户? (yes/no): ')
        if confirm.lower() != 'yes':
            print('❌ 取消迁移')
            return

        # 执行迁移
        for conv in old_sessions:
            conv.user_id = 'admin'

        session.commit()
        print(f'✅ 成功迁移 {len(old_sessions)} 条会话到 admin')

    except Exception as e:
        session.rollback()
        print(f'❌ 迁移失败: {e}')
        raise
    finally:
        session.close()


if __name__ == '__main__':
    migrate_user_sessions()
