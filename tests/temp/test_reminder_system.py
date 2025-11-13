#!/usr/bin/env python3
"""
测试提醒系统
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import asyncio
from datetime import datetime, timedelta
from reminder_manager import get_reminder_manager
from scheduler import get_scheduler

async def test_reminder_system():
    """测试提醒系统"""
    print("=" * 60)
    print("提醒系统诊断")
    print("=" * 60)
    
    # 1. 检查scheduler状态
    scheduler = get_scheduler()
    print(f"\n1. Scheduler状态:")
    print(f"   运行中: {scheduler.is_running}")
    if scheduler.is_running:
        status = scheduler.get_status()
        print(f"   任务数: {status['total_jobs']}")
        for job in status['jobs']:
            print(f"   - {job['name']}: {job['next_run_time']}")
    else:
        print("   ⚠️ Scheduler未运行！")
    
    # 2. 检查提醒管理器
    reminder_mgr = get_reminder_manager()
    print(f"\n2. 提醒管理器:")
    print(f"   WebSocket回调: {'已设置' if reminder_mgr.websocket_callback else '未设置'}")
    
    # 3. 查询活跃提醒
    from db_setup import Reminder
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from dotenv import load_dotenv
    
    load_dotenv()
    
    if os.getenv('DATABASE_URL'):
        DB_URL = os.getenv('DATABASE_URL')
    else:
        DB_URL = (
            f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASS')}"
            f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}"
            f"/{os.getenv('DB_NAME')}"
        )
    
    engine = create_engine(DB_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # 查询所有活跃提醒
        now = datetime.now()
        active_reminders = session.query(Reminder).filter(
            Reminder.enabled == True,
            Reminder.triggered == False
        ).all()
        
        print(f"\n3. 活跃提醒: {len(active_reminders)}个")
        
        for reminder in active_reminders:
            print(f"\n   📌 提醒 #{reminder.id}")
            print(f"      标题: {reminder.title}")
            print(f"      类型: {reminder.trigger_type}")
            
            if reminder.trigger_type == 'time':
                trigger_time = reminder.trigger_condition.get('datetime')
                if trigger_time:
                    trigger_dt = datetime.fromisoformat(trigger_time)
                    if trigger_dt <= now:
                        print(f"      ⚠️ 已到期: {trigger_time}")
                        print(f"      差值: {now - trigger_dt}")
                    else:
                        print(f"      触发时间: {trigger_time}")
                        print(f"      剩余: {trigger_dt - now}")
            
            print(f"      优先级: {reminder.priority}")
            print(f"      已触发: {reminder.triggered}")
            print(f"      触发时间: {reminder.triggered_at}")
        
        # 4. 测试触发检查
        print(f"\n4. 测试触发检查:")
        triggered = await reminder_mgr.check_time_reminders("default_user")
        print(f"   应触发提醒: {len(triggered)}个")
        
        for r in triggered:
            print(f"   - #{r['reminder_id']}: {r.get('title', 'Untitled')}")
        
    finally:
        session.close()
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    asyncio.run(test_reminder_system())
