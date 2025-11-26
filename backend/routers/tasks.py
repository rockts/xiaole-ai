from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, Optional
from dependencies import get_xiaole_agent
from agent import XiaoLeAgent
from logger import logger

router = APIRouter(
    prefix="/api/tasks",
    tags=["tasks"]
)


def get_agent():
    return get_xiaole_agent()


@router.post("", response_model=Dict[str, Any])
def create_task(
    request: Dict[str, Any],
    agent: XiaoLeAgent = Depends(get_agent)
):
    """创建任务"""
    try:
        user_id = request.get('user_id', 'default_user')
        session_id = request.get('session_id')
        title = request.get('title')
        description = request.get('description', '')
        priority = request.get('priority', 0)

        if not title:
            raise HTTPException(status_code=400, detail="缺少任务标题")

        task_id = agent.task_manager.create_task(
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
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"创建任务失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("", response_model=Dict[str, Any])
def get_tasks_list(
    user_id: str = "default_user",
    status: Optional[str] = None,
    limit: int = 50,
    agent: XiaoLeAgent = Depends(get_agent)
):
    """获取当前用户的任务列表"""
    try:
        tasks = agent.task_manager.get_tasks_by_user(
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


@router.get("/{task_id}", response_model=Dict[str, Any])
def get_task(
    task_id: int,
    agent: XiaoLeAgent = Depends(get_agent)
):
    """获取任务详情"""
    try:
        task = agent.task_manager.get_task(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="任务不存在")

        # 获取步骤
        steps = agent.task_manager.get_task_steps(task_id)

        return {
            "success": True,
            "task": dict(task),
            "steps": steps
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取任务详情失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{task_id}/status", response_model=Dict[str, Any])
def update_task_status(
    task_id: int,
    request: Dict[str, Any],
    agent: XiaoLeAgent = Depends(get_agent)
):
    """更新任务状态"""
    try:
        status = request.get('status')
        if not status:
            return {"success": False, "error": "缺少状态参数"}

        success = agent.task_manager.update_task_status(
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


@router.post("/{task_id}/execute", response_model=Dict[str, Any])
def execute_task(
    task_id: int,
    request: Dict[str, Any],
    agent: XiaoLeAgent = Depends(get_agent)
):
    """执行任务"""
    try:
        user_id = request.get('user_id', 'default_user')
        session_id = request.get('session_id', '')

        result = agent.task_executor.execute_task(
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


@router.post("/{task_id}/cancel", response_model=Dict[str, Any])
def cancel_task(
    task_id: int,
    agent: XiaoLeAgent = Depends(get_agent)
):
    """取消任务"""
    try:
        result = agent.task_executor.cancel_task(task_id)
        return result
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@router.delete("/{task_id}", response_model=Dict[str, Any])
def delete_task(
    task_id: int,
    agent: XiaoLeAgent = Depends(get_agent)
):
    """删除任务"""
    try:
        success = agent.task_manager.delete_task(task_id)
        return {
            "success": success
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@router.get("/stats/{user_id}", response_model=Dict[str, Any])
def get_task_stats(
    user_id: str,
    agent: XiaoLeAgent = Depends(get_agent)
):
    """获取用户任务统计"""
    try:
        stats = agent.task_manager.get_task_statistics(user_id)
        return {
            "success": True,
            "stats": stats
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
