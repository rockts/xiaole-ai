"""
主动问答模块 - v0.3.0 Learning层
识别用户未完整回答的问题，主动追问，提升对话体验
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db_setup import ProactiveQuestion, Message
from datetime import datetime
import os
import re
import json
from dotenv import load_dotenv

load_dotenv()

# 数据库连接
if os.getenv('DATABASE_URL'):
    DB_URL = os.getenv('DATABASE_URL')
else:
    DB_URL = (
        f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASS')}"
        f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}"
        f"/{os.getenv('DB_NAME')}"
    )

engine = create_engine(
    DB_URL,
    connect_args={'check_same_thread': False} if DB_URL.startswith('sqlite')
    else {'client_encoding': 'utf8'}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class ProactiveQA:
    """主动问答分析器"""

    # 问题关键词模式
    QUESTION_PATTERNS = [
        r'(什么|啥|哪|谁|多少|怎么|为什么|如何)',  # 疑问词
        r'(吗|呢|啊)\s*\??$',  # 句尾语气词
        r'\?',  # 问号
    ]

    # 不完整回答标记
    INCOMPLETE_MARKERS = [
        '不知道', '不清楚', '不太确定', '不记得', '忘了',
        '说不上来', '不好说', '看情况', '再说', '以后',
        '可能', '大概', '应该', '或许', '也许',
    ]

    def __init__(self):
        """初始化（不创建持久session）"""
        pass

    def is_question(self, text: str) -> bool:
        """判断文本是否为问句"""
        if not text:
            return False

        # 检查问题模式
        for pattern in self.QUESTION_PATTERNS:
            if re.search(pattern, text):
                return True
        return False

    def is_incomplete_answer(self, text: str) -> bool:
        """判断回答是否不完整"""
        if not text:
            return True

        # 检查不完整标记
        for marker in self.INCOMPLETE_MARKERS:
            if marker in text:
                return True

        # 回答过短（少于5个字）
        if len(text.strip()) < 5:
            return True

        return False

    def analyze_conversation(
        self, session_id: str, user_id: str = "default_user"
    ) -> dict:
        """
        分析对话，识别需要追问的问题

        返回格式：
        {
            "needs_followup": bool,
            "questions": [
                {
                    "question": str,
                    "type": str,
                    "missing_info": list,
                    "confidence": int
                }
            ]
        }
        """
        session = SessionLocal()
        try:
            # 获取该会话的最近20条消息
            messages = (
                session.query(Message)
                .filter_by(session_id=session_id)
                .order_by(Message.created_at.desc())
                .limit(20)
                .all()
            )

            if not messages:
                return {"needs_followup": False, "questions": []}

            # 反转消息顺序（从旧到新）
            messages = list(reversed(messages))

            needs_followup_list = []

            # 分析消息对
            for i in range(len(messages) - 1):
                current_msg = messages[i]
                next_msg = messages[i + 1]

                # 查找：用户提问 -> AI回答的模式
                if (current_msg.role == "user" and
                        next_msg.role == "assistant"):

                    user_text = current_msg.content
                    ai_response = next_msg.content

                    # 判断用户是否提问
                    if self.is_question(user_text):
                        # 判断AI回答是否不完整
                        if self.is_incomplete_answer(ai_response):
                            # 分析缺失信息
                            missing_info = self._analyze_missing_info(
                                user_text, ai_response
                            )

                            # 计算置信度
                            confidence = self._calculate_confidence(
                                user_text, ai_response, missing_info
                            )

                            needs_followup_list.append({
                                "question": user_text,
                                "type": "incomplete",
                                "missing_info": missing_info,
                                "confidence": confidence,
                                "ai_response": ai_response
                            })

            # 检查是否有需要追问的问题
            needs_followup = len(needs_followup_list) > 0

            return {
                "needs_followup": needs_followup,
                "questions": needs_followup_list
            }

        finally:
            session.close()

    def _analyze_missing_info(
        self, question: str, answer: str
    ) -> list:
        """分析缺失的信息点"""
        missing = []

        # 提取问题中的关键信息点
        if '什么' in question or '啥' in question:
            if not any(word in answer for word in ['是', '叫', '指']):
                missing.append("具体名称")

        if '怎么' in question or '如何' in question:
            if not any(word in answer for word in ['步骤', '方法', '可以']):
                missing.append("操作方法")

        if '为什么' in question:
            if not any(word in answer for word in ['因为', '由于', '原因']):
                missing.append("原因说明")

        if '多少' in question or '几' in question:
            if not any(char.isdigit() for char in answer):
                missing.append("具体数值")

        if '哪' in question or '谁' in question:
            missing.append("具体对象")

        # 如果没有识别到具体缺失点，给出通用描述
        if not missing:
            missing.append("完整回答")

        return missing

    def _calculate_confidence(
        self, question: str, answer: str, missing_info: list
    ) -> int:
        """计算判断置信度（0-100）"""
        confidence = 50  # 基础分

        # 根据不完整标记增加置信度
        for marker in self.INCOMPLETE_MARKERS:
            if marker in answer:
                confidence += 15
                break

        # 回答过短大幅增加置信度
        if len(answer.strip()) < 5:
            confidence += 30
        elif len(answer.strip()) < 10:
            confidence += 20

        # 缺失信息越多，置信度越高
        confidence += len(missing_info) * 5

        # 限制在0-100范围
        return min(max(confidence, 0), 100)

    def generate_followup_question(
        self, original_question: str, missing_info: list, ai_response: str
    ) -> str:
        """生成追问内容"""

        # 根据缺失信息类型生成追问
        if "具体名称" in missing_info:
            return f"关于'{original_question}'，您能说得更具体一些吗？"

        if "操作方法" in missing_info:
            return f"您提到'{original_question}'，能详细说说具体怎么做吗？"

        if "原因说明" in missing_info:
            return f"关于'{original_question}'，能再说说具体原因吗？"

        if "具体数值" in missing_info:
            return f"您说的'{original_question}'，大概是多少呢？"

        if "具体对象" in missing_info:
            return f"您提到'{original_question}'，具体是指哪个呢？"

        # 通用追问
        return f"您刚才提到'{original_question}'，能再详细说说吗？"

    def save_proactive_question(
        self,
        session_id: str,
        user_id: str,
        original_question: str,
        question_type: str,
        missing_info: list,
        confidence: int,
        followup_question: str
    ) -> int:
        """保存主动问答记录，返回记录ID"""
        session = SessionLocal()
        try:
            record = ProactiveQuestion(
                user_id=user_id,
                session_id=session_id,
                original_question=original_question,
                question_type=question_type,
                is_answered=False,
                need_followup=True,
                followup_question=followup_question,
                followup_asked=False,
                missing_info=json.dumps(missing_info, ensure_ascii=False),
                confidence_score=confidence
            )
            session.add(record)
            session.commit()
            return record.id
        finally:
            session.close()

    def get_pending_followups(
        self, session_id: str, limit: int = 5
    ) -> list:
        """获取待追问的问题列表"""
        session = SessionLocal()
        try:
            records = (
                session.query(ProactiveQuestion)
                .filter_by(session_id=session_id, followup_asked=False)
                .order_by(ProactiveQuestion.confidence_score.desc())
                .limit(limit)
                .all()
            )

            result = []
            for record in records:
                result.append({
                    "id": record.id,
                    "question": record.original_question,
                    "followup": record.followup_question,
                    "confidence": record.confidence_score,
                    "created_at": record.created_at.isoformat()
                })
            return result
        finally:
            session.close()

    def mark_followup_asked(self, question_id: int):
        """标记追问已发送"""
        session = SessionLocal()
        try:
            record = session.query(ProactiveQuestion).get(question_id)
            if record:
                record.followup_asked = True
                record.asked_at = datetime.now()
                session.commit()
        finally:
            session.close()

    def get_followup_history(
        self, session_id: str = None, user_id: str = None, limit: int = 20
    ) -> list:
        """获取追问历史记录"""
        session = SessionLocal()
        try:
            query = session.query(ProactiveQuestion)

            if session_id:
                query = query.filter_by(session_id=session_id)
            if user_id:
                query = query.filter_by(user_id=user_id)

            records = (
                query.order_by(ProactiveQuestion.created_at.desc())
                .limit(limit)
                .all()
            )

            result = []
            for record in records:
                result.append({
                    "id": record.id,
                    "original_question": record.original_question,
                    "followup_question": record.followup_question,
                    "type": record.question_type,
                    "confidence": record.confidence_score,
                    "followup_asked": record.followup_asked,
                    "created_at": record.created_at.isoformat(),
                    "asked_at": (
                        record.asked_at.isoformat()
                        if record.asked_at else None
                    )
                })
            return result
        finally:
            session.close()
