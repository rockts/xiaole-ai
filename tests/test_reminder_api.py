"""
测试提醒系统API
"""
import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"


def test_reminder_api():
    """测试提醒系统API"""
    print("=" * 60)
    print("🧪 测试提醒系统API")
    print("=" * 60)
    
    user_id = "test_user_api"
    
    # 测试1: 创建时间提醒
    print("\n📝 测试1: POST /api/reminders - 创建时间提醒")
    tomorrow = datetime.now() + timedelta(days=1)
    response = requests.post(f"{BASE_URL}/api/reminders", params={
        "user_id": user_id,
        "reminder_type": "time",
        "title": "API测试提醒",
        "content": "这是通过API创建的测试提醒",
        "priority": 1
    }, json={
        "trigger_condition": {
            "datetime": tomorrow.strftime("%Y-%m-%d 10:00:00")
        }
    })
    
    if response.status_code == 200:
        data = response.json()
        if data.get("success"):
            reminder_id = data["reminder"]["reminder_id"]
            print(f"✅ 创建成功: ID={reminder_id}")
        else:
            print(f"❌ 创建失败: {data.get('error')}")
            return False
    else:
        print(f"❌ API调用失败: {response.status_code}")
        return False
    
    # 测试2: 获取提醒列表
    print("\n📝 测试2: GET /api/reminders - 获取提醒列表")
    response = requests.get(f"{BASE_URL}/api/reminders", params={
        "user_id": user_id
    })
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ 查询成功: 共{data['total']}条提醒")
        for r in data['reminders']:
            print(f"   - [{r['reminder_type']}] {r['title']}")
    else:
        print(f"❌ API调用失败: {response.status_code}")
        return False
    
    # 测试3: 获取单个提醒
    print(f"\n📝 测试3: GET /api/reminders/{reminder_id} - 获取提醒详情")
    response = requests.get(
        f"{BASE_URL}/api/reminders/{reminder_id}",
        params={"user_id": user_id}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ 查询成功: {data['title']}")
    else:
        print(f"❌ API调用失败: {response.status_code}")
    
    # 测试4: 更新提醒
    print(f"\n📝 测试4: PUT /api/reminders/{reminder_id} - 更新提醒")
    response = requests.put(
        f"{BASE_URL}/api/reminders/{reminder_id}",
        params={
            "content": "更新后的提醒内容",
            "priority": 2
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        if data.get("success"):
            print(f"✅ 更新成功")
        else:
            print(f"❌ 更新失败")
    else:
        print(f"❌ API调用失败: {response.status_code}")
    
    # 测试5: 切换提醒状态
    print(f"\n📝 测试5: POST /api/reminders/{reminder_id}/toggle - 禁用提醒")
    response = requests.post(
        f"{BASE_URL}/api/reminders/{reminder_id}/toggle"
    )
    
    if response.status_code == 200:
        data = response.json()
        if data.get("success"):
            print(f"✅ 状态切换成功: enabled={data['enabled']}")
        else:
            print(f"❌ 状态切换失败")
    else:
        print(f"❌ API调用失败: {response.status_code}")
    
    # 测试6: 检查提醒触发
    print(f"\n📝 测试6: POST /api/reminders/check - 检查提醒")
    response = requests.post(
        f"{BASE_URL}/api/reminders/check",
        params={"user_id": user_id}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ 检查完成: {data['total_checked']}个提醒需要触发")
    else:
        print(f"❌ API调用失败: {response.status_code}")
    
    # 测试7: 获取提醒历史
    print(f"\n📝 测试7: GET /api/reminders/history - 获取历史")
    response = requests.get(
        f"{BASE_URL}/api/reminders/history",
        params={"user_id": user_id, "limit": 10}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ 查询成功: {data['total']}条历史记录")
    else:
        print(f"❌ API调用失败: {response.status_code}")
    
    # 测试8: 删除提醒
    print(f"\n📝 测试8: DELETE /api/reminders/{reminder_id} - 删除提醒")
    response = requests.delete(f"{BASE_URL}/api/reminders/{reminder_id}")
    
    if response.status_code == 200:
        data = response.json()
        if data.get("success"):
            print(f"✅ 删除成功")
        else:
            print(f"❌ 删除失败")
    else:
        print(f"❌ API调用失败: {response.status_code}")
    
    print("\n" + "=" * 60)
    print("✅ API测试完成！")
    print("=" * 60)
    return True


if __name__ == "__main__":
    try:
        # 先检查服务器是否运行
        response = requests.get(f"{BASE_URL}/")
        if response.status_code != 200:
            print("❌ 服务器未运行，请先启动: python3 main.py")
            exit(1)
        
        # 运行测试
        result = test_reminder_api()
        exit(0 if result else 1)
        
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器")
        print("请先启动服务器: python3 main.py")
        exit(1)
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
