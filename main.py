from fastapi import FastAPI, WebSocket, WebSocketDisconnect, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from agent import XiaoLeAgent
from memory import MemoryManager
from conflict_detector import ConflictDetector
from proactive_qa import ProactiveQA  # v0.3.0 主动问答
from reminder_manager import get_reminder_manager  # v0.5.0 主动提醒
from scheduler import get_scheduler  # v0.5.0 定时调度

app = FastAPI(
    title="小乐AI管家",
    version="0.5.0",
    description="支持主动提醒的AI助手 - Active Perception层已完成"
)

# 配置CORS，允许网页访问API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有HTTP方法
    allow_headers=["*"],  # 允许所有请求头
)

# 挂载静态文件目录
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


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
            # 调用图片识别 - 使用详细的表格识别prompt
            ocr_prompt = '''这是一张学生课程表。请仔细识别表格中的内容：
1. 表头有：星期一、星期二、星期三、星期四、星期五
2. 左侧行标题有：晨读、第1节、第2节...第7节、午休、课后辅导
3. 每个格子可能有课程名称（如"科学"）和编号（如"(5)"）

请完整地列出每一天的所有课程，包括空格子（标注"无课"）。
格式：
周一：晨读-XX, 第1节-XX, 第2节-XX...
周二：...
依此类推。不要省略任何信息。'''

            print(f"\n🔍 图片识别 - 使用表格专用prompt")

            vision_result = vision_tool.analyze_image(
                image_path=image_path,
                prompt=ocr_prompt,
                prefer_model="auto"
            )

            if vision_result.get('success'):
                vision_description = vision_result.get('description', '')

                print(f"\n{'='*60}")
                print(f"🔍 调试：图片识别结果")
                print(f"识别内容长度: {len(vision_description)} 字符")
                print(f"前800字符: {vision_description[:800]}")
                print(f"{'='*60}\n")

                # 构建包含图片识别结果的完整消息
                if prompt:
                    combined_prompt = f"[图片内容]: {vision_description}\n\n[用户问题]: {prompt}"
                else:
                    combined_prompt = f"[图片内容]: {vision_description}"

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
                        ind in vision_description for ind in important_content_indicators)

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
                    print(f"ℹ️ 图片不需要记忆（普通照片）")

                # 使用包含图片内容的完整消息进行对话
                return xiaole.chat(combined_prompt, session_id, user_id, response_style)
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
    """手动触发提醒"""
    success = await reminder_manager.trigger_reminder(reminder_id)
    return {
        "success": success,
        "message": "Reminder triggered" if success else "Trigger failed"
    }


@app.post("/api/reminders/{reminder_id}/snooze")
async def snooze_reminder(reminder_id: int, minutes: int = 5):
    """延迟提醒（稍后提醒）"""
    from datetime import datetime, timedelta
    import json

    # 获取当前提醒
    conn = await reminder_manager.get_connection()
    reminder = await conn.fetchrow(
        "SELECT * FROM reminders WHERE reminder_id = $1",
        reminder_id
    )

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

    # 触发所有需要触发的提醒
    results = []
    for reminder in all_triggered:
        success = await reminder_manager.trigger_reminder(
            reminder['reminder_id']
        )
        results.append({
            "reminder_id": reminder['reminder_id'],
            "title": reminder.get('title', 'Untitled'),
            "content": reminder['content'],
            "triggered": success
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
        user_id = request.get("user_id", "default_user")
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
