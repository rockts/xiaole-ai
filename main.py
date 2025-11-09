from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from agent import XiaoLeAgent

app = FastAPI(title="小乐AI管家")

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
