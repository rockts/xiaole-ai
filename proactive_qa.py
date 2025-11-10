"""
主动问答模块 - v0.6.0 优化版
识别用户未完整回答的问题，主动追问，提升对话体验

v0.6.0更新:
- 优化置信度计算算法
- 改进追问生成的自然度
- 添加可配置的阈值
- 减少误判率
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

    # v0.6.0: 可配置的置信度阈值
    CONFIDENCE_THRESHOLD = int(os.getenv('PROACTIVE_QA_THRESHOLD', '65'))
    
    # 问题关键词模式
    QUESTION_PATTERNS = [
        r'(什么|啥|什么时候|哪里|哪个|哪种|哪|谁|多少|几个|怎么|为什么|如何|怎样)',  # 疑问词
        r'(吗|呢|啊)\s*\??$',  # 句尾语气词
        r'\?',  # 问号
    ]

    # 不完整回答标记
    INCOMPLETE_MARKERS = [
        '不知道', '不清楚', '不太确定', '不记得', '忘了',
        '说不上来', '不好说', '看情况', '再说', '以后',
        '可能', '大概', '应该', '或许', '也许',
    ]

    def __init__(self, confidence_threshold=None):
        """
        初始化
        
        Args:
            confidence_threshold: 自定义置信度阈值（默认使用环境变量）
        """
        self.confidence_threshold = (
            confidence_threshold or self.CONFIDENCE_THRESHOLD
        )

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
        """
        判断回答是否不完整
        
        v0.6.0优化:
        - 排除明显完整的回答
        - 减少误判率
        """
        if not text:
            return True

        # 排除明显完整的回答（包含详细解释词汇）
        complete_indicators = [
            '具体来说', '详细地说', '总而言之', '综上所述',
            '因此', '所以说', '总之', '例如', '比如说',
            '第一', '第二', '首先', '其次', '最后',
            '步骤', '方法如下', '可以这样', '建议'
        ]
        
        # 如果包含完整性指示词且长度>20，认为是完整回答
        if len(text) > 20:
            if any(indicator in text for indicator in complete_indicators):
                return False

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
        """
        计算判断置信度（0-100）
        
        v0.6.0优化:
        - 调整基础分为40（降低误判）
        - 优化不完整标记权重
        - 考虑回答长度更细致
        - 添加问题复杂度因素
        """
        confidence = 40  # 基础分（从50降低到40，减少误触发）

        # 1. 根据不完整标记增加置信度
        incomplete_count = sum(
            1 for marker in self.INCOMPLETE_MARKERS if marker in answer
        )
        if incomplete_count >= 2:
            confidence += 25  # 多个标记词，强烈暗示不完整
        elif incomplete_count == 1:
            confidence += 15  # 单个标记词

        # 2. 回答长度分析（更细致的评分）
        answer_length = len(answer.strip())
        if answer_length < 5:
            confidence += 35  # 极短回答
        elif answer_length < 10:
            confidence += 25  # 很短回答
        elif answer_length < 20:
            confidence += 15  # 较短回答
        elif answer_length < 30:
            confidence += 5   # 中等长度，可能不完整

        # 3. 缺失信息评分
        confidence += len(missing_info) * 5

        # 4. 问题复杂度（复杂问题更需要详细回答）
        question_length = len(question)
        if question_length > 30 and answer_length < question_length * 0.5:
            confidence += 10  # 问题长但回答短

        # 5. 特殊情况调整
        # 如果回答中有举例、解释等词，降低置信度
        if any(word in answer for word in ['例如', '比如', '就是', '也就是说', '具体来说']):
            confidence -= 10
        
        # 如果回答中有明确的结论性词汇，降低置信度
        if any(word in answer for word in ['总之', '综上', '因此', '所以说']):
            confidence -= 15

        # 限制在0-100范围
        return min(max(confidence, 0), 100)

    def generate_followup_question(
        self, original_question: str, missing_info: list, ai_response: str
    ) -> str:
        """
        生成追问内容
        
        v0.6.0优化:
        - 更自然的表达方式
        - 根据回答内容调整追问策略
        - 添加多样化的追问模板
        """
        import random
        
        # 截取问题（太长则省略）
        question_preview = original_question
        if len(original_question) > 40:
            question_preview = original_question[:40] + "..."

        # 根据缺失信息类型生成追问
        if "具体名称" in missing_info:
            templates = [
                f"关于「{question_preview}」，您能说得更具体一些吗？",
                f"「{question_preview}」这个问题，能详细解释一下吗？",
                f"刚才提到的「{question_preview}」，具体是指什么呢？"
            ]
            return random.choice(templates)

        if "操作方法" in missing_info:
            templates = [
                f"关于「{question_preview}」，能详细说说具体步骤吗？",
                f"「{question_preview}」这个操作，具体该怎么做呢？",
                f"您能展开讲讲「{question_preview}」的具体方法吗？"
            ]
            return random.choice(templates)

        if "原因说明" in missing_info:
            templates = [
                f"关于「{question_preview}」，能再说说具体原因吗？",
                f"为什么会这样呢？能详细解释下「{question_preview}」吗？",
                f"「{question_preview}」背后的原因是什么呢？"
            ]
            return random.choice(templates)

        if "具体数值" in missing_info:
            templates = [
                f"「{question_preview}」，大概是多少呢？",
                f"关于「{question_preview}」，能给个具体的数字吗？",
                f"能具体说说「{question_preview}」的数量吗？"
            ]
            return random.choice(templates)

        if "具体对象" in missing_info:
            templates = [
                f"「{question_preview}」，具体是指哪个呢？",
                f"关于「{question_preview}」，您说的是哪一个？",
                f"能明确一下「{question_preview}」说的是谁/什么吗？"
            ]
            return random.choice(templates)

        # 通用追问（根据回答长度选择）
        if len(ai_response) < 10:
            templates = [
                f"「{question_preview}」这个问题，能展开说说吗？",
                f"关于「{question_preview}」，能再详细一点吗？",
                f"「{question_preview}」能具体解释一下吗？"
            ]
        else:
            templates = [
                f"「{question_preview}」这个话题，还能再多说一点吗？",
                f"关于「{question_preview}」，我想了解更多细节",
                f"「{question_preview}」能补充说明一下吗？"
            ]
        
        return random.choice(templates)

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
        """保存主动问答记录，返回记录ID（自动去重）"""
        session = SessionLocal()
        try:
            # 检查是否已存在相同的未回答问题（基于user_id去重，避免跨会话重复）
            # 只检查最近10分钟内的记录，避免误删旧记录
            from datetime import datetime, timedelta
            ten_minutes_ago = datetime.now() - timedelta(minutes=10)

            existing = (
                session.query(ProactiveQuestion)
                .filter_by(
                    user_id=user_id,
                    original_question=original_question,
                    followup_asked=False
                )
                .filter(ProactiveQuestion.created_at >= ten_minutes_ago)
                .first()
            )

            if existing:
                # 如果已存在，更新置信度（取较高值）并返回现有记录ID
                if confidence > existing.confidence_score:
                    existing.confidence_score = confidence
                    session.commit()
                return existing.id

            # 不存在则创建新记录
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
        """获取待追问的问题列表（按user_id去重，避免跨会话重复）"""
        session = SessionLocal()
        try:
            # 先获取该会话的user_id
            from db_setup import Message
            msg = session.query(Message).filter_by(
                session_id=session_id).first()
            user_id = msg.user_id if msg else "default_user"

            # 查询该用户的待追问问题（不限定session_id，避免跨会话重复显示）
            # 使用子查询去重：每个original_question只保留最新的一条
            from sqlalchemy import func
            subquery = (
                session.query(
                    ProactiveQuestion.original_question,
                    func.max(ProactiveQuestion.id).label('max_id')
                )
                .filter_by(user_id=user_id, followup_asked=False)
                .group_by(ProactiveQuestion.original_question)
                .subquery()
            )

            records = (
                session.query(ProactiveQuestion)
                .join(
                    subquery,
                    ProactiveQuestion.id == subquery.c.max_id
                )
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
        """获取追问历史记录（去重显示，每个问题只显示最新一条）"""
        session = SessionLocal()
        try:
            # 如果没有指定user_id，尝试从session_id获取
            if not user_id and session_id:
                from db_setup import Message
                msg = session.query(Message).filter_by(
                    session_id=session_id
                ).first()
                if msg:
                    user_id = msg.user_id

            # 使用user_id查询，避免session_id限制导致的重复
            if user_id:
                # 子查询：每个问题保留最新的一条记录
                from sqlalchemy import func
                subquery = (
                    session.query(
                        ProactiveQuestion.original_question,
                        func.max(ProactiveQuestion.id).label('max_id')
                    )
                    .filter_by(user_id=user_id)
                    .group_by(ProactiveQuestion.original_question)
                    .subquery()
                )

                records = (
                    session.query(ProactiveQuestion)
                    .join(
                        subquery,
                        ProactiveQuestion.id == subquery.c.max_id
                    )
                    .order_by(ProactiveQuestion.created_at.desc())
                    .limit(limit)
                    .all()
                )
            else:
                # 没有user_id，使用原逻辑（不去重）
                query = session.query(ProactiveQuestion)
                if session_id:
                    query = query.filter_by(session_id=session_id)
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
