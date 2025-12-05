#!/usr/bin/env python3
"""
恢复消息的图片路径

根据时间戳将上传的图片与数据库中的消息关联起来
"""
import os
import sys

# 添加项目根目录到路径
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)

from pathlib import Path
from backend.db_setup import SessionLocal, Message

UPLOADS_DIR = Path(PROJECT_ROOT) / "backend" / "uploads"
TIME_TOLERANCE = 10  # 时间戳容差（秒）


def collect_image_files():
    """收集所有带时间戳的图片文件"""
    image_files = {}
    extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
    
    # 根目录图片
    for f in UPLOADS_DIR.glob('*.*'):
        if f.is_file() and f.suffix.lower() in extensions:
            parts = f.name.split('_', 1)
            if parts[0].isdigit():
                ts = int(parts[0])
                image_files[ts] = f"uploads/{f.name}"
    
    # images 子目录
    images_dir = UPLOADS_DIR / "images"
    if images_dir.exists():
        for f in images_dir.glob('*.*'):
            if f.is_file() and f.suffix.lower() in extensions:
                parts = f.name.split('_', 1)
                if parts[0].isdigit():
                    ts = int(parts[0])
                    image_files[ts] = f"uploads/images/{f.name}"
    
    return image_files


def find_matches(db, image_files):
    """匹配消息和图片"""
    messages = db.query(Message).filter(
        Message.role == 'user',
        Message.image_path == None
    ).all()
    
    matches = []
    used_images = set()
    
    for msg in messages:
        msg_ts = int(msg.created_at.timestamp())
        best_match = None
        best_diff = TIME_TOLERANCE + 1
        
        for img_ts, img_path in image_files.items():
            if img_ts in used_images:
                continue
            diff = abs(img_ts - msg_ts)
            if diff <= TIME_TOLERANCE and diff < best_diff:
                best_match = (img_ts, img_path)
                best_diff = diff
        
        if best_match:
            matches.append({
                'msg_id': msg.id,
                'msg_ts': msg_ts,
                'msg_time': msg.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'msg_content': (msg.content[:40] if msg.content else "")[:40],
                'img_ts': best_match[0],
                'img_path': best_match[1],
                'time_diff': best_diff
            })
            used_images.add(best_match[0])
    
    return matches


def main(auto_confirm=False):
    print("=" * 60)
    print("恢复消息图片路径工具")
    print("=" * 60)
    
    # 收集图片
    image_files = collect_image_files()
    print(f"\n📁 找到 {len(image_files)} 个带时间戳的图片文件")
    
    db = SessionLocal()
    try:
        # 统计
        total_msgs = db.query(Message).filter(Message.role == 'user').count()
        msgs_with_img = db.query(Message).filter(
            Message.role == 'user',
            Message.image_path != None
        ).count()
        msgs_without_img = total_msgs - msgs_with_img
        
        print(f"📊 用户消息统计:")
        print(f"   - 总数: {total_msgs}")
        print(f"   - 已有图片: {msgs_with_img}")
        print(f"   - 无图片: {msgs_without_img}")
        
        # 查找匹配
        matches = find_matches(db, image_files)
        print(f"\n🔍 找到 {len(matches)} 个可恢复的图片关联")
        
        if not matches:
            print("\n✅ 没有需要恢复的图片")
            return
        
        # 显示匹配
        print("\n匹配列表:")
        print("-" * 60)
        for m in matches:
            print(f"消息 #{m['msg_id']} ({m['msg_time']})")
            print(f"  内容: {m['msg_content']}...")
            print(f"  图片: {m['img_path']}")
            print(f"  时间差: {m['time_diff']}秒")
            print()
        
        # 确认
        if auto_confirm:
            confirm = 'y'
        else:
            confirm = input(f"\n是否更新这 {len(matches)} 条记录? (y/n): ").strip().lower()
        if confirm != 'y':
            print("已取消")
            return
        
        # 执行更新
        updated = 0
        for m in matches:
            msg = db.query(Message).filter(Message.id == m['msg_id']).first()
            if msg:
                msg.image_path = m['img_path']
                updated += 1
        
        db.commit()
        print(f"\n✅ 成功更新 {updated} 条消息的图片路径")
        
    finally:
        db.close()


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='恢复消息图片路径')
    parser.add_argument('-y', '--yes', action='store_true', help='自动确认')
    args = parser.parse_args()
    main(auto_confirm=args.yes)
