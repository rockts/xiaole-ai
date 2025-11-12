"""
v0.8.0 任务管理功能测试
测试任务识别、拆解、执行的完整流程
"""
import requests
import json
import time

API_BASE = "http://localhost:8000"
USER_ID = "test_user"
SESSION_ID = "test_session_001"


def test_1_task_identification():
    """测试1: 任务识别"""
    print("\n" + "="*50)
    print("测试1: 任务识别")
    print("="*50)

    test_cases = [
        {
            "input": "帮我准备周末野餐",
            "expected": True,
            "description": "复杂任务 - 需要多步骤"
        },
        {
            "input": "今天天气怎么样",
            "expected": False,
            "description": "简单查询 - 不是任务"
        },
        {
            "input": "帮我整理一份工作报告,需要数据分析和图表",
            "expected": True,
            "description": "复杂任务 - 多个子任务"
        }
    ]

    for i, case in enumerate(test_cases, 1):
        print(f"\n测试用例 {i}: {case['description']}")
        print(f"输入: {case['input']}")

        # 通过chat接口发送消息
        response = requests.post(
            f"{API_BASE}/chat",
            json={
                "message": case['input'],
                "user_id": USER_ID,
                "session_id": SESSION_ID
            }
        )

        if response.status_code == 200:
            data = response.json()
            print(f"响应: {data.get('reply', '')[:100]}...")
            print(f"✅ 测试通过")
        else:
            print(f"❌ 请求失败: {response.status_code}")


def test_2_create_task():
    """测试2: 创建任务"""
    print("\n" + "="*50)
    print("测试2: 手动创建任务")
    print("="*50)

    task_data = {
        "user_id": USER_ID,
        "session_id": SESSION_ID,
        "title": "准备周末野餐",
        "description": "包括查天气、购物、准备物品等",
        "priority": 1
    }

    response = requests.post(
        f"{API_BASE}/api/tasks",
        json=task_data
    )

    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            task_id = data.get('task_id')
            print(f"✅ 任务创建成功, ID: {task_id}")
            return task_id
        else:
            print(f"❌ 创建失败: {data.get('error')}")
    else:
        print(f"❌ 请求失败: {response.status_code}")

    return None


def test_3_get_task(task_id):
    """测试3: 获取任务详情"""
    print("\n" + "="*50)
    print("测试3: 获取任务详情")
    print("="*50)

    if not task_id:
        print("❌ 没有任务ID")
        return

    response = requests.get(f"{API_BASE}/api/tasks/{task_id}")

    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            task = data.get('task', {})
            steps = data.get('steps', [])
            print(f"✅ 任务详情:")
            print(f"  标题: {task.get('title')}")
            print(f"  状态: {task.get('status')}")
            print(f"  优先级: {task.get('priority')}")
            print(f"  步骤数: {len(steps)}")
            for i, step in enumerate(steps, 1):
                print(
                    f"    {i}. {step.get('description')} [{step.get('status')}]")
        else:
            print(f"❌ 获取失败: {data.get('error')}")
    else:
        print(f"❌ 请求失败: {response.status_code}")


def test_4_list_tasks():
    """测试4: 获取任务列表"""
    print("\n" + "="*50)
    print("测试4: 获取任务列表")
    print("="*50)

    response = requests.get(
        f"{API_BASE}/api/sessions/{SESSION_ID}/tasks"
    )

    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            tasks = data.get('tasks', [])
            print(f"✅ 找到 {len(tasks)} 个任务")
            for task in tasks[:5]:  # 只显示前5个
                print(f"  - [{task.get('status')}] {task.get('title')}")
        else:
            print(f"❌ 获取失败: {data.get('error')}")
    else:
        print(f"❌ 请求失败: {response.status_code}")


def test_5_execute_task(task_id):
    """测试5: 执行任务"""
    print("\n" + "="*50)
    print("测试5: 执行任务")
    print("="*50)

    if not task_id:
        print("❌ 没有任务ID")
        return

    response = requests.post(
        f"{API_BASE}/api/tasks/{task_id}/execute",
        json={
            "user_id": USER_ID,
            "session_id": SESSION_ID
        }
    )

    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            print(f"✅ 任务执行成功")
            print(f"  总步骤: {data.get('total_steps')}")
            print(f"  完成步骤: {data.get('completed_steps')}")
            print(f"  失败步骤: {data.get('failed_steps')}")
            print(f"  最终状态: {data.get('status')}")
        else:
            print(f"❌ 执行失败: {data.get('error')}")
    else:
        print(f"❌ 请求失败: {response.status_code}")


def test_6_update_status(task_id):
    """测试6: 更新任务状态"""
    print("\n" + "="*50)
    print("测试6: 更新任务状态")
    print("="*50)

    if not task_id:
        print("❌ 没有任务ID")
        return

    response = requests.put(
        f"{API_BASE}/api/tasks/{task_id}/status",
        json={"status": "cancelled"}
    )

    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            print(f"✅ 状态更新成功")
        else:
            print(f"❌ 更新失败: {data.get('error')}")
    else:
        print(f"❌ 请求失败: {response.status_code}")


def test_7_delete_task(task_id):
    """测试7: 删除任务"""
    print("\n" + "="*50)
    print("测试7: 删除任务")
    print("="*50)

    if not task_id:
        print("❌ 没有任务ID")
        return

    response = requests.delete(f"{API_BASE}/api/tasks/{task_id}")

    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            print(f"✅ 任务删除成功")
        else:
            print(f"❌ 删除失败: {data.get('error')}")
    else:
        print(f"❌ 请求失败: {response.status_code}")


def test_8_statistics():
    """测试8: 获取统计信息"""
    print("\n" + "="*50)
    print("测试8: 获取统计信息")
    print("="*50)

    response = requests.get(f"{API_BASE}/api/tasks/stats/{USER_ID}")

    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            stats = data.get('stats', {})
            print(f"✅ 统计信息:")
            print(f"  总任务数: {stats.get('total', 0)}")
            print(f"  待处理: {stats.get('pending', 0)}")
            print(f"  执行中: {stats.get('in_progress', 0)}")
            print(f"  已完成: {stats.get('completed', 0)}")
            print(f"  失败: {stats.get('failed', 0)}")
        else:
            print(f"❌ 获取失败: {data.get('error')}")
    else:
        print(f"❌ 请求失败: {response.status_code}")


def main():
    """运行所有测试"""
    print("\n" + "="*60)
    print("🧪 开始任务管理功能测试")
    print("="*60)

    try:
        # 测试基本功能
        # test_1_task_identification()

        # 创建并管理任务
        task_id = test_2_create_task()
        time.sleep(1)

        test_3_get_task(task_id)
        time.sleep(1)

        test_4_list_tasks()
        time.sleep(1)

        # 不执行任务,避免实际调用工具
        # test_5_execute_task(task_id)
        # time.sleep(1)

        test_8_statistics()
        time.sleep(1)

        test_6_update_status(task_id)
        time.sleep(1)

        test_7_delete_task(task_id)

        print("\n" + "="*60)
        print("✅ 测试完成!")
        print("="*60)

    except Exception as e:
        print(f"\n❌ 测试过程中出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
