# 图片记忆持久化与识别置信度说明

本指南介绍图片分析与记忆落库的工作流、环境变量、以及快速测试方法。

## 工作流概述
- 分析入口：`POST /api/vision/analyze`（见 `backend/routers/vision.py`）。
- 分析实现：`tools/vision_tool.py`，先做人脸识别（`backend/face_manager.py`）后调用视觉大模型（可选）。
- 记忆落库：分析成功后写入 `memories` 表，`tag='image:<filename>'`；若提供 `image_path`，将以前缀形式写入内容（例如：`[image_path:/uploads/images/xxx.png] ...`）。
- Agent 路径：若对话中通过工具链触发 `vision_analysis`，`backend/agent.py` 同样会按上述规则写入图片记忆。

## 识别置信度与确认
- `FACE_MATCH_THRESHOLD`（默认 `0.5`）：人脸匹配判定阈值，越小越严格。
- `FACE_ANNOUNCE_THRESHOLD`（默认 `0.6`）：用于对外话术的“低置信”提示阈值。识别低于该阈值时，结果以“可能是…需确认”的方式呈现。
- `VisionTool.analyze_image` 会在返回值中附带 `face_details`，包含 `name/matched/best_distance/confidence` 等细节。

## 快速测试
1) 启动后端
```bash
cd backend
../.venv/bin/uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

2) 上传图片（可选，也可直接使用现有文件路径）
```bash
curl -F "file=@/absolute/path/to/image.jpg" http://127.0.0.1:8000/api/vision/upload
```
响应中的 `file_path` 形如 `/uploads/images/<filename>`。

3) 触发分析并写入图片记忆
```bash
curl -X POST http://127.0.0.1:8000/api/vision/analyze \
  -H 'Content-Type: application/json' \
  -d '{"image_path":"/uploads/images/<filename>","prompt":"请描述这张图片"}'
```
返回体包含：`description/face_info/face_details/model/memory_id/tag`。

4) 数据库验证（示例脚本）
```bash
/Users/rockts/Dev/xiaole-ai/.venv/bin/python - <<'PY'
import sys
sys.path.append('/Users/rockts/Dev/xiaole-ai/backend')
from db_setup import SessionLocal, Memory
s=SessionLocal()
rows = s.query(Memory).filter(Memory.tag.like('image:%')).order_by(Memory.created_at.desc()).limit(10).all()
print('Image memories:', len(rows))
for m in rows:
    print(m.id, m.tag, (m.content or '')[:120].replace('\n',' '))
s.close()
PY
```

## 常见问题
- 看不到图片记忆：请用 `like('image:%')` 查询；等值 `tag=='image'` 会匹配不到。
- 视觉模型报错/未配置：`VisionTool` 会兜底返回“人脸识别结果 + 空描述”，保证流程不中断。
- 需要纠正识别身份：前端/对话中确认后可调用 `register_face` 工具（`tools/vision_tool.py`）注册面孔以提升后续识别准确率。
