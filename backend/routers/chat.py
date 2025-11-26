from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from typing import Dict, Any, Optional
from dependencies import get_xiaole_agent, get_proactive_qa
from agent import XiaoLeAgent
from proactive_qa import ProactiveQA
from auth import get_current_user
from logger import logger

router = APIRouter(
    tags=["chat"]
)


def get_agent():
    return get_xiaole_agent()


def get_qa():
    return get_proactive_qa()


@router.post("/chat")
def chat(
    prompt: str,
    session_id: Optional[str] = None,
    user_id: str = "default_user",
    response_style: str = "balanced",
    image_path: Optional[str] = None,
    memorize: bool = False,
    current_user: str = Depends(get_current_user),
    agent: XiaoLeAgent = Depends(get_agent),
    qa: ProactiveQA = Depends(get_qa)
):
    """支持上下文的对话接口"""
    # 使用认证用户ID覆盖请求中的user_id
    user_id = current_user

    # 如果有图片，先进行图片识别
    if image_path:
        from tools.vision_tool import VisionTool
        vision_tool = VisionTool()

        try:
            # 智能选择识别prompt
            important_kw = ['课程表', '课表', '时间表', '上课']
            if prompt and any(kw in prompt for kw in important_kw):
                ocr_prompt = '''这是一张学生课程表。请仔细识别表格中的内容：
1. 表头有：星期一、星期二、星期三、星期四、星期五
2. 左侧行标题有：晨读、第1节、第2节...第7节、午休、课后辅导
3. 每个格子可能有课程名称（如"科学"）和编号（如"(5)"）

请完整地列出每一天的所有课程，包括空格子（标注"无课"）。
格式：
周一：晨读-XX, 第1节-XX, 第2节-XX...
周二：...
依此类推。不要省略任何信息。'''
            else:
                ocr_prompt = (
                    '请详细描述这张图片的内容，包括：\n'
                    '1. 主体物品或场景是什么\n'
                    '2. 图片中的文字信息（如有），如看到片段“ckin/ickin”等，可推测完整品牌名\n'
                    '3. 颜色、品牌、标识等细节\n'
                    '4. 其他值得注意的特征\n\n'
                    '如能识别品牌请直接说明。'
                )

            vision_result = vision_tool.analyze_image(
                image_path=image_path,
                prompt=ocr_prompt,
                prefer_model="auto"
            )

            if vision_result.get('success'):
                vision_description = vision_result.get('description', '')

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

                should_memorize = memorize
                if prompt:
                    memorize_keywords = ['记住', '保存', '记下', '存一下', '记录']
                    relation_keywords = ['我的', '我儿子', '我女儿', '我妻子', '我老婆',
                                         '我老公', '我爸', '我妈', '家人', '孩子', '宝宝']

                    should_memorize = should_memorize or any(
                        kw in prompt for kw in memorize_keywords)
                    should_memorize = should_memorize or any(
                        kw in prompt for kw in relation_keywords)

                if not should_memorize:
                    important_content_indicators = [
                        '课程表', '时间表', '日程', '表格', '证件']
                    should_memorize = any(
                        ind in vision_description
                        for ind in important_content_indicators
                    )

                if should_memorize:
                    try:
                        agent.memory.remember(
                            content=vision_description,
                            tag=f"image:{image_path.split('/')[-1]}"
                        )
                        combined_prompt += "\n\n[系统提示：这张图片的内容我已经记住了，以后可以回忆]"
                    except Exception as e:
                        logger.error(f"⚠️ 保存图片记忆失败: {e}")

                return agent.chat(
                    combined_prompt, session_id, user_id, response_style,
                    image_path=image_path,
                    original_user_prompt=prompt
                )
            else:
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

    result = agent.chat(prompt, session_id, user_id, response_style)

    try:
        actual_session_id = result.get('session_id') if isinstance(
            result, dict) else session_id

        if actual_session_id:
            try:
                qa.analyze_conversation(actual_session_id, user_id)
            except Exception as e:
                logger.error(f"⚠️ 追问分析异常: {e}")
    except Exception as e:
        logger.error(f"⚠️ 追问模块异常: {e}")

    return result


@router.post("/chat/stream")
def chat_stream(
    prompt: str,
    session_id: Optional[str] = None,
    user_id: str = "default_user",
    response_style: str = "balanced",
    image_path: Optional[str] = None,
    memorize: bool = False,
    current_user: str = Depends(get_current_user),
    agent: XiaoLeAgent = Depends(get_agent),
    qa: ProactiveQA = Depends(get_qa)
):
    """流式对话接口（SSE 兼容）。

    说明：
    - 为尽快上线体验，当前实现为“切片流”：先生成完整回复，再按块推送；
      命中直达规则（时间/日期/计算/小名等）时能即时返回；
    - 后续可改为直连模型原生流式（DeepSeek/Claude）。
    """
    user_id = current_user

    def event_stream():
        import json
        # 起始事件，便于前端建立状态
        start_payload = {"type": "start"}
        yield f"data: {json.dumps(start_payload, ensure_ascii=False)}\n\n"

        # 处理图片（沿用同步路径，保持稳定）
        if image_path:
            from tools.vision_tool import VisionTool
            vision_tool = VisionTool()
            try:
                important_kw = ['课程表', '课表', '时间表', '上课']
                if prompt and any(kw in prompt for kw in important_kw):
                    ocr_prompt = '这是一张课程表，请识别并按天/节次列出。'
                else:
                    ocr_prompt = '请详细描述这张图片的内容（主体/文字/颜色/品牌等）。'

                vision_result = vision_tool.analyze_image(
                    image_path=image_path,
                    prompt=ocr_prompt,
                    prefer_model="auto"
                )

                if vision_result.get('success'):
                    desc = vision_result.get('description', '')
                    if prompt:
                        combined_prompt = (
                            f"<vision_result>\n{desc}\n</vision_result>\n\n"
                            f"用户问题：{prompt}\n\n请基于识别结果作答。"
                        )
                    else:
                        combined_prompt = (
                            f"<vision_result>\n{desc}\n</vision_result>\n\n"
                            f"请分析并解释图片内容。"
                        )

                    try:
                        if memorize:
                            agent.memory.remember(
                                content=desc,
                                tag=f"image:{image_path.split('/')[-1]}"
                            )
                    except Exception:
                        pass

                    result = agent.chat(
                        combined_prompt, session_id, user_id,
                        response_style, image_path=image_path,
                        original_user_prompt=prompt
                    )
                else:
                    err = vision_result.get('error', '未知错误')
                    result = {
                        'reply': f"❌ 图片识别失败: {err}",
                        'session_id': session_id or 'error'
                    }
            except Exception as e:
                result = {
                    'reply': f'❌ 图片处理出错: {str(e)}',
                    'session_id': session_id or 'error'
                }
        else:
            # 常规对话
            result = agent.chat(prompt, session_id, user_id, response_style)

        # 追问分析（异步重要性不高，这里保持与同步一致）
        try:
            actual_session_id = (
                result.get('session_id')
                if isinstance(result, dict) else session_id
            )
            if actual_session_id:
                try:
                    qa.analyze_conversation(actual_session_id, user_id)
                except Exception:
                    pass
        except Exception:
            pass

        reply = (
            result.get('reply') if isinstance(result, dict)
            else str(result)
        )
        # 切片流式输出
        chunk_size = 120
        idx = 0
        while idx < len(reply):
            part = reply[idx: idx + chunk_size]
            idx += chunk_size
            payload = {"type": "delta", "data": part}
            yield f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"

        # 完成事件，带上元信息
        end_payload = {
            "type": "end",
            "session_id": (
                result.get('session_id')
                if isinstance(result, dict) else session_id
            ),
            "user_message_id": (
                result.get('user_message_id')
                if isinstance(result, dict) else None
            ),
            "assistant_message_id": (
                result.get('assistant_message_id')
                if isinstance(result, dict) else None
            ),
        }
        yield f"data: {json.dumps(end_payload, ensure_ascii=False)}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@router.get("/sessions")
def get_sessions(
    user_id: str = "default_user",
    limit: Optional[int] = None,
    all_sessions: bool = False,
    agent: XiaoLeAgent = Depends(get_agent)
):
    """获取用户的对话会话列表"""
    effective_limit = None if all_sessions else limit
    sessions = agent.conversation.get_recent_sessions(
        user_id, effective_limit
    )
    return {"sessions": sessions}


@router.get("/session/{session_id}")
def get_session(
    session_id: str,
    limit: int = 200,
    agent: XiaoLeAgent = Depends(get_agent)
):
    """获取会话详情"""
    stats = agent.conversation.get_session_stats(session_id)
    history = agent.conversation.get_history(session_id, limit=limit)

    if not stats:
        raise HTTPException(status_code=404, detail="Session not found")

    return {
        "session_id": stats["session_id"],
        "title": stats["title"],
        "message_count": stats["message_count"],
        "created_at": stats["created_at"],
        "updated_at": stats["updated_at"],
        "messages": history
    }


@router.patch("/api/chat/sessions/{session_id}")
def update_session(
    session_id: str,
    update_data: Dict[str, Any],
    agent: XiaoLeAgent = Depends(get_agent)
):
    """更新会话信息"""
    try:
        if "title" in update_data:
            agent.conversation.update_session_title(
                session_id, update_data["title"])

        if "pinned" in update_data:
            agent.conversation.update_session_pinned(
                session_id, update_data["pinned"])

        return {"message": "Session updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/session/{session_id}")
def delete_session(
    session_id: str,
    agent: XiaoLeAgent = Depends(get_agent)
):
    """删除会话"""
    agent.conversation.delete_session(session_id)
    return {"message": "Session deleted"}


@router.delete("/api/chat/sessions/{session_id}")
def delete_session_api(
    session_id: str,
    agent: XiaoLeAgent = Depends(get_agent)
):
    """删除会话 (新API路径)"""
    agent.conversation.delete_session(session_id)
    return {"message": "Session deleted"}


@router.delete("/api/messages/{message_id}")
def delete_message_api(
    message_id: int,
    agent: XiaoLeAgent = Depends(get_agent)
):
    """删除消息及其后续消息"""
    success = agent.conversation.delete_message_and_following(message_id)
    if success:
        return {"success": True, "message": "Messages deleted"}
    else:
        raise HTTPException(
            status_code=404,
            detail="Message not found or delete failed"
        )
