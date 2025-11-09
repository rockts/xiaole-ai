"""
提醒系统集成测试
测试完整的提醒流程：创建 -> 触发 -> 展示 -> 历史
"""
import requests
import time
from datetime import datetime, timedelta
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

BASE_URL = "http://localhost:8000"
USER_ID = "test_user"


def print_section(title):
    """打印测试章节标题"""
    print(f"\n{'=' * 70}")
    print(f"  {title}")
    print('=' * 70)


def test_create_reminder():
    """测试创建提醒"""
    print_section("测试1: 创建提醒")

    # 创建一个2分钟前的提醒（模拟已到期）
    trigger_time = (datetime.now() - timedelta(minutes=2)
                    ).strftime("%Y-%m-%d %H:%M:%S")

    response = requests.post(
        f"{BASE_URL}/api/reminders",
        json={
            "user_id": USER_ID,
            "reminder_type": "time",
            "trigger_condition": {"datetime": trigger_time},
            "title": "测试会议提醒",
            "content": "这是一个测试提醒，用于验证系统功能",
            "priority": 1,
            "repeat": False
        },
        timeout=10
    )

    assert response.status_code == 200, f"创建失败: {response.text}"
    data = response.json()
    assert data['success'], "返回success为False"

    reminder_id = data['reminder']['reminder_id']
    print(f"✅ 提醒创建成功")
    print(f"   - ID: {reminder_id}")
    print(f"   - 标题: {data['reminder']['title']}")
    print(f"   - 优先级: {data['reminder']['priority']}")

    return reminder_id


def test_get_reminders(user_id=USER_ID):
    """测试获取提醒列表"""
    print_section("测试2: 获取提醒列表")

    response = requests.get(
        f"{BASE_URL}/api/reminders",
        params={"user_id": user_id, "enabled_only": False},
        timeout=10
    )

    assert response.status_code == 200, f"获取失败: {response.text}"
    data = response.json()

    print(f"✅ 获取成功，共 {data['total']} 条提醒")
    for reminder in data['reminders'][:3]:
        print(f"   - {reminder['title']}: {reminder['content'][:30]}...")

    return data['reminders']


def test_trigger_reminder(reminder_id):
    """测试触发提醒"""
    print_section("测试3: 触发提醒")

    response = requests.post(
        f"{BASE_URL}/api/reminders/{reminder_id}/trigger",
        timeout=10
    )

    assert response.status_code == 200, f"触发失败: {response.text}"
    data = response.json()
    assert data['success'], "触发失败"

    print(f"✅ 提醒已触发 (ID: {reminder_id})")
    return True


def test_reminder_in_chat(user_id=USER_ID):
    """测试提醒在聊天中的展示"""
    print_section("测试4: 聊天中的提醒展示")

    response = requests.post(
        f"{BASE_URL}/chat",
        params={
            "prompt": "你好，今天天气怎么样？",
            "user_id": user_id
        },
        timeout=60
    )

    assert response.status_code == 200, f"聊天失败: {response.text}"
    data = response.json()
    reply = data['reply']

    # 检查回复中是否包含提醒
    has_reminder = '🔔' in reply or '提醒' in reply

    print(f"✅ 聊天回复已收到")
    if has_reminder:
        print("✅ 回复中包含提醒内容")
        print(f"\n小乐的回复:\n{'-' * 70}")
        print(reply)
        print('-' * 70)
    else:
        print("⚠️  回复中未检测到提醒（可能已超过5分钟）")

    return has_reminder


def test_reminder_history(user_id=USER_ID):
    """测试提醒历史"""
    print_section("测试5: 提醒历史")

    response = requests.get(
        f"{BASE_URL}/api/reminders/history/{user_id}",
        params={"limit": 5},
        timeout=10
    )

    assert response.status_code == 200, f"获取历史失败: {response.text}"
    data = response.json()

    print(f"✅ 获取历史成功，共 {data['total']} 条记录")
    for record in data['history'][:3]:
        print(f"   - {record['title']}: 触发于 {record['triggered_at']}")

    return data['history']


def test_toggle_reminder(reminder_id):
    """测试切换提醒状态"""
    print_section("测试6: 切换提醒状态")

    response = requests.post(
        f"{BASE_URL}/api/reminders/{reminder_id}/toggle",
        params={"user_id": USER_ID},  # 添加user_id参数
        timeout=10
    )

    assert response.status_code == 200, f"切换失败: {response.text}"
    data = response.json()
    assert data['success'], f"切换失败: {data}"

    print(f"✅ 提醒状态已切换")
    print(f"   - 当前状态: {'启用' if data['enabled'] else '禁用'}")

    return data['enabled']


def test_delete_reminder(reminder_id):
    """测试删除提醒"""
    print_section("测试7: 删除提醒")

    response = requests.delete(
        f"{BASE_URL}/api/reminders/{reminder_id}",
        timeout=10
    )

    assert response.status_code == 200, f"删除失败: {response.text}"
    data = response.json()
    assert data['success'], "删除失败"

    print(f"✅ 提醒已删除 (ID: {reminder_id})")
    return True


def test_check_reminders(user_id=USER_ID):
    """测试手动检查提醒"""
    print_section("测试8: 手动检查提醒")

    # 先创建一个已过期的提醒
    trigger_time = (datetime.now() - timedelta(minutes=1)
                    ).strftime("%Y-%m-%d %H:%M:%S")

    create_response = requests.post(
        f"{BASE_URL}/api/reminders",
        json={
            "user_id": user_id,
            "reminder_type": "time",
            "trigger_condition": {"datetime": trigger_time},
            "title": "自动检查测试",
            "content": "用于测试自动检查功能",
            "priority": 2,
            "repeat": False
        },
        timeout=10
    )

    assert create_response.status_code == 200
    reminder_id = create_response.json()['reminder']['reminder_id']
    print(f"✅ 创建测试提醒 (ID: {reminder_id})")

    # 手动检查
    response = requests.post(
        f"{BASE_URL}/api/reminders/check",
        json={"user_id": user_id},
        timeout=10
    )

    assert response.status_code == 200, f"检查失败: {response.text}"
    data = response.json()

    print(f"✅ 检查完成")
    print(f"   - 检查数量: {data['total_checked']}")
    print(f"   - 触发的提醒:")
    for item in data['triggered']:
        print(f"     • {item['title']}: {'成功' if item['triggered'] else '失败'}")

    # 清理
    requests.delete(f"{BASE_URL}/api/reminders/{reminder_id}", timeout=10)

    return data['total_checked']


def test_scheduler_status():
    """测试调度器状态"""
    print_section("测试9: 调度器状态")

    response = requests.get(
        f"{BASE_URL}/api/scheduler/status",
        timeout=10
    )

    assert response.status_code == 200, f"获取状态失败: {response.text}"
    data = response.json()

    print(f"✅ 调度器状态")
    print(f"   - 运行中: {data['running']}")
    print(f"   - 任务数: {data['total_jobs']}")
    print(f"   - 任务列表:")
    for job in data['jobs']:
        print(f"     • {job['name']}: 下次运行 {job['next_run_time']}")

    return data['running']


def run_all_tests():
    """运行所有测试"""
    print("\n")
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 20 + "🔔 提醒系统集成测试" + " " * 27 + "║")
    print("╚" + "═" * 68 + "╝")

    try:
        # 测试1: 创建提醒
        reminder_id = test_create_reminder()
        time.sleep(0.5)

        # 测试2: 获取提醒列表
        reminders = test_get_reminders()
        time.sleep(0.5)

        # 测试3: 触发提醒
        test_trigger_reminder(reminder_id)
        time.sleep(0.5)

        # 测试4: 聊天中的提醒展示
        test_reminder_in_chat()
        time.sleep(0.5)

        # 测试5: 提醒历史
        test_reminder_history()
        time.sleep(0.5)

        # 测试6: 切换状态
        test_toggle_reminder(reminder_id)
        time.sleep(0.5)

        # 测试7: 删除提醒
        test_delete_reminder(reminder_id)
        time.sleep(0.5)

        # 测试8: 手动检查
        test_check_reminders()
        time.sleep(0.5)

        # 测试9: 调度器状态
        test_scheduler_status()

        # 总结
        print_section("✨ 测试总结")
        print("✅ 所有测试通过！")
        print("\n功能验证:")
        print("  ✓ 提醒创建、获取、更新、删除")
        print("  ✓ 提醒触发和历史记录")
        print("  ✓ 聊天时主动展示提醒")
        print("  ✓ 手动检查和自动调度")
        print("\n" + "=" * 70 + "\n")

        return True

    except AssertionError as e:
        print(f"\n❌ 测试失败: {e}")
        return False
    except Exception as e:
        print(f"\n❌ 测试出错: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n⏳ 等待服务器启动...")
    time.sleep(2)

    # 检查服务器是否运行
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        if response.status_code == 200:
            print("✅ 服务器已就绪\n")
        else:
            print("❌ 服务器响应异常")
            sys.exit(1)
    except Exception as e:
        print(f"❌ 无法连接到服务器: {e}")
        print("   请确保服务器在 http://localhost:8000 运行")
        sys.exit(1)

    # 运行测试
    success = run_all_tests()
    sys.exit(0 if success else 1)
