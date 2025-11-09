"""
测试提醒系统数据库和基本功能
"""
from reminder_manager import get_reminder_manager, ReminderType
import asyncio
import sys
import os
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


async def test_reminder_system():
    """测试提醒系统"""
    print("=" * 60)
    print("🧪 测试主动提醒系统")
    print("=" * 60)

    manager = get_reminder_manager()
    user_id = "test_user"

    # 测试1: 创建时间提醒
    print("\n📝 测试1: 创建时间提醒")
    try:
        tomorrow = datetime.now() + timedelta(days=1)
        reminder1 = await manager.create_reminder(
            user_id=user_id,
            reminder_type=ReminderType.TIME,
            trigger_condition={
                "datetime": tomorrow.strftime("%Y-%m-%d 09:00:00")
            },
            content="明天早上9点的会议，记得准时参加哦！",
            title="会议提醒",
            priority=1,
            repeat=False
        )
        print(
            f"✅ 创建成功: ID={reminder1['reminder_id']}, 标题={reminder1['title']}")
    except Exception as e:
        print(f"❌ 创建失败: {e}")
        return False

    # 测试2: 创建行为提醒
    print("\n📝 测试2: 创建行为提醒")
    try:
        reminder2 = await manager.create_reminder(
            user_id=user_id,
            reminder_type=ReminderType.BEHAVIOR,
            trigger_condition={
                "inactive_hours": 2  # 2小时未活跃就提醒
            },
            content="好久不见，最近还好吗？",
            title="长时间未聊天",
            priority=3,
            repeat=True,
            repeat_interval=7200  # 2小时重复一次
        )
        print(
            f"✅ 创建成功: ID={reminder2['reminder_id']}, 类型={reminder2['reminder_type']}")
    except Exception as e:
        print(f"❌ 创建失败: {e}")
        return False

    # 测试3: 创建天气提醒
    print("\n📝 测试3: 创建天气提醒")
    try:
        reminder3 = await manager.create_reminder(
            user_id=user_id,
            reminder_type=ReminderType.WEATHER,
            trigger_condition={
                "condition": "rain",
                "location": "天水"
            },
            content="今天可能会下雨，记得带伞！",
            title="下雨提醒",
            priority=2,
            repeat=False
        )
        print(f"✅ 创建成功: ID={reminder3['reminder_id']}")
    except Exception as e:
        print(f"❌ 创建失败: {e}")
        return False

    # 测试4: 查询用户提醒
    print("\n📝 测试4: 查询用户提醒")
    try:
        reminders = await manager.get_user_reminders(user_id)
        print(f"✅ 查询成功: 共{len(reminders)}条提醒")
        for r in reminders:
            print(
                f"   - [{r['reminder_type']}] {r['title']}: {r['content'][:30]}...")
    except Exception as e:
        print(f"❌ 查询失败: {e}")
        return False

    # 测试5: 检查时间提醒（创建一个已过期的）
    print("\n📝 测试5: 检查时间提醒触发")
    try:
        # 创建一个1秒前的提醒
        past_time = datetime.now() - timedelta(seconds=1)
        reminder_expired = await manager.create_reminder(
            user_id=user_id,
            reminder_type=ReminderType.TIME,
            trigger_condition={
                "datetime": past_time.strftime("%Y-%m-%d %H:%M:%S")
            },
            content="这是一个测试触发的提醒",
            title="测试触发",
            priority=1
        )
        print(f"✅ 创建已过期提醒: ID={reminder_expired['reminder_id']}")

        # 检查触发
        triggered = await manager.check_time_reminders(user_id)
        print(f"✅ 检测到{len(triggered)}个需要触发的提醒")

        if triggered:
            # 触发第一个
            success = await manager.trigger_reminder(triggered[0]['reminder_id'])
            if success:
                print(f"✅ 触发成功: {triggered[0]['title']}")
            else:
                print(f"❌ 触发失败")
    except Exception as e:
        print(f"❌ 测试触发失败: {e}")
        return False

    # 测试6: 更新提醒
    print("\n📝 测试6: 更新提醒")
    try:
        success = await manager.update_reminder(
            reminder1['reminder_id'],
            content="会议时间改为10点了",
            priority=1
        )
        if success:
            print(f"✅ 更新成功")
        else:
            print(f"❌ 更新失败")
    except Exception as e:
        print(f"❌ 更新失败: {e}")
        return False

    # 测试7: 查询提醒历史
    print("\n📝 测试7: 查询提醒历史")
    try:
        history = await manager.get_reminder_history(user_id, limit=10)
        print(f"✅ 查询成功: 共{len(history)}条历史记录")
        for h in history:
            print(f"   - {h['triggered_at']}: {h['content'][:30]}...")
    except Exception as e:
        print(f"❌ 查询历史失败: {e}")
        return False

    # 测试8: 删除提醒
    print("\n📝 测试8: 删除测试提醒")
    try:
        # 删除所有测试提醒
        all_reminders = await manager.get_user_reminders(user_id, enabled_only=False)
        deleted_count = 0
        for r in all_reminders:
            success = await manager.delete_reminder(r['reminder_id'])
            if success:
                deleted_count += 1
        print(f"✅ 删除成功: {deleted_count}条提醒")
    except Exception as e:
        print(f"❌ 删除失败: {e}")
        return False

    print("\n" + "=" * 60)
    print("✅ 所有测试通过！")
    print("=" * 60)
    return True


if __name__ == "__main__":
    try:
        result = asyncio.run(test_reminder_system())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n测试中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
