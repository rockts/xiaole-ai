#!/usr/bin/env python3
"""
生成测试行为数据 - 用于展示行为分析功能
运行后可在前端看到行为分析数据
"""
from db_setup import Message, UserBehavior, SessionLocal
from datetime import datetime, timedelta
import random
import json


def generate_test_data():
    """生成测试行为数据"""
    session = SessionLocal()

    try:
        # 清空旧测试数据
        session.query(UserBehavior).delete()
        session.commit()
        print("✅ 清空旧数据")

        # 生成5个会话的测试数据
        user_id = "default_user"
        topics_pool = ["天气", "美食", "运动", "电影", "音乐", "旅游", "科技", "健康"]

        for i in range(5):
            session_id = f"test_session_{i+1}"

            # 随机生成会话数据
            message_count = random.randint(5, 15)
            user_message_count = message_count // 2
            avg_message_length = random.randint(20, 80)

            # 随机时间（过去7天内）
            days_ago = random.randint(0, 7)
            hours = random.randint(8, 22)
            start_time = datetime.now() - timedelta(days=days_ago, hours=24 -
                                                    hours, minutes=random.randint(0, 59))
            end_time = start_time + timedelta(minutes=random.randint(5, 30))

            duration_seconds = int((end_time - start_time).total_seconds())

            # 随机选择1-3个话题
            topics = random.sample(topics_pool, random.randint(1, 3))

            behavior = UserBehavior(
                user_id=user_id,
                session_id=session_id,
                message_count=message_count,
                user_message_count=user_message_count,
                avg_message_length=avg_message_length,
                start_time=start_time,
                end_time=end_time,
                duration_seconds=duration_seconds,
                topics=json.dumps(topics, ensure_ascii=False),
                created_at=start_time
            )

            session.add(behavior)
            print(
                f"✅ 生成会话 {i+1}: {topics}, {message_count}条消息, {duration_seconds}秒")

        session.commit()

        # 显示统计
        total = session.query(UserBehavior).count()
        print(f"\n✅ 成功生成 {total} 条行为数据")
        print("\n现在可以访问前端 '📊 行为分析' 标签页查看数据了！")

    finally:
        session.close()


if __name__ == "__main__":
    print("🔧 生成测试行为数据...\n")
    generate_test_data()
