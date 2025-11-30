from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import List
import os

from backend.routers import (
    auth, chat, memories, reminders, tasks,
    tools, analytics, documents, voice,
    schedule, feedback, faces, dashboard, vision
)
from backend.dependencies import (
    get_reminder_manager, get_scheduler, get_xiaole_agent
)
from backend.config import STATIC_DIR, UPLOADS_DIR, FILES_DIR
from backend.logger import logger

app = FastAPI(
    title="小乐 AI 管家",
    description="个人 AI 助手系统",
    version="0.8.0",
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 自定义StaticFiles类，禁用缓存


class NoCacheStaticFiles(StaticFiles):
    async def get_response(self, path: str, scope):
        response = await super().get_response(path, scope)
        response.headers["Cache-Control"] = (
            "no-cache, no-store, must-revalidate"
        )
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response


# 挂载静态文件目录
app.mount(
    "/static",
    NoCacheStaticFiles(directory=STATIC_DIR),
    name="static"
)
app.mount("/uploads", StaticFiles(directory=UPLOADS_DIR), name="uploads")
if os.path.exists(FILES_DIR):
    app.mount("/files", StaticFiles(directory=FILES_DIR), name="files")

# WebSocket连接管理器


class ConnectionManager:
    """管理WebSocket连接"""

    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """接受新连接"""
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"✅ WebSocket客户端已连接，当前连接数: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        """断开连接"""
        self.active_connections.remove(websocket)
        logger.info(f"👋 WebSocket客户端已断开，当前连接数: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        """广播消息给所有连接的客户端"""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"❌ 发送消息失败: {e}")
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
    reminder_manager = get_reminder_manager(websocket_manager.broadcast)

    # 设置事件循环，使 ReminderManager 可以在后台线程中推送 WebSocket 消息
    import asyncio
    loop = asyncio.get_event_loop()
    reminder_manager.set_loop(loop)

    # 启动提醒调度器
    scheduler = get_scheduler()
    scheduler.start()
    logger.info("✅ 提醒调度器已启动")
    logger.info("✅ WebSocket推送已配置")


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时清理"""
    scheduler = get_scheduler()
    scheduler.stop()
    logger.info("👋 提醒调度器已停止")


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket端点，用于实时推送提醒"""
    await websocket_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_json({"type": "pong"})
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket错误: {e}")
        websocket_manager.disconnect(websocket)

# 注册路由
app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(memories.router)
app.include_router(reminders.router)
app.include_router(tasks.router)
app.include_router(tools.router)
app.include_router(analytics.router)
app.include_router(documents.router)
app.include_router(voice.router)
app.include_router(schedule.router)
app.include_router(feedback.router)
app.include_router(faces.router)
app.include_router(dashboard.router)
app.include_router(vision.router)


@app.get("/")
def hello():
    return {"message": "你好，我是小乐AI管家，我已启动。"}


@app.post("/think")
def think(prompt: str):
    agent = get_xiaole_agent()
    return {"result": agent.think(prompt)}


@app.post("/act")
def act(command: str):
    agent = get_xiaole_agent()
    return {"result": agent.act(command)}


# 挂载前端静态文件(放在最后,避免覆盖API路由)
FRONTEND_DIST = os.path.join(os.path.dirname(
    os.path.dirname(__file__)), "frontend", "dist")
if os.path.exists(FRONTEND_DIST):
    from fastapi.responses import FileResponse, HTMLResponse

    @app.get("/assets/{path:path}")
    async def serve_assets(path: str):
        """提供前端资源文件"""
        asset_path = os.path.join(FRONTEND_DIST, "assets", path)
        if os.path.isfile(asset_path):
            return FileResponse(asset_path)
        raise HTTPException(status_code=404, detail="Asset not found")

    @app.get("/{full_path:path}", response_class=HTMLResponse)
    async def serve_frontend(full_path: str):
        """提供前端页面,所有未匹配的路由返回 index.html"""
        # 如果是API路由或特殊路径,跳过(让其他路由处理)
        if (full_path.startswith("api/") or
            full_path.startswith("docs") or
            full_path == "openapi.json" or
                full_path == "health"):
            raise HTTPException(status_code=404)

        # 尝试返回具体文件
        file_path = os.path.join(FRONTEND_DIST, full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)

        # SPA fallback: 返回 index.html
        index_path = os.path.join(FRONTEND_DIST, "index.html")
        if os.path.isfile(index_path):
            return FileResponse(index_path)

        raise HTTPException(status_code=404, detail="Frontend not found")

    logger.info(f"✅ 前端静态文件已挂载: {FRONTEND_DIST}")
else:
    logger.warning(f"⚠️ 前端 dist 目录不存在: {FRONTEND_DIST}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
