import urllib.request
import json

BASE_URL = "http://localhost:8000"
USER_ID = "default_user"


def create_task(title, description, priority=0):
    url = f"{BASE_URL}/api/tasks"
    payload = {
        "user_id": USER_ID,
        "session_id": "00000000-0000-0000-0000-000000000000",
        "title": title,
        "description": description,
        "priority": priority
    }
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={
                                 'Content-Type': 'application/json'})

    try:
        with urllib.request.urlopen(req) as response:
            if response.status == 200:
                result = json.loads(response.read().decode('utf-8'))
                if result.get("success"):
                    print(
                        f"✅ Created task: {title} (ID: {result.get('task_id')})")
                else:
                    print(
                        f"❌ Failed to create task: {title} - {result.get('error')}")
            else:
                print(
                    f"❌ Failed to create task: {title} - Status Code: {response.status}")
    except Exception as e:
        print(f"❌ Error creating task: {e}")


def main():
    print("🚀 Populating test tasks...")

    tasks = [
        ("完成前端侧边栏开发", "实现任务列表显示功能", 2),
        ("修复移动端适配问题", "检查iPhone上的显示效果", 1),
        ("编写API文档", "更新Swagger文档", 0),
        ("测试语音输入功能", "验证百度语音识别准确率", 1),
        ("优化数据库查询", "添加索引提高查询速度", 2)
    ]

    for title, desc, priority in tasks:
        create_task(title, desc, priority)

    print("✨ Done!")


if __name__ == "__main__":
    main()
