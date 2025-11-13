from fastapi import (
    FastAPI, WebSocket, WebSocketDisconnect,
    File, UploadFile, HTTPException
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import Response
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import os
import json
from urllib.parse import quote
from agent import XiaoLeAgent
from memory import MemoryManager
from conflict_detector import ConflictDetector
from proactive_qa import ProactiveQA  # v0.3.0 主动问答
from reminder_manager import get_reminder_manager  # v0.5.0 主动提醒
from scheduler import get_scheduler  # v0.5.0 定时调度
from baidu_voice_tool import baidu_voice_tool  # v0.8.0 百度语音识别
from document_summarizer import DocumentSummarizer  # v0.8.0 Phase 3 文档总结
import time

app = FastAPI(
    title="小乐 AI 管家",
    description="个人 AI 助手系统",
    version="0.8.0",
)

# 配置CORS，允许网页访问API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有HTTP方法
    allow_headers=["*"],  # 允许所有请求头
)

# 挂载静态文件目录（使用绝对路径，避免工作目录不同导致404）
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
UPLOADS_DIR = os.path.join(BASE_DIR, "uploads")

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
app.mount("/uploads", StaticFiles(directory=UPLOADS_DIR), name="uploads")


# Pydantic模型 - v0.5.0提醒系统
class ReminderCreate(BaseModel):
    user_id: str = "default_user"
    reminder_type: str = "time"
    trigger_condition: Dict[str, Any]
    content: str
    title: Optional[str] = None
    priority: int = 3
    repeat: bool = False
    repeat_interval: Optional[int] = None


# v0.8.0: 语音合成请求体
class TTSRequest(BaseModel):
    text: str
    person: int = 0
    speed: int = 5
    pitch: int = 5
    volume: int = 5
    audio_format: str = "mp3"  # mp3|wav|pcm


# v0.8.1: 用户反馈请求体
class FeedbackRequest(BaseModel):
    session_id: str
    message_content: str
    feedback_type: str  # 'good' or 'bad'
    timestamp: str
    user_id: str = "default_user"


xiaole = XiaoLeAgent()
conflict_detector = ConflictDetector()  # v0.3.0 冲突检测器
proactive_qa = ProactiveQA()  # v0.3.0 主动问答分析器
reminder_manager = get_reminder_manager()  # v0.5.0 提醒管理器
scheduler = get_scheduler()  # v0.5.0 定时调度器


# WebSocket连接管理器
class ConnectionManager:
    """管理WebSocket连接"""

    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """接受新连接"""
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"✅ WebSocket客户端已连接，当前连接数: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        """断开连接"""
        self.active_connections.remove(websocket)
        print(f"👋 WebSocket客户端已断开，当前连接数: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        """广播消息给所有连接的客户端"""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                print(f"❌ 发送消息失败: {e}")
                disconnected.append(connection)

        # 清理断开的连接
        for conn in disconnected:
            if conn in self.active_connections:
                self.active_connections.remove(conn)


websocket_manager = ConnectionManager()


@app.on_event("startup")
async def startup_event():
    """应用启动时初始化"""
    # 设置ReminderManager的WebSocket推送回调
    global reminder_manager
    reminder_manager = get_reminder_manager(websocket_manager.broadcast)

    # 启动提醒调度器
    scheduler.start()
    print("✅ 提醒调度器已启动")
    print("✅ WebSocket推送已配置")


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时清理"""
    # 停止提醒调度器
    scheduler.stop()
    print("👋 提醒调度器已停止")


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket端点，用于实时推送提醒"""
    await websocket_manager.connect(websocket)
    try:
        while True:
            # 保持连接，接收客户端消息（心跳等）
            data = await websocket.receive_text()
            # 可以处理客户端消息，如心跳响应
            if data == "ping":
                await websocket.send_json({"type": "pong"})
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket错误: {e}")
        websocket_manager.disconnect(websocket)


@app.get("/")
def hello():
    return {"message": "你好，我是小乐AI管家，我已启动。"}


@app.post("/think")
def think(prompt: str):
    return {"result": xiaole.think(prompt)}


@app.post("/act")
def act(command: str):
    return {"result": xiaole.act(command)}


@app.get("/memory")
def memory(tag: str = "general", limit: int = 10):
    """获取指定标签的记忆"""
    return {"memory": xiaole.memory.recall(tag, limit=limit)}


@app.get("/memory/recent")
def memory_recent(hours: int = 24, tag: str = None, limit: int = 10):
    """获取最近N小时的记忆"""
    return {"memory": xiaole.memory.recall_recent(hours, tag, limit)}


@app.get("/memory/search")
def memory_search(keywords: str, tag: str = None, limit: int = 10):
    """通过关键词搜索记忆（多个关键词用逗号分隔）"""
    kw_list = [kw.strip() for kw in keywords.split(',')]
    memories = xiaole.memory.recall_by_keywords(kw_list, tag, limit)
    return {"memories": memories}


@app.get("/memory/semantic")
def memory_semantic_search(query: str, tag: str = None, limit: int = 10):
    """语义搜索记忆（理解查询意图）"""
    memories = xiaole.memory.semantic_recall(query, tag, limit, min_score=0.1)
    return {"memories": memories}


@app.get("/memory/stats")
def memory_stats():
    """获取记忆统计信息"""
    return xiaole.memory.get_stats()


# ========================================
# v0.7.0: 记忆管理 CRUD API
# ========================================

@app.put("/api/memory/{memory_id}")
async def update_memory(memory_id: int, request: dict):
    """
    更新记忆内容

    Args:
        memory_id: 记忆ID
        request: 包含content和tag的请求体

    Returns:
        dict: 更新结果
    """
    try:
        memory_manager = MemoryManager()
        from db_setup import Memory

        # 查询记忆
        memory = memory_manager.session.query(Memory).filter(
            Memory.id == memory_id
        ).first()

        if not memory:
            return {
                "success": False,
                "error": "记忆不存在"
            }

        # 更新内容
        content = request.get("content")
        tag = request.get("tag")

        if content:
            memory.content = content
        if tag:
            memory.tag = tag

        memory_manager.session.commit()

        return {
            "success": True,
            "message": "记忆已更新"
        }

    except Exception as e:
        print(f"❌ 更新记忆失败: {e}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e)
        }


@app.delete("/api/memory/{memory_id}")
async def delete_memory(memory_id: int):
    """
    删除记忆

    Args:
        memory_id: 记忆ID

    Returns:
        dict: 删除结果
    """
    try:
        memory_manager = MemoryManager()
        from db_setup import Memory

        # 查询记忆
        memory = memory_manager.session.query(Memory).filter(
            Memory.id == memory_id
        ).first()

        if not memory:
            return {
                "success": False,
                "error": "记忆不存在"
            }

        # 删除记忆
        memory_manager.session.delete(memory)
        memory_manager.session.commit()

        return {
            "success": True,
            "message": "记忆已删除"
        }

    except Exception as e:
        print(f"❌ 删除记忆失败: {e}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e)
        }


# 对话会话管理 API
@app.post("/chat")
def chat(
    prompt: str,
    session_id: str = None,
    user_id: str = "default_user",
    response_style: str = "balanced",  # v0.6.0: 响应风格
    image_path: str = None,  # 图片路径（可选）
    memorize: bool = False  # 是否强制记忆（可选）
):
    """
    支持上下文的对话接口

    Args:
        prompt: 用户消息
        session_id: 会话ID (None则创建新会话)
        user_id: 用户ID
        response_style: 响应风格 (concise/balanced/detailed/professional)
        image_path: 图片路径（可选，用于图片识别）
        memorize: 是否强制记忆图片内容（可选）
    """
    # 如果有图片，先进行图片识别
    if image_path:
        from vision_tool import VisionTool
        vision_tool = VisionTool()

        try:
            # 智能选择识别prompt
            # 如果用户问题提到课程表，使用表格专用prompt
            if prompt and any(kw in prompt for kw in ['课程表', '课表', '时间表', '上课']):
                ocr_prompt = '''这是一张学生课程表。请仔细识别表格中的内容：
1. 表头有：星期一、星期二、星期三、星期四、星期五
2. 左侧行标题有：晨读、第1节、第2节...第7节、午休、课后辅导
3. 每个格子可能有课程名称（如"科学"）和编号（如"(5)"）

请完整地列出每一天的所有课程，包括空格子（标注"无课"）。
格式：
周一：晨读-XX, 第1节-XX, 第2节-XX...
周二：...
依此类推。不要省略任何信息。'''
                print("\n🔍 图片识别 - 使用课程表专用prompt")
            else:
                # 通用识别prompt - 增强品牌识别能力
                ocr_prompt = '''请详细描述这张图片的内容，包括：
1. 主体物品或场景是什么
2. 图片中的文字信息（如有）- 特别注意识别品牌标识，如果看到部分文字如"ckin"、"ickin"等，请推测完整品牌名（如Luckin瑞幸咖啡、Starbucks星巴克等）
3. 颜色、品牌、标识等细节
4. 其他值得注意的特征

常见咖啡品牌参考：Luckin(瑞幸)、Starbucks(星巴克)、Costa、瑞幸咖啡等。
请尽可能详细和准确地描述，如识别出品牌请直接说明。'''
                print("\n🔍 图片识别 - 使用通用识别prompt")

            vision_result = vision_tool.analyze_image(
                image_path=image_path,
                prompt=ocr_prompt,
                prefer_model="auto"
            )

            if vision_result.get('success'):
                vision_description = vision_result.get('description', '')

                print(f"\n{'='*60}")
                print("🔍 调试：图片识别结果")
                print(f"识别内容长度: {len(vision_description)} 字符")
                print(f"前800字符: {vision_description[:800]}")
                print(f"{'='*60}\n")

                # 构建包含图片识别结果的完整消息
                # 使用更清晰的提示词，让AI知道这是它自己识别的内容
                if prompt:
                    combined_prompt = (
                        f"<vision_result>\n"
                        f"我通过视觉能力识别到的图片内容：\n"
                        f"{vision_description}\n"
                        f"</vision_result>\n\n"
                        f"用户问题：{prompt}\n\n"
                        f"请基于我识别到的图片内容回答用户的问题。"
                        f"如果识别到品牌相关的文字片段（如'ckin'、'kin'等），请结合常见品牌推理出完整品牌名。"
                        f"直接回答用户的实际问题，不要说'这不是XXX'。"
                    )
                else:
                    combined_prompt = (
                        f"<vision_result>\n"
                        f"我通过视觉能力识别到的图片内容：\n"
                        f"{vision_description}\n"
                        f"</vision_result>\n\n"
                        f"请分析并解释这张图片的内容。"
                    )

                # 智能判断是否需要保存图片记忆
                # 1. 用户明确要求记住
                # 2. 用户消息中提到了关系（我的、儿子、家人等）
                # 3. 图片内容包含重要信息（课程表、证件等）
                should_memorize = memorize  # 前端传递的参数

                if prompt:
                    # 检测用户是否明确要求记住
                    memorize_keywords = ['记住', '保存', '记下', '存一下', '记录']
                    # 检测是否提到了关系
                    relation_keywords = ['我的', '我儿子', '我女儿', '我妻子', '我老婆',
                                         '我老公', '我爸', '我妈', '家人', '孩子', '宝宝']

                    should_memorize = should_memorize or any(
                        kw in prompt for kw in memorize_keywords)
                    should_memorize = should_memorize or any(
                        kw in prompt for kw in relation_keywords)

                # 检测图片内容是否包含重要信息（课程表、表格等结构化数据）
                if not should_memorize:
                    important_content_indicators = [
                        '课程表', '时间表', '日程', '表格', '证件']
                    should_memorize = any(
                        ind in vision_description
                        for ind in important_content_indicators
                    )

                if should_memorize:
                    try:
                        print(f"💾 保存图片到记忆库，内容长度: {len(vision_description)}")
                        xiaole.memory.remember(
                            content=vision_description,
                            tag=f"image:{image_path.split('/')[-1]}"
                        )
                        print(f"✅ 图片记忆已保存: image:{image_path.split('/')[-1]}")
                        # 在提示中告知小乐这张图片已经保存
                        combined_prompt += "\n\n[系统提示：这张图片的内容我已经记住了，以后可以回忆]"
                    except Exception as e:
                        print(f"⚠️ 保存图片记忆失败: {e}")
                else:
                    print("ℹ️ 图片不需要记忆（普通照片）")

                # 使用包含图片内容的完整消息进行对话
                # 但保存到数据库时只保存用户的原始输入
                return xiaole.chat(
                    combined_prompt, session_id, user_id, response_style,
                    image_path=image_path,
                    original_user_prompt=prompt  # 用户的原始输入
                )
            else:
                # 图片识别失败，返回错误信息
                error_msg = vision_result.get('error', '未知错误')
                return {
                    'reply': f'❌ 图片识别失败: {error_msg}',
                    'session_id': session_id or 'error'
                }
        except Exception as e:
            return {
                'reply': f'❌ 图片处理出错: {str(e)}',
                'session_id': session_id or 'error'
            }

    # 没有图片，正常对话
    return xiaole.chat(prompt, session_id, user_id, response_style)


@app.get("/sessions")
def get_sessions(user_id: str = "default_user", limit: int = 10):
    """获取用户的对话会话列表"""
    sessions = xiaole.conversation.get_recent_sessions(user_id, limit)
    return {"sessions": sessions}


@app.get("/session/{session_id}")
def get_session(session_id: str):
    """获取会话详情"""
    stats = xiaole.conversation.get_session_stats(session_id)
    history = xiaole.conversation.get_history(session_id, limit=50)

    if not stats:
        return {"error": "Session not found"}, 404

    return {
        "session_id": stats["session_id"],
        "title": stats["title"],
        "message_count": stats["message_count"],
        "created_at": stats["created_at"],
        "updated_at": stats["updated_at"],
        "messages": history  # 改为messages，与前端期望的字段名一致
    }


@app.delete("/session/{session_id}")
def delete_session(session_id: str):
    """删除会话"""
    xiaole.conversation.delete_session(session_id)
    return {"message": "Session deleted"}


# v0.3.0 用户行为分析 API
@app.get("/analytics/behavior")
def get_behavior_analytics(
    user_id: str = "default_user",
    days: int = 30
):
    """获取用户行为分析报告"""
    report = xiaole.behavior_analyzer.generate_behavior_report(user_id, days)
    if not report or not report.get("conversation_stats"):
        return {"error": "No data available"}, 404
    return report


@app.get("/analytics/activity")
def get_activity_pattern(user_id: str = "default_user", days: int = 30):
    """获取用户活跃时间模式"""
    pattern = xiaole.behavior_analyzer.get_user_activity_pattern(user_id, days)
    if not pattern:
        return {"error": "No data available"}, 404
    return pattern


@app.get("/analytics/topics")
def get_topic_preferences(user_id: str = "default_user", days: int = 30):
    """获取用户话题偏好"""
    topics = xiaole.behavior_analyzer.get_topic_preferences(user_id, days)
    if not topics:
        return {"error": "No data available"}, 404
    return topics


# v0.3.0 模式学习 API
@app.get("/patterns/frequent")
def get_frequent_words(
    user_id: str = "default_user",
    limit: int = 20
):
    """获取用户高频词列表"""
    words = xiaole.pattern_learner.get_frequent_words(user_id, limit)
    return {"user_id": user_id, "frequent_words": words}


@app.get("/patterns/common_questions")
def get_common_questions(
    user_id: str = "default_user",
    limit: int = 10
):
    """获取用户常见问题分类"""
    questions = xiaole.pattern_learner.get_common_questions(user_id, limit)
    return {"user_id": user_id, "common_questions": questions}


@app.get("/patterns/insights")
def get_learning_insights(user_id: str = "default_user"):
    """获取模式学习统计洞察"""
    insights = xiaole.pattern_learner.get_learning_insights(user_id)
    return insights


# v0.3.0 记忆冲突检测 API
@app.get("/memory/conflicts")
def check_memory_conflicts(tag: str = "facts", limit: int = 100):
    """检测记忆冲突"""
    conflicts = conflict_detector.detect_conflicts(tag, limit)
    return {
        "has_conflicts": len(conflicts) > 0,
        "total": len(conflicts),
        "conflicts": conflicts
    }


@app.get("/memory/conflicts/summary")
def get_conflict_summary():
    """获取冲突摘要"""
    return conflict_detector.get_conflict_summary()


@app.get("/memory/conflicts/report")
def get_conflict_report():
    """获取可读的冲突报告"""
    report = conflict_detector.generate_conflict_report()
    return {"report": report}


# v0.3.0 主动问答 API
@app.get("/proactive/pending/{session_id}")
def get_pending_followups(session_id: str, limit: int = 5):
    """获取待追问的问题列表"""
    questions = proactive_qa.get_pending_followups(session_id, limit)
    return {
        "session_id": session_id,
        "pending_count": len(questions),
        "questions": questions
    }


@app.get("/proactive/history")
def get_followup_history(
    session_id: str = None,
    user_id: str = None,
    limit: int = 20
):
    """获取追问历史记录"""
    history = proactive_qa.get_followup_history(session_id, user_id, limit)
    return {
        "total": len(history),
        "history": history
    }


@app.post("/proactive/mark_asked/{question_id}")
def mark_followup_asked(question_id: int):
    """标记追问已发送"""
    proactive_qa.mark_followup_asked(question_id)
    return {"message": "Followup marked as asked"}


@app.get("/proactive/analyze/{session_id}")
def analyze_session(session_id: str, user_id: str = "default_user"):
    """分析会话，返回需要追问的问题"""
    analysis = proactive_qa.analyze_conversation(session_id, user_id)
    return analysis


# v0.4.0 工具调用 API
@app.get("/tools/list")
def list_tools(category: str = None, enabled_only: bool = True):
    """列出所有可用工具"""
    tools = xiaole.tool_registry.list_tools(category, enabled_only)
    return {
        "total": len(tools),
        "tools": tools
    }


@app.post("/tools/execute")
async def execute_tool(
    tool_name: str,
    params: dict,
    user_id: str = "default_user",
    session_id: str = None
):
    """执行指定工具"""
    result = await xiaole.tool_registry.execute(
        tool_name=tool_name,
        params=params,
        user_id=user_id,
        session_id=session_id
    )
    return result


@app.get("/tools/history")
def get_tool_history(
    user_id: str = "default_user",
    session_id: str = None,
    limit: int = 20
):
    """获取工具执行历史"""
    from db_setup import SessionLocal, ToolExecution

    db = SessionLocal()
    try:
        query = db.query(ToolExecution).filter(
            ToolExecution.user_id == user_id
        )

        if session_id:
            query = query.filter(ToolExecution.session_id == session_id)

        executions = query.order_by(
            ToolExecution.executed_at.desc()
        ).limit(limit).all()

        return {
            "total": len(executions),
            "history": [
                {
                    "execution_id": e.execution_id,
                    "tool_name": e.tool_name,
                    "success": e.success,
                    "execution_time": e.execution_time,
                    "executed_at": e.executed_at.isoformat(),
                    "error_message": e.error_message
                }
                for e in executions
            ]
        }
    finally:
        db.close()


# ============ v0.5.0 主动提醒系统 API ============

@app.post("/api/reminders")
async def create_reminder(reminder: ReminderCreate):
    """创建新提醒"""
    try:
        result = await reminder_manager.create_reminder(
            user_id=reminder.user_id,
            reminder_type=reminder.reminder_type,
            trigger_condition=reminder.trigger_condition,
            content=reminder.content,
            title=reminder.title,
            priority=reminder.priority,
            repeat=reminder.repeat,
            repeat_interval=reminder.repeat_interval
        )
        return {
            "success": True,
            "reminder": result
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@app.get("/api/reminders")
async def get_reminders(
    user_id: str = "default_user",
    enabled_only: bool = True,
    reminder_type: str = None
):
    """获取用户提醒列表"""
    reminders = await reminder_manager.get_user_reminders(
        user_id=user_id,
        enabled_only=enabled_only,
        reminder_type=reminder_type
    )
    return {
        "total": len(reminders),
        "reminders": reminders
    }


@app.get("/api/reminders/{reminder_id}")
async def get_reminder(reminder_id: int, user_id: str = "default_user"):
    """获取单个提醒详情"""
    reminders = await reminder_manager.get_user_reminders(user_id)
    reminder = next(
        (r for r in reminders if r['reminder_id'] == reminder_id), None)

    if not reminder:
        return {"error": "Reminder not found"}, 404

    return reminder


@app.put("/api/reminders/{reminder_id}")
async def update_reminder(
    reminder_id: int,
    content: str = None,
    title: str = None,
    priority: int = None,
    enabled: bool = None,
    trigger_condition: dict = None
):
    """更新提醒"""
    updates = {}
    if content is not None:
        updates['content'] = content
    if title is not None:
        updates['title'] = title
    if priority is not None:
        updates['priority'] = priority
    if enabled is not None:
        updates['enabled'] = enabled
    if trigger_condition is not None:
        import json
        updates['trigger_condition'] = json.dumps(trigger_condition)

    success = await reminder_manager.update_reminder(reminder_id, **updates)

    return {
        "success": success,
        "message": "Reminder updated" if success else "Update failed"
    }


@app.delete("/api/reminders/{reminder_id}")
async def delete_reminder(reminder_id: int):
    """删除提醒"""
    success = await reminder_manager.delete_reminder(reminder_id)
    return {
        "success": success,
        "message": "Reminder deleted" if success else "Delete failed"
    }


@app.post("/api/reminders/{reminder_id}/toggle")
async def toggle_reminder(reminder_id: int, user_id: str = "default_user"):
    """启用/禁用提醒"""
    # 先获取当前状态
    reminders = await reminder_manager.get_user_reminders(
        user_id,
        enabled_only=False
    )
    reminder = next(
        (r for r in reminders if r['reminder_id'] == reminder_id), None
    )

    if not reminder:
        return {"error": "Reminder not found", "success": False}

    # 切换状态
    new_enabled = not reminder.get('enabled', True)
    success = await reminder_manager.update_reminder(
        reminder_id,
        enabled=new_enabled
    )

    return {
        "success": success,
        "enabled": new_enabled,
        "message": f"Reminder {'enabled' if new_enabled else 'disabled'}"
    }


@app.post("/api/reminders/{reminder_id}/trigger")
async def trigger_reminder_manually(reminder_id: int):
    """手动触发提醒（测试用） - 只推送通知不写历史"""
    success = await reminder_manager.check_and_notify_reminder(reminder_id)
    return {
        "success": success,
        "message": "Reminder notified" if success else "Notify failed"
    }


@app.post("/api/reminders/{reminder_id}/snooze")
async def snooze_reminder(reminder_id: int, minutes: int = 5):
    """延迟提醒（稍后提醒）- 不写入历史，只延迟触发时间"""
    from datetime import datetime, timedelta
    import json
    import psycopg2
    from psycopg2.extras import RealDictCursor

    # 获取数据库连接
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST', '192.168.88.188'),
        port=os.getenv('DB_PORT', '5432'),
        database=os.getenv('DB_NAME', 'xiaole_ai'),
        user=os.getenv('DB_USER', 'xiaole_user'),
        password=os.getenv('DB_PASS', 'Xiaole2025User'),
        client_encoding='UTF8'
    )

    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # 获取当前提醒
            cur.execute(
                "SELECT * FROM reminders WHERE reminder_id = %s",
                (reminder_id,)
            )
            reminder = cur.fetchone()

            if not reminder:
                return {"success": False, "error": "Reminder not found"}

            # 计算新的触发时间（当前时间 + minutes分钟）
            new_trigger_time = datetime.now() + timedelta(minutes=minutes)

            # 更新trigger_condition
            trigger_condition = json.loads(reminder['trigger_condition'])
            new_time_str = new_trigger_time.strftime('%Y-%m-%d %H:%M:%S')
            trigger_condition['datetime'] = new_time_str

            success = await reminder_manager.update_reminder(
                reminder_id,
                trigger_condition=json.dumps(trigger_condition),
                last_triggered=None,  # 清除last_triggered，允许重新触发
                enabled=True  # 确保提醒是启用状态
            )

            return {
                "success": success,
                "new_trigger_time": new_time_str,
                "message": (
                    f"Reminder snoozed for {minutes} minutes"
                    if success else "Snooze failed"
                )
            }
    finally:
        conn.close()


@app.post("/api/reminders/{reminder_id}/confirm")
async def confirm_reminder(reminder_id: int):
    """用户确认提醒（点击"已知道"） - 写入历史并禁用非重复提醒"""
    success = await reminder_manager.confirm_reminder(reminder_id)

    return {
        "success": success,
        "message": "Reminder confirmed" if success else "Confirm failed"
    }


@app.get("/api/reminders/history/{user_id}")
async def get_reminder_history(
    user_id: str,
    limit: int = 50
):
    """获取提醒历史"""
    history = await reminder_manager.get_reminder_history(user_id, limit)
    return {
        "total": len(history),
        "history": history
    }


@app.post("/api/reminders/check")
async def check_reminders(user_id: str = "default_user"):
    """手动检查并触发提醒"""
    # 检查时间提醒
    time_triggered = await reminder_manager.check_time_reminders(user_id)

    # 检查行为提醒
    behavior_triggered = await reminder_manager.check_behavior_reminders(
        user_id
    )

    all_triggered = time_triggered + behavior_triggered

    # 触发所有需要触发的提醒（只推送通知）
    results = []
    for reminder in all_triggered:
        success = await reminder_manager.check_and_notify_reminder(
            reminder['reminder_id']
        )
        results.append({
            "reminder_id": reminder['reminder_id'],
            "title": reminder.get('title', 'Untitled'),
            "content": reminder['content'],
            "notified": success
        })

    return {
        "total_checked": len(all_triggered),
        "triggered": results
    }


@app.get("/api/scheduler/status")
def get_scheduler_status():
    """获取调度器状态"""
    return scheduler.get_status()


@app.post("/api/scheduler/start")
def start_scheduler():
    """启动调度器"""
    scheduler.start()
    return {"message": "Scheduler started", "status": scheduler.get_status()}


@app.post("/api/scheduler/stop")
def stop_scheduler():
    """停止调度器"""
    scheduler.stop()
    return {"message": "Scheduler stopped", "status": scheduler.get_status()}


# ========================================
# v0.7.0: 课程表管理
# ========================================

@app.get("/api/schedule")
async def get_schedule(user_id: str = "default_user"):
    """
    获取用户课程表

    Args:
        user_id: 用户ID

    Returns:
        dict: 课程表数据
    """
    try:
        # 尝试从数据库查询课程表记忆
        memory_manager = MemoryManager()

        # 查询image或facts类型的课程表记忆
        from db_setup import Memory
        from sqlalchemy import or_

        # 优先查询image类型的课程表
        memories = memory_manager.session.query(Memory).filter(
            Memory.tag.like('image:%'),
            or_(
                Memory.content.like('%周一：晨读%'),
                Memory.content.like('%周一：第1节%'),
                Memory.content.like('%第1节-无课%')
            )
        ).order_by(Memory.created_at.desc()).limit(1).all()

        # 如果没找到image，再查schedule类型
        if not memories:
            memories = memory_manager.session.query(Memory).filter(
                Memory.tag == 'schedule'
            ).order_by(Memory.created_at.desc()).limit(1).all()

        if memories:
            content = memories[0].content

            # 解析课程表内容
            schedule = {
                "periods": ['第1节', '第2节', '第3节', '第4节', '第5节', '第6节', '第7节'],
                "weekdays": ['周一', '周二', '周三', '周四', '周五'],
                "courses": {}
            }

            # 解析文本（格式：周一：晨读-科学(5), 第1节-无课, ...）
            lines = content.split('\n')
            import re

            for line in lines:
                # 匹配 "周X：..." 格式
                match = re.match(r'^(周[一二三四五])[:：]\s*(.*)', line)
                if match:
                    day = match.group(1)
                    course_info = match.group(2)

                    # 按逗号分割
                    items = course_info.split(',')

                    for item in items:
                        item = item.strip()
                        # 解析 "第X节-课程" 或 "晨读-课程"
                        if '第' in item and '节' in item:
                            # 提取节次
                            period_match = re.search(r'第(\d+)节', item)
                            if period_match:
                                period_num = int(period_match.group(1))
                                # 提取课程名
                                course_match = re.search(r'-\s*(.+)', item)
                                if course_match:
                                    course_name = course_match.group(1).strip()
                                    if course_name and course_name != '无课':
                                        # period_num-1 因为第1节对应index 0
                                        key = f"{period_num-1}_{day}"
                                        schedule["courses"][key] = course_name

            return {
                "success": True,
                "schedule": schedule
            }        # 如果没有找到，返回空课程表
        return {
            "success": True,
            "schedule": {
                "periods": ['第1节', '第2节', '第3节', '第4节', '第5节', '第6节', '第7节'],
                "weekdays": ['周一', '周二', '周三', '周四', '周五'],
                "courses": {}
            }
        }

    except Exception as e:
        print(f"❌ 获取课程表失败: {e}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e)
        }


@app.post("/api/schedule")
async def save_schedule(request: dict):
    """
    保存用户课程表

    Args:
        request: 包含user_id和schedule的请求体

    Returns:
        dict: 保存结果
    """
    try:
        # user_id = request.get("user_id", "default_user")  # 暂未使用
        schedule = request.get("schedule", {})

        if not schedule:
            return {
                "success": False,
                "error": "课程表数据为空"
            }

        # 将课程表转换为文本格式保存到记忆
        memory_manager = MemoryManager()

        # 按天组织课程
        courses_by_day = {}
        for key, course in schedule.get("courses", {}).items():
            period_index, day = key.split('_')
            if day not in courses_by_day:
                courses_by_day[day] = {}
            courses_by_day[day][int(period_index)] = course

        # 生成课程表文本
        lines = []
        for day in schedule.get("weekdays", []):
            if day in courses_by_day:
                courses = []
                for i in range(len(schedule.get("periods", []))):
                    course = courses_by_day[day].get(i, "无课")
                    courses.append(course)
                lines.append(f"{day}：{'-'.join(courses)}")

        content = "\n".join(lines)

        # 删除旧的课程表记忆
        from db_setup import Memory
        old_memories = memory_manager.session.query(Memory).filter(
            Memory.tag == 'schedule'
        ).all()

        for mem in old_memories:
            memory_manager.session.delete(mem)

        # 保存新的课程表
        new_memory = Memory(
            content=f"用户课程表：\n{content}",
            tag="schedule"
        )
        memory_manager.session.add(new_memory)
        memory_manager.session.commit()

        return {
            "success": True,
            "message": "课程表保存成功"
        }

    except Exception as e:
        print(f"❌ 保存课程表失败: {e}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e)
        }


# ========================================
# v0.6.0 Phase 4: 多模态支持 - 图片识别
# ========================================

@app.post("/api/vision/upload")
async def upload_image(file: UploadFile = File(...)):
    """
    上传图片文件

    Args:
        file: 上传的图片文件

    Returns:
        dict: 包含文件路径的响应
    """
    from vision_tool import VisionTool

    try:
        # 检查文件名
        if not file.filename:
            return {
                "success": False,
                "error": "文件名缺失"
            }

        # 读取文件数据
        file_data = await file.read()

        # 保存文件
        vision_tool = VisionTool()
        success, result = vision_tool.save_upload(file_data, file.filename)

        if success:
            return {
                "success": True,
                "file_path": result,
                "filename": file.filename,
                "size": len(file_data)
            }
        else:
            return {
                "success": False,
                "error": result
            }

    except Exception as e:
        return {
            "success": False,
            "error": f"上传失败: {str(e)}"
        }


# ========================================
# v0.8.0 语音识别接口（百度API）
# ========================================

@app.post("/api/voice/recognize")
async def voice_recognize(file: UploadFile = File(...)):
    """
    语音识别接口（使用百度API）

    Args:
        file: 音频文件（wav/pcm/amr/m4a格式）

    Returns:
        dict: {"success": True, "text": "识别结果"}
    """
    try:
        # 检查服务是否可用
        if not baidu_voice_tool.is_enabled():
            return {
                "success": False,
                "error": "百度语音服务未配置，请设置环境变量"
            }

        # 读取音频数据
        audio_data = await file.read()

        # 检测音频格式
        filename = file.filename.lower() if file.filename else ""
        if filename.endswith('.wav'):
            format_type = 'wav'
        elif filename.endswith('.pcm'):
            format_type = 'pcm'
        elif filename.endswith('.amr'):
            format_type = 'amr'
        elif filename.endswith('.m4a'):
            format_type = 'm4a'
        else:
            format_type = 'wav'  # 默认wav

        # 调用识别
        result = await baidu_voice_tool.recognize(
            audio_data,
            format=format_type,
            rate=16000
        )

        return result

    except Exception as e:
        return {
            "success": False,
            "error": f"语音识别失败: {str(e)}"
        }


@app.get("/api/voice/status")
def voice_status(detailed: bool = False):
    """检查语音服务状态

    Args:
        detailed: 是否返回详细脱敏后的密钥状态
    """
    return baidu_voice_tool.get_status(detailed)


@app.post("/api/voice/synthesize")
async def voice_synthesize(req: TTSRequest):
    """文本转语音（百度TTS）

    Args:
        req: TTSRequest，请求体

    Returns:
        JSON，包含 base64 音频与 mime 类型
    """
    try:
        if not baidu_voice_tool.is_enabled():
            return {
                "success": False,
                "error": "百度语音服务未配置，请设置环境变量"
            }

        audio_bytes = await baidu_voice_tool.synthesize(
            text=req.text,
            person=req.person,
            speed=req.speed,
            pitch=req.pitch,
            volume=req.volume,
            audio_format=req.audio_format,
        )

        if not audio_bytes:
            return {
                "success": False,
                "error": "语音合成失败"
            }

        import base64

        mime = "audio/mpeg"
        fmt = (req.audio_format or "mp3").lower()
        if fmt == "wav":
            mime = "audio/wav"
        elif fmt == "pcm":
            mime = "audio/x-pcm"

        b64 = base64.b64encode(audio_bytes).decode("utf-8")
        return {
            "success": True,
            "audio_base64": b64,
            "mime": mime,
            "format": fmt,
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"语音合成异常: {str(e)}"
        }


@app.post("/api/vision/analyze")
def analyze_image(request: dict):
    """
    分析图片内容

    Args:
        request: JSON请求体，包含:
            - image_path: 图片文件路径
            - prompt: 分析提示语（可选）
            - model: 优先使用的模型（可选，默认"auto"）

    Returns:
        dict: 图片分析结果
    """
    from vision_tool import VisionTool

    try:
        image_path = request.get('image_path')
        prompt = request.get('prompt')
        model = request.get('model', 'auto')

        if not image_path:
            return {
                "success": False,
                "error": "缺少 image_path 参数"
            }

        vision_tool = VisionTool()
        result = vision_tool.analyze_image(image_path, prompt, model)
        return result

    except Exception as e:
        return {
            "success": False,
            "error": f"分析失败: {str(e)}"
        }


# ==================== v0.8.0 任务管理API ====================

@app.post("/api/tasks")
def create_task_api(request: dict):
    """
    创建任务

    Args:
        request: {
            "user_id": "用户ID",
            "session_id": "会话ID",
            "title": "任务标题",
            "description": "任务描述",
            "priority": 0
        }
    """
    try:
        user_id = request.get('user_id', 'default_user')
        session_id = request.get('session_id')
        title = request.get('title')
        description = request.get('description', '')
        priority = request.get('priority', 0)

        if not title:
            return {"success": False, "error": "缺少任务标题"}

        task_id = xiaole.task_manager.create_task(
            user_id=user_id,
            session_id=session_id,
            title=title,
            description=description,
            priority=priority
        )

        return {
            "success": True,
            "task_id": task_id
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@app.get("/api/tasks/{task_id}")
def get_task_api(task_id: int):
    """获取任务详情"""
    try:
        task = xiaole.task_manager.get_task(task_id)
        if not task:
            return {"success": False, "error": "任务不存在"}

        # 获取步骤
        steps = xiaole.task_manager.get_task_steps(task_id)

        return {
            "success": True,
            "task": dict(task),
            "steps": steps
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@app.get("/api/sessions/{session_id}/tasks")
def get_session_tasks(session_id: str, status: str = None):
    """获取会话的所有任务"""
    try:
        tasks = xiaole.task_manager.get_tasks_by_session(
            session_id=session_id,
            status=status
        )

        return {
            "success": True,
            "tasks": [dict(t) for t in tasks]
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@app.get("/api/users/{user_id}/tasks")
def get_user_tasks(user_id: str, status: str = None, limit: int = 50):
    """获取用户的所有任务"""
    try:
        tasks = xiaole.task_manager.get_tasks_by_user(
            user_id=user_id,
            status=status,
            limit=limit
        )

        return {
            "success": True,
            "tasks": [dict(t) for t in tasks]
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@app.put("/api/tasks/{task_id}/status")
def update_task_status_api(task_id: int, request: dict):
    """更新任务状态"""
    try:
        status = request.get('status')
        if not status:
            return {"success": False, "error": "缺少状态参数"}

        success = xiaole.task_manager.update_task_status(
            task_id=task_id,
            status=status
        )

        return {
            "success": success
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@app.post("/api/tasks/{task_id}/execute")
def execute_task_api(task_id: int, request: dict):
    """执行任务"""
    try:
        user_id = request.get('user_id', 'default_user')
        session_id = request.get('session_id', '')

        result = xiaole.task_executor.execute_task(
            task_id=task_id,
            user_id=user_id,
            session_id=session_id
        )

        return result
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@app.post("/api/tasks/{task_id}/cancel")
def cancel_task_api(task_id: int):
    """取消任务"""
    try:
        result = xiaole.task_executor.cancel_task(task_id)
        return result
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@app.delete("/api/tasks/{task_id}")
def delete_task_api(task_id: int):
    """删除任务"""
    try:
        success = xiaole.task_manager.delete_task(task_id)
        return {
            "success": success
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@app.get("/api/tasks/stats/{user_id}")
def get_task_stats(user_id: str):
    """获取用户任务统计"""
    try:
        stats = xiaole.task_manager.get_task_statistics(user_id)
        return {
            "success": True,
            "stats": stats
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


# ==================== v0.8.0 Phase 3: 文档总结API ====================

# 数据库配置
DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'port': int(os.getenv('DB_PORT', 5432)),
    'database': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASS')
}

# 初始化文档总结器
document_summarizer = DocumentSummarizer(
    db_config=DB_CONFIG,
    upload_dir=UPLOADS_DIR
)


@app.post("/api/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    user_id: str = "default_user",
    session_id: str = None
):
    """
    上传文档并自动总结

    支持格式: PDF, DOCX, TXT, MD
    最大大小: 10MB
    """
    start_time = time.time()
    doc_id = None

    try:
        # 验证文件
        file_size = 0
        file_content = await file.read()
        file_size = len(file_content)

        valid, file_type, error_msg = document_summarizer.validate_file(
            file.filename, file_size
        )

        if not valid:
            return {
                "success": False,
                "error": error_msg
            }

        # 生成唯一文件名
        timestamp = int(time.time())
        safe_filename = f"{timestamp}_{file.filename}"
        file_path = os.path.join(UPLOADS_DIR, safe_filename)

        # 保存文件
        with open(file_path, 'wb') as f:
            f.write(file_content)

        # 创建数据库记录
        doc_id = document_summarizer.create_document_record(
            user_id=user_id,
            session_id=session_id or "",
            filename=safe_filename,
            original_filename=file.filename,
            file_type=file_type,
            file_size=file_size,
            file_path=file_path
        )

        # 提取文本
        try:
            content = document_summarizer.extract_text(file_path, file_type)
            chunks = document_summarizer.split_text(content)

            # 更新内容
            document_summarizer.update_document_content(
                doc_id, content, len(chunks)
            )

            # 生成总结
            if len(chunks) == 1:
                # 单块直接总结
                summary = document_summarizer.summarize_chunk(
                    chunks[0],
                    xiaole._call_deepseek
                )
            else:
                # 多块：先总结各块，再合并
                chunk_summaries = []
                for i, chunk in enumerate(chunks):
                    print(f"📝 总结第 {i+1}/{len(chunks)} 块...")
                    chunk_summary = document_summarizer.summarize_chunk(
                        chunk,
                        xiaole._call_deepseek
                    )
                    chunk_summaries.append(chunk_summary)

                # 合并总结
                combined_text = "\n\n".join(chunk_summaries)
                if len(combined_text) > 4000:
                    # 再次总结
                    summary = document_summarizer.summarize_chunk(
                        combined_text,
                        xiaole._call_deepseek
                    )
                else:
                    summary = combined_text

            # 提取关键要点
            key_points = document_summarizer.extract_key_points(
                content,
                xiaole._call_deepseek
            )

            # 更新总结结果
            processing_time = time.time() - start_time
            document_summarizer.update_document_summary(
                doc_id, summary, key_points, processing_time
            )

            return {
                "success": True,
                "document_id": doc_id,
                "summary": summary,
                "key_points": key_points,
                "processing_time": processing_time,
                "content_length": len(content),
                "chunk_count": len(chunks)
            }

        except Exception as e:
            # 标记处理失败
            if doc_id:
                document_summarizer.mark_document_failed(doc_id, str(e))
            raise

    except Exception as e:
        print(f"❌ 文档处理失败: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@app.get("/api/documents/{doc_id}")
def get_document_detail(doc_id: int):
    """获取文档详情"""
    try:
        doc = document_summarizer.get_document(doc_id)
        if not doc:
            return {
                "success": False,
                "error": "文档不存在"
            }

        return {
            "success": True,
            "document": doc
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@app.get("/api/users/{user_id}/documents")
def get_user_documents_api(
    user_id: str,
    status: str = None,
    limit: int = 50
):
    """获取用户的文档列表"""
    try:
        docs = document_summarizer.get_user_documents(
            user_id, status, limit
        )

        return {
            "success": True,
            "documents": docs,
            "count": len(docs)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@app.get("/api/documents/{doc_id}/export")
def export_document_api(doc_id: int, format: str = "md"):
    """导出文档总结"""
    try:
        doc = document_summarizer.get_document(doc_id)
        if not doc:
            raise HTTPException(status_code=404, detail="文档不存在")

        # 生成Markdown内容
        content = f"""# {doc['filename']}

## 文档信息
- 文件大小: {doc['file_size'] / 1024:.2f} KB
- 处理时间: {doc['processing_time']:.1f}秒
- 分块数量: {doc['chunk_count']}

## 关键要点

"""
        # 添加关键要点
        key_points = doc.get('key_points', [])
        if isinstance(key_points, str):
            try:
                key_points = json.loads(key_points)
            except Exception:
                key_points = []

        for i, point in enumerate(key_points, 1):
            content += f"{i}. {point}\n"

        content += f"\n## 智能总结\n\n{doc['summary']}\n"

        # 返回文件下载
        # URL编码文件名以支持中文
        filename = f"{doc['filename']}_summary.md"
        encoded_filename = quote(filename)
        return Response(
            content=content.encode('utf-8'),
            media_type="text/markdown; charset=utf-8",
            headers={
                "Content-Disposition": (
                    f"attachment; filename={encoded_filename}; "
                    f"filename*=UTF-8''{encoded_filename}"
                )
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/documents/{doc_id}")
def delete_document_api(doc_id: int):
    """删除文档"""
    try:
        success = document_summarizer.delete_document(doc_id)
        return {
            "success": success
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


# ==================== v0.8.1 用户反馈系统 ====================

@app.post("/api/feedback")
async def submit_feedback(feedback: FeedbackRequest):
    """
    提交用户反馈
    用于记录用户对AI回复的评价，帮助改进模型
    """
    try:
        from reminder_manager import get_db_connection

        conn = get_db_connection()
        cursor = conn.cursor()

        # 插入反馈记录
        cursor.execute("""
            INSERT INTO message_feedback 
            (session_id, user_id, message_content, feedback_type, created_at)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING feedback_id
        """, (
            feedback.session_id,
            feedback.user_id,
            feedback.message_content,
            feedback.feedback_type,
            feedback.timestamp
        ))

        feedback_id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        conn.close()

        # 如果是负面反馈，可以触发额外的学习机制
        if feedback.feedback_type == 'bad':
            # TODO: 未来可以在这里添加自动改进逻辑
            # 例如：分析错误模式、调整提示词等
            pass

        return {
            "success": True,
            "feedback_id": feedback_id,
            "message": "反馈已记录，感谢您的反馈！"
        }

    except Exception as e:
        print(f"❌ 反馈提交失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/feedback/stats")
def get_feedback_stats():
    """
    获取反馈统计数据
    用于分析AI回复质量
    """
    try:
        from reminder_manager import get_db_connection

        conn = get_db_connection()
        cursor = conn.cursor()

        # 获取总体统计
        cursor.execute("""
            SELECT 
                feedback_type,
                COUNT(*) as count,
                DATE(created_at) as date
            FROM message_feedback
            WHERE created_at >= NOW() - INTERVAL '30 days'
            GROUP BY feedback_type, DATE(created_at)
            ORDER BY date DESC
        """)

        stats = []
        for row in cursor.fetchall():
            stats.append({
                "feedback_type": row[0],
                "count": row[1],
                "date": str(row[2])
            })

        # 获取总体好评率
        cursor.execute("""
            SELECT 
                SUM(CASE WHEN feedback_type = 'good' THEN 1 ELSE 0 END) as good_count,
                SUM(CASE WHEN feedback_type = 'bad' THEN 1 ELSE 0 END) as bad_count,
                COUNT(*) as total_count
            FROM message_feedback
        """)

        row = cursor.fetchone()
        summary = {
            "good_count": row[0] or 0,
            "bad_count": row[1] or 0,
            "total_count": row[2] or 0,
            "satisfaction_rate": round((row[0] or 0) / (row[2] or 1) * 100, 2) if row[2] else 0
        }

        cursor.close()
        conn.close()

        return {
            "success": True,
            "stats": stats,
            "summary": summary
        }

    except Exception as e:
        print(f"❌ 获取反馈统计失败: {e}")
        return {
            "success": False,
            "error": str(e)
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
