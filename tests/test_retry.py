"""
测试错误处理和重试机制
"""
import os
import logging
import io
from error_handler import logger, APITimeoutError
from agent import XiaoLeAgent
import requests
import time
from unittest.mock import patch, MagicMock
import sys
sys.path.append('/Users/rockts/Dev/xiaole-ai')

print("=" * 60)
print("测试小乐AI管家 - 错误处理和重试机制")
print("=" * 60)

# 测试1: 模拟超时重试
print("\n【测试1: 模拟API超时 - 验证重试机制】")

# 捕获日志输出
log_stream = io.StringIO()
handler = logging.StreamHandler(log_stream)
handler.setLevel(logging.INFO)
logger.addHandler(handler)

# 创建agent实例
agent = XiaoLeAgent()

# 模拟超时场景
print("正在模拟API超时...")
original_post = requests.post

call_count = [0]


def mock_timeout_then_success(*args, **kwargs):
    call_count[0] += 1
    if call_count[0] <= 2:  # 前两次失败
        print(f"  第 {call_count[0]} 次调用: 超时")
        raise requests.Timeout("Connection timed out")
    else:  # 第三次成功
        print(f"  第 {call_count[0]} 次调用: 成功")
        # 返回模拟响应
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{
                "message": {
                    "content": "重试成功！我是小乐AI管家。"
                }
            }]
        }
        return mock_response


# 使用mock
with patch('requests.post', side_effect=mock_timeout_then_success):
    try:
        result = agent.think("你好")
        print(f"\n✅ 重试机制测试通过!")
        print(f"   总调用次数: {call_count[0]}")
        print(f"   最终结果: {result[:30]}...")
    except Exception as e:
        print(f"❌ 测试失败: {e}")

# 查看日志
log_output = log_stream.getvalue()
if "WARNING" in log_output:
    warning_count = log_output.count("WARNING")
    print(f"\n📝 日志验证:")
    print(f"   警告日志数: {warning_count}")
    print(f"   ✓ 重试过程已记录到日志")

# 测试2: 模拟连接错误
print("\n【测试2: 模拟网络连接错误】")
call_count[0] = 0
log_stream.truncate(0)
log_stream.seek(0)


def mock_connection_error(*args, **kwargs):
    call_count[0] += 1
    print(f"  第 {call_count[0]} 次调用: 连接失败")
    raise requests.ConnectionError("Network unreachable")


with patch('requests.post', side_effect=mock_connection_error):
    try:
        result = agent.think("测试")
        print(f"❌ 应该抛出异常但没有")
    except Exception as e:
        print(f"✅ 正确捕获异常: {type(e).__name__}")
        print(f"   重试次数: {call_count[0]}")
        if call_count[0] >= 3:
            print(f"   ✓ 达到最大重试次数")

# 测试3: 查看实际日志文件
print("\n【测试3: 检查实际日志文件】")
log_path = "/Users/rockts/Dev/xiaole-ai/logs/xiaole_ai.log"
if os.path.exists(log_path):
    with open(log_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # 统计各类日志
    info_count = sum(1 for line in lines if '[INFO]' in line)
    warning_count = sum(1 for line in lines if '[WARNING]' in line)
    error_count = sum(1 for line in lines if '[ERROR]' in line)

    print(f"✅ 日志文件统计:")
    print(f"   总行数: {len(lines)}")
    print(f"   INFO: {info_count}")
    print(f"   WARNING: {warning_count}")
    print(f"   ERROR: {error_count}")

    # 显示最近的重试日志
    print(f"\n📋 最近的重要日志:")
    for line in lines[-10:]:
        if any(x in line for x in ['WARNING', 'ERROR', '重试', '失败']):
            print(f"   {line.strip()}")

# 测试4: 实际API调用（验证正常流程不受影响）
print("\n【测试4: 验证正常API调用】")
try:
    response = requests.post(
        "http://localhost:8000/chat?prompt=测试重试功能",
        timeout=30
    )
    if response.status_code == 200:
        data = response.json()
        print(f"✅ 正常API调用成功")
        print(f"   回复: {data['reply'][:40]}...")
except Exception as e:
    print(f"❌ API调用失败: {e}")

print("\n" + "=" * 60)
print("测试完成")
print("=" * 60)
