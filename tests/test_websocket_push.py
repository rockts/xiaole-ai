"""
WebSocket实时推送测试脚本
测试提醒系统的实时推送功能
"""
import requests
import time
from datetime import datetime, timedelta
import subprocess
import sys


def print_section(title):
    """打印章节标题"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)


def create_test_reminder(seconds_delay=30):
    """创建测试提醒"""
    trigger_time = (datetime.now() + timedelta(seconds=seconds_delay)
                    ).strftime("%Y-%m-%d %H:%M:%S")

    response = requests.post(
        "http://localhost:8000/api/reminders",
        json={
            "user_id": "default_user",
            "reminder_type": "time",
            "trigger_condition": {"datetime": trigger_time},
            "title": f"⚡ WebSocket实时推送测试",
            "content": f"这是一个{seconds_delay}秒后触发的测试提醒。如果你看到这个弹窗，说明WebSocket实时推送工作正常！",
            "priority": 1,
            "repeat": False
        },
        timeout=10
    )

    return response.json()['reminder'], trigger_time


def monitor_logs(reminder_id, timeout=60):
    """监控日志直到看到提醒触发"""
    print(f"\n🔍 开始监控日志（最多等待{timeout}秒）...")

    start_time = time.time()
    last_check = 0

    while time.time() - start_time < timeout:
        elapsed = int(time.time() - start_time)

        # 每5秒打印一次进度
        if elapsed > last_check and elapsed % 5 == 0:
            remaining = timeout - elapsed
            print(f"   ⏳ 已等待 {elapsed}秒，还剩 {remaining}秒...")
            last_check = elapsed

        # 检查日志
        try:
            result = subprocess.run(
                ["grep", f"reminder {reminder_id}",
                    "/Users/rockts/Dev/xiaole-ai/server.log"],
                capture_output=True,
                text=True,
                timeout=2
            )

            logs = result.stdout.strip().split('\n')

            # 查找关键日志
            created = any("Created reminder" in log for log in logs)
            triggered = any("Triggered reminder" in log for log in logs)
            pushed = any("WebSocket推送" in log for log in logs)

            if triggered and pushed:
                print(f"\n   ✅ 提醒已触发并通过WebSocket推送！")
                print(f"\n日志详情：")
                for log in logs:
                    if str(reminder_id) in log:
                        print(f"   {log}")
                return True
            elif created:
                # 提醒已创建，继续等待
                time.sleep(1)

        except Exception as e:
            print(f"   ⚠️  日志检查出错: {e}")
            time.sleep(1)

    print(f"\n   ❌ 超时：{timeout}秒内未检测到提醒触发")
    return False


def main():
    """主测试流程"""
    print_section("🧪 WebSocket实时推送测试")

    print("\n📝 测试说明：")
    print("   1. 创建一个30秒后触发的测试提醒")
    print("   2. 实时监控服务器日志")
    print("   3. 验证WebSocket推送是否成功")
    print("   4. 请打开浏览器查看弹窗效果")

    # 检查服务器是否运行
    print("\n🔍 检查服务器状态...")
    try:
        response = requests.get("http://localhost:8000/", timeout=3)
        print("   ✅ 服务器运行正常")
    except Exception as e:
        print(f"   ❌ 服务器未运行: {e}")
        print("   请先启动服务器: python main.py")
        sys.exit(1)

    # 创建测试提醒
    print_section("📋 步骤1: 创建测试提醒")

    try:
        reminder, trigger_time = create_test_reminder(seconds_delay=30)
        reminder_id = reminder['reminder_id']

        print(f"✅ 提醒创建成功")
        print(f"   ID: {reminder_id}")
        print(f"   标题: {reminder['title']}")
        print(f"   触发时间: {trigger_time}")
        print(f"   内容: {reminder['content']}")

    except Exception as e:
        print(f"❌ 创建提醒失败: {e}")
        sys.exit(1)

    # 提示打开浏览器
    print_section("🌐 步骤2: 打开浏览器")
    print("\n请立即打开浏览器访问：")
    print("   👉 http://localhost:8000/static/index.html")
    print("\n建议操作：")
    print("   1. 打开浏览器控制台（F12）")
    print("   2. 查看Console标签，确认WebSocket已连接")
    print("   3. 应该看到: '✅ WebSocket已连接'")
    print("\n按Enter键继续监控...")
    input()

    # 监控日志
    print_section("📊 步骤3: 监控提醒触发")

    success = monitor_logs(reminder_id, timeout=60)

    # 测试结果
    print_section("📝 测试结果")

    if success:
        print("\n🎉 测试成功！")
        print("   ✅ 提醒已触发")
        print("   ✅ WebSocket推送成功")
        print("   ✅ 请检查浏览器是否显示弹窗")
        print("\n预期效果：")
        print("   1. 浏览器右上角出现提醒弹窗")
        print("   2. 弹窗包含标题、内容和操作按钮")
        print("   3. 10秒后自动消失")
        print("   4. 如果页面在后台，应收到系统通知")
    else:
        print("\n❌ 测试失败")
        print("   请检查：")
        print("   1. 服务器是否正常运行")
        print("   2. WebSocket连接是否建立")
        print("   3. 浏览器控制台是否有错误")

    print("\n" + "="*70)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  测试被中断")
        sys.exit(0)
