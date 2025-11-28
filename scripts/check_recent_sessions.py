#!/usr/bin/env python3
"""检查最近创建的会话"""

import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.db_setup import Session, Conversation
from sqlalchemy import desc

def main():
    session = Session()
    try:
        # 获取最近10条会话
        recent = session.query(Conversation).order_by(
            desc(Conversation.updated_at)
        ).limit(10).all()
        
        print('📋 最近10条会话 (按更新时间倒序):')
        print('=' * 80)
        
        for i, conv in enumerate(recent, 1):
            print(f'\n{i}. 标题: {conv.title}')
            print(f'   Session ID: {conv.session_id}')
            print(f'   用户: {conv.user_id}')
            print(f'   创建时间: {conv.created_at}')
            print(f'   更新时间: {conv.updated_at}')
        
        total = session.query(Conversation).count()
        print(f'\n{"=" * 80}')
        print(f'✅ 数据库中总共有 {total} 条会话\n')
        
    except Exception as e:
        print(f'❌ 查询失败: {e}')
    finally:
        session.close()

if __name__ == '__main__':
    main()
