import requests
from datetime import datetime, timedelta

BASE_URL = "http://127.0.0.1:8000"


def create_reminder(content, priority, enabled=True, time_offset_minutes=10):
    url = f"{BASE_URL}/api/reminders"

    trigger_time = datetime.now() + timedelta(minutes=time_offset_minutes)

    data = {
        "user_id": "default_user",
        "reminder_type": "time",
        "trigger_condition": {
            "datetime": trigger_time.strftime("%Y-%m-%d %H:%M:%S")
        },
        "content": content,
        "title": f"测试提醒 - {content}",
        "priority": priority,
        "repeat": False
    }

    response = requests.post(url, json=data)
    if response.status_code == 200:
        result = response.json()
        if result.get("success"):
            reminder = result["reminder"]
            print(f"✅ Created reminder: {content} "
                  f"(ID: {reminder['reminder_id']})")

            # If we want it disabled, we need to toggle it
            if not enabled:
                toggle_url = (
                    f"{BASE_URL}/api/reminders/"
                    f"{reminder['reminder_id']}/toggle"
                )
                requests.post(toggle_url)
                print(f"  -> Disabled reminder: {content}")

            return reminder
    else:
        print(f"❌ Failed to create reminder: {content}")
        print(response.text)
        return None


def main():
    print("🚀 Starting to populate test reminders...")

    # 1. High Priority Active (Should be at top)
    create_reminder(
        "高优先级待办 (Priority 1)",
        priority=1,
        enabled=True,
        time_offset_minutes=30
    )

    # 2. Medium Priority Active
    create_reminder(
        "中优先级待办 (Priority 3)",
        priority=3,
        enabled=True,
        time_offset_minutes=60
    )

    # 3. Low Priority Active
    create_reminder(
        "低优先级待办 (Priority 5)",
        priority=5,
        enabled=True,
        time_offset_minutes=120
    )

    # 4. Disabled Reminder (Should be at bottom)
    create_reminder(
        "已禁用提醒 (Disabled)",
        priority=2,
        enabled=False,
        time_offset_minutes=10
    )

    print("\n✨ Test data populated! Please check the frontend UI.")
    print("Expected Order:")
    print("1. 高优先级待办")
    print("2. 中优先级待办")
    print("3. 低优先级待办")
    print("4. 已禁用提醒")


if __name__ == "__main__":
    main()
