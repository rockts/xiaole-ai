from fastapi import APIRouter, Depends
from typing import Dict, Any, Optional
from dependencies import get_xiaole_agent
from agent import XiaoLeAgent

router = APIRouter(
    tags=["analytics"]
)


def get_agent():
    return get_xiaole_agent()


@router.get("/analytics/behavior")
def get_behavior_analytics(
    user_id: str = "default_user",
    days: int = 30,
    agent: XiaoLeAgent = Depends(get_agent)
):
    """获取用户行为分析报告"""
    report = agent.behavior_analyzer.generate_behavior_report(user_id, days)
    if not report or not report.get("conversation_stats"):
        return {"error": "No data available"}, 404
    return report


@router.get("/analytics/activity")
def get_activity_pattern(
    user_id: str = "default_user",
    days: int = 30,
    agent: XiaoLeAgent = Depends(get_agent)
):
    """获取用户活跃时间模式"""
    pattern = agent.behavior_analyzer.get_user_activity_pattern(user_id, days)
    if not pattern:
        return {"error": "No data available"}, 404
    return pattern


@router.get("/analytics/topics")
def get_topic_preferences(
    user_id: str = "default_user",
    days: int = 30,
    agent: XiaoLeAgent = Depends(get_agent)
):
    """获取用户话题偏好"""
    topics = agent.behavior_analyzer.get_topic_preferences(user_id, days)
    if not topics:
        return {"error": "No data available"}, 404
    return topics


@router.get("/patterns/frequent")
def get_frequent_words(
    user_id: str = "default_user",
    limit: int = 20,
    agent: XiaoLeAgent = Depends(get_agent)
):
    """获取用户高频词列表"""
    words = agent.pattern_learner.get_frequent_words(user_id, limit)
    return {"user_id": user_id, "frequent_words": words}


@router.get("/patterns/common_questions")
def get_common_questions(
    user_id: str = "default_user",
    limit: int = 10,
    agent: XiaoLeAgent = Depends(get_agent)
):
    """获取用户常见问题分类"""
    questions = agent.pattern_learner.get_common_questions(user_id, limit)
    return {"user_id": user_id, "common_questions": questions}


@router.get("/patterns/insights")
def get_learning_insights(
    user_id: str = "default_user",
    agent: XiaoLeAgent = Depends(get_agent)
):
    """获取模式学习统计洞察"""
    insights = agent.pattern_learner.get_learning_insights(user_id)
    return insights
