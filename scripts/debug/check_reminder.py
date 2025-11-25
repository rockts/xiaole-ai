"""检查提醒数据"""
import json
from backend.reminder_manager import get_reminder_manager
import asyncio
import sys
sys.path.insert(0, '/Users/rockts/Dev/xiaole-ai')
sys.path.insert(0, '/Users/rockts/Dev/xiaole-ai/backend')


async def main():
    mgr = get_reminder_manager()
    reminders = await mgr.get_user_reminders("default_user", enabled_only=True)

    print("\n=== 当前提醒列表 ===")
    for r in reminders:
        print(f"\nID: {r['reminder_id']}")
        print(f"内容: {r['content']}")
        print(f"类型: {r['reminder_type']}")
        print(f"启用: {r['enabled']}")

        trigger = r.get('trigger_condition')
        if isinstance(trigger, str):
            trigger = json.loads(trigger)
        print(f"触发条件: {json.dumps(trigger, ensure_ascii=False, indent=2)}")
        print(f"创建时间: {r['created_at']}")

if __name__ == "__main__":
    asyncio.run(main())
