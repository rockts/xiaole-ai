#!/usr/bin/env python3
"""快速恢复图片路径"""
import os
import sys
sys.path.insert(0, '/Users/rockts/Dev/xiaole-ai')

from pathlib import Path
from backend.db_setup import SessionLocal, Message

UPLOADS_DIR = Path('/Users/rockts/Dev/xiaole-ai/backend/uploads')
image_files = {}

# 收集图片
for f in UPLOADS_DIR.glob('*.*'):
    if f.is_file() and f.suffix.lower() in ['.jpg', '.jpeg', '.png']:
        parts = f.name.split('_', 1)
        if parts[0].isdigit():
            image_files[int(parts[0])] = 'uploads/' + f.name

images_dir = UPLOADS_DIR / 'images'
for f in images_dir.glob('*.*'):
    if f.is_file() and f.suffix.lower() in ['.jpg', '.jpeg', '.png']:
        parts = f.name.split('_', 1)
        if parts[0].isdigit():
            image_files[int(parts[0])] = 'uploads/images/' + f.name

print(f'Found {len(image_files)} images')

db = SessionLocal()
messages = db.query(Message).filter(Message.role == 'user', Message.image_path == None).all()
print(f'Messages without image: {len(messages)}')

updated = 0
for msg in messages:
    msg_ts = int(msg.created_at.timestamp())
    for img_ts in image_files:
        if abs(img_ts - msg_ts) <= 10:
            msg.image_path = image_files[img_ts]
            updated += 1
            print(f'Updated msg {msg.id} -> {image_files[img_ts]}')
            break

db.commit()
print(f'Total updated: {updated}')
db.close()
