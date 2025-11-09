from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from agent import XiaoLeAgent
from conflict_detector import ConflictDetector
from proactive_qa import ProactiveQA  # v0.3.0 主动问答
from reminder_manager import get_reminder_manager  # v0.5.0 主动提醒
from scheduler import get_scheduler  # v0.5.0 定时调度

app = FastAPI(
    title="小乐AI管家",
    version="0.5.0-dev",
    description="支持主动提醒的AI助手 - Active Perception层开发中"
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

xiaole = XiaoLeAgent()
conflict_detector = ConflictDetector()  # v0.3.0 冲突检测器
proactive_qa = ProactiveQA()  # v0.3.0 主动问答分析器
reminder_manager = get_reminder_manager()  # v0.5.0 提醒管理器
scheduler = get_scheduler()  # v0.5.0 定时调度器


@app.on_event("startup")
async def startup_event():
    """应用启动时初始化"""
    # 启动提醒调度器
    scheduler.start()
    print("✅ 提醒调度器已启动")


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时清理"""
    # 停止提醒调度器
    scheduler.stop()
    print("👋 提醒调度器已停止")


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


# 对话会话管理 API
@app.post("/chat")
def chat(prompt: str, session_id: str = None, user_id: str = "default_user"):
    """支持上下文的对话接口"""
    return xiaole.chat(prompt, session_id, user_id)


@app.get("/sessions")
def get_sessions(user_id: str = "default_user", limit: int = 10):
    """获取用户的对话会话列表"""
    return {"sessions": xiaole.conversation.get_recent_sessions(user_id, limit)}


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
        "history": history
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
async def create_reminder(
    user_id: str = "default_user",
    reminder_type: str = "time",
    trigger_condition: dict = None,
    content: str = "",
    title: str = None,
    priority: int = 3,
    repeat: bool = False,
    repeat_interval: int = None
):
    """创建新提醒"""
    try:
        reminder = await reminder_manager.create_reminder(
            user_id=user_id,
            reminder_type=reminder_type,
            trigger_condition=trigger_condition or {},
            content=content,
            title=title,
            priority=priority,
            repeat=repeat,
            repeat_interval=repeat_interval
        )
        return {
            "success": True,
            "reminder": reminder
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
    reminder = next((r for r in reminders if r['reminder_id'] == reminder_id), None)
    
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
async def toggle_reminder(reminder_id: int):
    """启用/禁用提醒"""
    # 先获取当前状态
    reminders = await reminder_manager.get_user_reminders(
        "default_user",
        enabled_only=False
    )
    reminder = next((r for r in reminders if r['reminder_id'] == reminder_id), None)
    
    if not reminder:
        return {"error": "Reminder not found"}, 404
    
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


@app.get("/api/reminders/history")
async def get_reminder_history(
    user_id: str = "default_user",
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
    behavior_triggered = await reminder_manager.check_behavior_reminders(user_id)
    
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
