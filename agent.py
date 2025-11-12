from memory import MemoryManager
from conversation import ConversationManager
from behavior_analytics import BehaviorAnalyzer
from proactive_qa import ProactiveQA  # v0.3.0 主动问答
from pattern_learning import PatternLearner  # v0.3.0 模式学习
from tool_manager import get_tool_registry  # v0.4.0 工具管理
from enhanced_intent import EnhancedToolSelector, ContextEnhancer
from dialogue_enhancer import DialogueEnhancer  # v0.6.0
from task_manager import TaskManager  # v0.8.0 任务管理
from error_handler import (
    retry_with_backoff, log_execution, handle_api_errors,
    logger
)
import os
from dotenv import load_dotenv
import requests
from datetime import datetime
import re
import asyncio  # v0.4.0 用于同步执行异步工具调用

load_dotenv()


class XiaoLeAgent:
    def __init__(self):
        self.memory = MemoryManager()
        self.conversation = ConversationManager()
        self.behavior_analyzer = BehaviorAnalyzer()  # v0.3.0 行为分析器
        self.proactive_qa = ProactiveQA()  # v0.3.0 主动问答分析器
        self.pattern_learner = PatternLearner()  # v0.3.0 模式学习器
        self.tool_registry = get_tool_registry()  # v0.4.0 工具注册中心

        # v0.6.0 Phase 3: AI能力增强
        self.enhanced_selector = EnhancedToolSelector(self.tool_registry)
        self.context_enhancer = ContextEnhancer(self.memory, self.conversation)
        self.dialogue_enhancer = DialogueEnhancer()  # Day 4: 对话质量

        # v0.8.0 任务管理器
        db_config = {
            'host': os.getenv('DB_HOST'),
            'port': int(os.getenv('DB_PORT', 5432)),
            'database': os.getenv('DB_NAME'),
            'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_PASS')
        }
        self.task_manager = TaskManager(db_config)

        # v0.8.0 任务执行器(延迟导入避免循环依赖)
        from task_executor import TaskExecutor
        self.task_executor = TaskExecutor(
            self.task_manager, self.tool_registry
        )

        # 注册工具
        self._register_tools()

        # 支持多个AI平台
        self.api_type = os.getenv("AI_API_TYPE", "deepseek")

        # DeepSeek配置
        self.deepseek_key = os.getenv("DEEPSEEK_API_KEY")
        self.deepseek_url = "https://api.deepseek.com/chat/completions"

        # Claude配置
        self.claude_key = os.getenv("CLAUDE_API_KEY")

        self.model = self._get_model()
        self.client = self._init_client()

    def _register_tools(self):
        """注册所有可用工具"""
        try:
            from tools import (
                weather_tool, system_info_tool,
                time_tool, calculator_tool, reminder_tool,
                search_tool, file_tool, delete_memory_tool
            )

            # 注册工具
            self.tool_registry.register(weather_tool)
            self.tool_registry.register(system_info_tool)
            self.tool_registry.register(time_tool)
            self.tool_registry.register(calculator_tool)
            self.tool_registry.register(reminder_tool)  # v0.5.0 提醒工具
            self.tool_registry.register(search_tool)  # v0.5.0 搜索工具
            self.tool_registry.register(file_tool)  # v0.5.0 文件工具
            self.tool_registry.register(delete_memory_tool)  # v0.8.1 删除记忆

            logger.info(
                f"✅ 工具注册完成，共 "
                f"{len(self.tool_registry.get_tool_names())} 个工具"
            )
        except Exception as e:
            logger.error(f"工具注册失败: {e}", exc_info=True)

    def _get_model(self):
        """根据API类型获取模型名称"""
        if self.api_type == "deepseek":
            return os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
        else:  # claude
            return os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-20241022")

    def _init_client(self):
        """初始化客户端"""
        if self.api_type == "deepseek":
            if not self.deepseek_key or \
               self.deepseek_key == "your_deepseek_api_key_here":
                print("⚠️  警告: 未配置 DEEPSEEK_API_KEY，使用占位模式")
                return None
            print(f"✅ 使用 DeepSeek API ({self.model})")
            return "deepseek"

        elif self.api_type == "claude":
            if not self.claude_key or \
               self.claude_key == "your_claude_api_key_here":
                print("⚠️  警告: 未配置 CLAUDE_API_KEY，使用占位模式")
                # 尝试回退到 DeepSeek
                if self.deepseek_key and \
                   self.deepseek_key != "your_deepseek_api_key_here":
                    print("↩️  回退到 DeepSeek（因缺少 Claude Key）")
                    self.api_type = "deepseek"
                    self.model = self._get_model()
                    print(f"✅ 使用 DeepSeek API ({self.model})")
                    return "deepseek"
                return None
            try:
                from anthropic import Anthropic
                print(f"✅ 使用 Claude API ({self.model})")
                return Anthropic(api_key=self.claude_key)
            except Exception as e:
                print(f"⚠️  Claude初始化失败: {e}")
                # 尝试回退到 DeepSeek
                if self.deepseek_key and \
                   self.deepseek_key != "your_deepseek_api_key_here":
                    print("↩️  回退到 DeepSeek（Claude 初始化失败）")
                    self.api_type = "deepseek"
                    self.model = self._get_model()
                    print(f"✅ 使用 DeepSeek API ({self.model})")
                    return "deepseek"
                return None

        print(f"⚠️  未知的API类型: {self.api_type}")
        # 尝试回退到 DeepSeek
        if self.deepseek_key and \
           self.deepseek_key != "your_deepseek_api_key_here":
            print("↩️  回退到 DeepSeek（未知 API 类型）")
            self.api_type = "deepseek"
            self.model = self._get_model()
            print(f"✅ 使用 DeepSeek API ({self.model})")
            return "deepseek"
        return None

    def think(self, prompt, use_memory=True):
        """调用 AI API 进行思考"""
        # 如果没有配置 API，返回占位响应
        if not self.client:
            return f"（占位模式）你说的是：{prompt}"

        try:
            # 获取当前时间和星期
            now = datetime.now()
            current_datetime = now.strftime("%Y年%m月%d日 %H:%M")
            weekday_names = ['周一', '周二', '周三', '周四',
                             '周五', '周六', '周日']
            current_weekday = weekday_names[now.weekday()]

            # 构建系统提示
            system_prompt = (
                "你是小乐AI管家，一个诚实、友好的个人助手。\n\n"
                "核心原则：\n"
                "1. 你是对话助手，没有连接智能设备（无手环/摄像头/传感器）\n"
                "2. 只使用用户明确告诉你的信息和下方的记忆库内容\n"
                "3. 记忆库按时间倒序排列，最新信息在前，优先使用最新信息\n"
                "4. 如果记忆库没有相关信息，诚实说'您还没告诉我'\n"
                "5. 当用户告诉你新信息时，友好确认并记录\n"
                "6. 绝不编造数据、假装有设备、或推测未知信息\n"
                f"当前时间：{current_datetime}（{current_weekday}）\n"
            )

            # 添加历史记忆（智能检索）
            if use_memory:
                # 1. 获取最近5条记忆（时间相关）- 最新信息优先
                recent_memories = self.memory.recall(
                    tag="general", limit=5)

                # 2. 搜索关键信息（名字、生日等重要记忆）
                keywords = ['叫', '名字', '生日', '爱好', '喜欢']
                important_memories = []
                for kw in keywords:
                    mems = self.memory.recall(
                        tag="general", keyword=kw, limit=2)
                    important_memories.extend(mems)

                # 3. 合并去重：最近记忆在前（优先级高）
                all_memories = list(dict.fromkeys(
                    recent_memories + important_memories))[:8]

                if all_memories:
                    context = "记忆库（按时间倒序，最新在前）：\n" + \
                              "\n".join(all_memories)
                    system_prompt += f"\n\n{context}"

            # 根据API类型调用
            if self.api_type == "deepseek":
                reply = self._call_deepseek(system_prompt, prompt)
            elif self.api_type == "claude":
                reply = self._call_claude(system_prompt, prompt)
            else:
                reply = "未知的API类型"

            # 处理回复中的日期占位符（以防AI还是使用了）
            reply = self._process_date_placeholders(reply)

            # 注意：对话记录不应存入memories表，会导致AI把自己的回复当成事实
            # 如果需要记录对话，应使用conversation.add_message()

            return reply

        except Exception as e:
            error_msg = f"调用 AI API 时出错: {str(e)}"
            print(f"❌ {error_msg}")
            return f"抱歉，我遇到了一些问题：{str(e)}"

    @retry_with_backoff(
        max_retries=3,
        initial_delay=1.0,
        exceptions=(requests.Timeout, requests.ConnectionError)
    )
    @handle_api_errors
    @log_execution
    def _call_deepseek(self, system_prompt, user_prompt):
        """调用 DeepSeek API"""
        logger.info(f"调用 DeepSeek API - Prompt长度: {len(user_prompt)}")

        headers = {
            "Authorization": f"Bearer {self.deepseek_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.5,
            "max_tokens": 512,
            "stream": False
        }

        response = requests.post(
            self.deepseek_url,
            headers=headers,
            json=data,
            timeout=60  # 增加超时时间以处理复杂问题
        )

        response.raise_for_status()
        result = response.json()
        reply = result["choices"][0]["message"]["content"]
        logger.info(f"DeepSeek API 响应成功 - 回复长度: {len(reply)}")
        return reply

    @retry_with_backoff(
        max_retries=3,
        initial_delay=1.0,
        exceptions=(Exception,)
    )
    @handle_api_errors
    @log_execution
    def _call_claude(self, system_prompt, user_prompt):
        """调用 Claude API"""
        logger.info(f"调用 Claude API - Prompt长度: {len(user_prompt)}")

        response = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_prompt}
            ]
        )

        reply = response.content[0].text
        logger.info(f"Claude API 响应成功 - 回复长度: {len(reply)}")
        return reply

    def _process_date_placeholders(self, text):
        """处理文本中的日期占位符"""
        current_date = datetime.now().strftime("%Y年%m月%d日")
        current_datetime = datetime.now().strftime("%Y年%m月%d日 %H:%M")

        # 替换各种可能的日期占位符
        replacements = {
            r'\{\{当前日期\}\}': current_date,
            r'\{\{当前时间\}\}': current_datetime,
            r'\{\{今天\}\}': current_date,
            r'\{\{date\}\}': current_date,
            r'\{\{datetime\}\}': current_datetime,
        }

        for pattern, replacement in replacements.items():
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

        return text

    def _extract_and_remember(self, user_message):
        """
        智能提取用户消息中的关键事实并存储
        只有当用户主动告诉我们关键信息时才存储
        """
        if not self.client:
            return  # 占位模式不提取

        # 让AI判断是否包含需要记住的关键事实
        extraction_prompt = f"""分析用户的这句话，判断是否包含需要长期记住的关键信息。

用户说："{user_message}"

如果包含以下类型的关键信息，请提取出来（只提取用户明确告知的事实）：
- 姓名、年龄、生日
- 明确的爱好、兴趣（例如"我喜欢..."）
- 职业、工作
- 家庭成员（**特别注意**：如果是家人的信息，必须明确标注"儿子"、"女儿"、"妻子"等，不要写"用户"）
- 重要日期
- **用户的纠正和反馈**（例如"不算晨读"、"不包括..."）
- **用户的偏好和规则**（例如"我不喜欢..."、"只算..."）
- **对AI回答的补充说明**（例如"实际上..."、"其实..."）

**重要规则：**
1. 只提取用户主动告诉的信息，不要推测
2. 如果只是闲聊（如"今天天气好"、"你好"），返回"无"
3. **特别注意用户的纠正**：如果用户指出AI的错误，这是重要信息
4. **区分主语**：家人的信息必须标注关系（如"儿子姓名：xxx"），不要写成"用户姓名"
5. 提取格式：简洁的陈述句，例如"用户姓名：张三"、"儿子学校：逸夫中学"、"统计课程数量时不算晨读"

请直接返回提取结果，如果没有需要记住的信息就返回"无"。"""

        try:
            if self.api_type == "deepseek":
                result = self._call_deepseek(
                    system_prompt="你是信息提取助手，专门识别和提取用户的关键个人信息。",
                    user_prompt=extraction_prompt
                )
            else:  # claude
                result = self._call_claude(
                    system_prompt="你是信息提取助手，专门识别和提取用户的关键个人信息。",
                    user_prompt=extraction_prompt
                )

            # 如果提取到了有效信息（不是"无"），存储到记忆
            invalid_results = ["无", "无。", "None", "none", ""]
            if result and result.strip() not in invalid_results:
                self.memory.remember(result.strip(), tag="facts")
                logger.info(f"✅ 提取并存储关键事实: {result.strip()}")
            else:
                logger.info(f"ℹ️ 无需存储: {user_message}")

        except Exception as e:
            # 提取失败不影响主流程
            logger.warning(f"⚠️ 信息提取失败: {e}")

    def _summarize_conversation(self, session_id, message_count=10):
        """
        定期对对话内容生成摘要并存储

        Args:
            session_id: 会话ID
            message_count: 每隔多少条消息生成一次摘要
        """
        if not self.client:
            return  # 占位模式不生成摘要

        try:
            # 获取本次会话的所有历史消息
            history = self.conversation.get_history(
                session_id, limit=message_count
            )

            if len(history) < 3:  # 太少不值得摘要
                return

            # 构建对话内容
            conversation_text = "\n".join([
                f"{'用户' if msg['role'] == 'user' else '小乐'}: {msg['content']}"
                for msg in history
            ])

            # 让AI生成对话摘要
            summary_prompt = f"""请为以下对话生成一个简洁的摘要，重点记录：
1. 用户的状态和心情（如困、开心、担心等）
2. 讨论的主要话题
3. 重要的上下文信息（正在做什么、计划做什么等）
4. 用户的需求或问题

对话内容：
{conversation_text}

请用1-3句话总结，格式如："用户表示很困还在聊天，讨论了课程安排的问题。"
如果对话只是简单问候或没有实质内容，返回"无"。"""

            if self.api_type == "deepseek":
                summary = self._call_deepseek(
                    system_prompt="你是对话摘要助手，提取对话中的关键信息。",
                    user_prompt=summary_prompt
                )
            else:
                summary = self._call_claude(
                    system_prompt="你是对话摘要助手，提取对话中的关键信息。",
                    user_prompt=summary_prompt
                )

            # 存储摘要
            invalid_results = ["无", "无。", "None", "none", ""]
            if summary and summary.strip() not in invalid_results:
                date_str = datetime.now().strftime("%Y-%m-%d")
                self.memory.remember(
                    summary.strip(),
                    tag=f"conversation:{date_str}"
                )
                logger.info(f"📝 对话摘要已存储: {summary.strip()[:50]}...")

        except Exception as e:
            logger.warning(f"⚠️ 对话摘要生成失败: {e}")

    def act(self, command):
        """执行任务：思考 -> 记录 -> 输出"""
        thought = self.think(command, use_memory=True)

        # 额外记录到 task 标签
        self.memory.remember(
            f"执行任务：{command} => {thought}",
            tag="task"
        )

        return thought

    def chat(self, prompt, session_id=None, user_id="default_user",
             response_style="balanced"):
        """
        v0.6.0: 支持上下文的对话方法（支持响应风格）

        Args:
            prompt: 用户消息
            session_id: 会话ID（None则创建新会话）
            user_id: 用户ID
            response_style: 响应风格 (concise/balanced/detailed/professional)
        """
        # 如果没有session_id，创建新会话
        if not session_id:
            session_id = self.conversation.create_session(
                user_id=user_id,
                title=prompt[:50] + "..." if len(prompt) > 50 else prompt
            )

        # v0.5.0: 检查未读提醒
        pending_reminders = []
        try:
            from reminder_manager import get_reminder_manager
            reminder_mgr = get_reminder_manager()
            pending_reminders = asyncio.run(
                reminder_mgr.get_pending_reminders(user_id, limit=3)
            )
        except Exception as e:
            logger.warning(f"检查提醒失败: {e}")

        # 获取对话历史
        history = self.conversation.get_history(session_id, limit=5)

        # v0.4.0: 智能工具调用 - 先分析是否需要调用工具
        tool_result = None

        # v0.8.0: 任务关键词预检查 (优先级高于工具调用)
        task_keywords = [
            '创建任务', '添加任务', '新建任务',
            '帮我准备', '帮我整理', '帮我规划',
            '帮我安排', '帮我计划', '帮我组织'
        ]
        skip_tool_check = any(keyword in prompt for keyword in task_keywords)

        if not skip_tool_check:
            try:
                # v0.6.0 Phase 3: 使用增强的意图识别
                context = {
                    'recent_messages': history,
                    'user_id': user_id,
                    'session_id': session_id
                }
                tool_calls = self.enhanced_selector.analyze_intent(
                    prompt, context)

                if tool_calls:
                    # 执行工具调用（按优先级）
                    for tool_call in tool_calls:
                        result = self.enhanced_selector.execute_with_retry(
                            tool_call, max_retries=2
                        )
                        if result.success:
                            tool_result = result.data
                            break
                else:
                    # 回退到旧的工具调用逻辑
                    tool_result = self._auto_call_tool(
                        prompt, user_id, session_id)
            except Exception as e:
                logger.warning(f"增强工具调用失败: {e}")
                # 回退到旧逻辑
                try:
                    tool_result = self._auto_call_tool(
                        prompt, user_id, session_id)
                except Exception as e2:
                    logger.warning(f"旧工具调用也失败: {e2}")

        # v0.8.0: 任务识别和执行
        task_result = None
        try:
            # 识别是否为复杂任务
            task_check = self.identify_complex_task(prompt, user_id)
            if task_check.get('is_task', False):
                confidence = task_check.get('confidence', 0)
                if confidence >= 0.7:
                    logger.info(
                        f"识别到复杂任务(置信度:{confidence}): "
                        f"{task_check.get('title')}"
                    )

                    # 拆解任务
                    decompose_result = self.decompose_task(
                        task_title=task_check['title'],
                        task_description=task_check.get('description', ''),
                        user_id=user_id
                    )

                    if decompose_result.get('success'):
                        # 创建任务
                        task_id = self.task_manager.create_task(
                            user_id=user_id,
                            session_id=session_id,
                            title=task_check['title'],
                            description=task_check.get('description', ''),
                            priority=decompose_result.get('priority', 0)
                        )

                        if task_id:
                            # 创建步骤
                            for step in decompose_result.get('steps', []):
                                self.task_manager.create_step(
                                    task_id=task_id,
                                    step_num=step.get('step_num', 0),
                                    description=step.get('description', ''),
                                    action_type=step.get('action_type'),
                                    action_params=step.get('action_params')
                                )

                            # 执行任务
                            task_result = self.task_executor.execute_task(
                                task_id=task_id,
                                user_id=user_id,
                                session_id=session_id
                            )

                            logger.info(f"任务执行结果: {task_result}")
        except Exception as e:
            logger.warning(f"任务处理失败: {e}", exc_info=True)

        # v0.6.0: 调用 AI 生成回复（带上下文、工具结果和响应风格）
        reply = self._think_with_context(
            prompt, history, tool_result or task_result, response_style
        )

        # v0.6.0 Phase 3 Day 4: 对话质量增强
        try:
            reply = self.dialogue_enhancer.enhance_response(
                reply, prompt, history, response_style
            )
        except Exception as e:
            logger.warning(f"对话质量增强失败: {e}")

        # v0.5.0: 如果有未读提醒，在回复前插入提醒
        if pending_reminders:
            reminder_text = self._format_reminders(pending_reminders)
            reply = reminder_text + "\n\n" + reply

        # 保存用户消息和助手回复到会话表
        self.conversation.add_message(session_id, "user", prompt)
        self.conversation.add_message(session_id, "assistant", reply)

        # 智能提取：让AI判断是否有关键事实需要记住
        self._extract_and_remember(prompt)

        # v0.3.0: 模式学习（从用户消息中学习使用模式）
        try:
            self.pattern_learner.learn_from_message(
                user_id, prompt, session_id
            )
        except Exception as e:
            logger.warning(f"模式学习失败: {e}")

        # v0.3.0: 记录用户行为数据
        try:
            self.behavior_analyzer.record_session_behavior(user_id, session_id)
        except Exception as e:
            logger.warning(f"行为数据记录失败: {e}")

        # v0.6.0: 主动问答分析（检测是否需要追问）
        followup_info = None
        try:
            analysis = self.proactive_qa.analyze_conversation(
                session_id, user_id
            )
            if analysis.get("needs_followup"):
                questions = analysis.get("questions", [])
                if questions:
                    # 取置信度最高的问题
                    best_question = max(
                        questions, key=lambda x: x.get("confidence", 0)
                    )

                    # v0.6.0: 检查置信度是否达到阈值
                    confidence = best_question["confidence"]
                    threshold = self.proactive_qa.confidence_threshold

                    if confidence >= threshold:
                        # 生成追问
                        followup = (
                            self.proactive_qa.generate_followup_question(
                                best_question["question"],
                                best_question["missing_info"],
                                best_question.get("ai_response", "")
                            )
                        )
                        # 保存追问记录
                        question_id = (
                            self.proactive_qa.save_proactive_question(
                                session_id=session_id,
                                user_id=user_id,
                                original_question=best_question["question"],
                                question_type=best_question["type"],
                                missing_info=best_question["missing_info"],
                                confidence=confidence,
                                followup_question=followup
                            )
                        )
                        followup_info = {
                            "id": question_id,
                            "followup": followup,
                            "confidence": confidence
                        }
                        logger.info(
                            f"触发追问 (置信度: {confidence}% >= {threshold}%)"
                        )
                    else:
                        logger.debug(
                            f"置信度不足 ({confidence}% < {threshold}%)，跳过追问"
                        )
        except Exception as e:
            logger.warning(f"主动问答分析失败: {e}")

        # v0.6.1: 定期生成对话摘要（每5轮对话）
        try:
            history = self.conversation.get_history(session_id, limit=1)
            if history:
                # 获取当前会话的消息总数（简单估算：历史记录数量）
                message_count = len(
                    self.conversation.get_history(session_id, limit=100)
                )
                # 每5轮对话（10条消息）生成一次摘要
                if message_count > 0 and message_count % 10 == 0:
                    self._summarize_conversation(session_id, message_count=10)
        except Exception as e:
            logger.warning(f"对话摘要失败: {e}")

        result = {
            "session_id": session_id,
            "reply": reply
        }
        if followup_info:
            result["followup"] = followup_info

        return result

    def _quick_intent_match(self, prompt):
        """
        v0.6.0: 快速意图匹配 - 无需AI调用的常见模式识别

        返回: None 或 {"needs_tool": bool, "tool_name": str, "parameters": dict}
        """
        prompt_lower = prompt.lower().strip()

        # 1. 时间查询 - 直接模式
        time_patterns = ['现在几点', '几点了', '当前时间', '现在时间', '今天日期', '今天几号']
        if any(p in prompt_lower for p in time_patterns):
            return {
                "needs_tool": True,
                "tool_name": "time",
                "parameters": {"format": "full"}
            }

        # 2. 系统信息 - 直接模式
        if any(word in prompt_lower for word in ['cpu', '内存', '磁盘', '系统信息']):
            info_type = "all"
            if 'cpu' in prompt_lower:
                info_type = "cpu"
            elif '内存' in prompt_lower:
                info_type = "memory"
            elif '磁盘' in prompt_lower:
                info_type = "disk"

            return {
                "needs_tool": True,
                "tool_name": "system_info",
                "parameters": {"info_type": info_type}
            }

        # 3. 计算器 - 简单数学表达式检测
        import re
        # 检测数学表达式 (数字 + 运算符)
        math_pattern = r'[\d\+\-\*/\(\)\s]+'
        if re.match(r'^\s*' + math_pattern + r'\s*[=?]?\s*$', prompt) and \
           any(op in prompt for op in ['+', '-', '*', '/', '×', '÷']):
            # 清理表达式
            expression = prompt.replace('=', '').replace('?', '').strip()
            expression = expression.replace('×', '*').replace('÷', '/')
            return {
                "needs_tool": True,
                "tool_name": "calculator",
                "parameters": {"expression": expression}
            }

        # 4. 搜索 - 明显的搜索意图
        search_keywords = [
            '搜索', '查询', '查一下', '搜一下', '找一下',
            '百度', '谷歌', '帮我找', '帮我查'
        ]

        # 扩展: 实时信息关键词 (需要上网查询的内容)
        realtime_keywords = [
            'iphone 17', 'iphone17', 'iphone 16', 'iphone16',
            '最新', '新闻', '消息', '资讯',
            '什么时候发布', '何时发布', '上市时间', '发售时间',
            '最新价格', '现在价格',
            '2025年', '2024年9月', '今年',
        ]

        # 检查是否包含搜索关键词
        has_search_keyword = any(kw in prompt_lower for kw in search_keywords)

        # 检查是否包含实时信息关键词
        has_realtime_keyword = any(
            kw in prompt_lower for kw in realtime_keywords
        )

        # 调试日志
        if has_search_keyword or has_realtime_keyword:
            logger.info(
                f"🔍 快速规则匹配: 搜索={has_search_keyword}, "
                f"实时={has_realtime_keyword}, prompt='{prompt[:50]}'"
            )

        if has_search_keyword or has_realtime_keyword:
            # 如果是明确搜索,去除触发词;如果是实时信息,保留完整prompt
            if has_search_keyword and not has_realtime_keyword:
                query = prompt
                for kw in search_keywords:
                    query = query.replace(kw, '')
                query = query.strip()
            else:
                query = prompt.strip()

            # 确保有实际搜索内容
            if query and len(query) > 2:
                logger.info(f"✅ 触发搜索工具, query='{query[:50]}'")
                return {
                    "needs_tool": True,
                    "tool_name": "search",
                    "parameters": {"query": query, "max_results": 5}
                }
            else:
                logger.warning(f"⚠️  搜索query太短或为空: '{query}'")
                return None        # 5. 提醒 - 明确的提醒请求
        reminder_keywords = ['提醒我', '记得', '别忘了', '设置提醒', '定时提醒']
        if any(kw in prompt_lower for kw in reminder_keywords):
            # 需要AI解析时间和内容，返回None让AI处理
            return None

        # 6. 天气 - 需要提取城市，让AI处理
        if '天气' in prompt_lower:
            return None

        # 7. 文件操作 - 需要AI精确解析
        file_keywords = ['读取文件', '写入文件', '文件列表', '搜索文件']
        if any(kw in prompt_lower for kw in file_keywords):
            return None

        # 无匹配 - 可能是普通对话或需要AI分析
        return None

    def _get_style_instruction(self, style):
        """
        v0.6.0: 获取响应风格的指令

        Args:
            style: 响应风格 (concise/balanced/detailed/professional)

        Returns:
            str: 风格指令
        """
        styles = {
            'concise': '7. 响应风格：简洁模式 - 使用1-2句话简短回答，直接切中要点',
            'balanced': '7. 响应风格：均衡模式 - 提供适中长度的回答，既清晰又完整',
            'detailed': '7. 响应风格：详细模式 - 提供详细全面的解答，包含背景信息和例子',
            'professional': '7. 响应风格：专业模式 - 使用正式专业的语气，结构化表达'
        }
        return styles.get(style, styles['balanced'])

    def _get_llm_parameters(self, style):
        """
        v0.6.0: 根据响应风格获取LLM调用参数

        Args:
            style: 响应风格

        Returns:
            dict: {temperature, max_tokens, top_p}
        """
        params = {
            'concise': {
                'temperature': 0.3,  # 更确定性
                'max_tokens': 256,   # 更短
                'top_p': 0.8
            },
            'balanced': {
                'temperature': 0.5,  # 适中
                'max_tokens': 512,   # 适中
                'top_p': 0.9
            },
            'detailed': {
                'temperature': 0.7,  # 更创造性
                'max_tokens': 1024,  # 更长
                'top_p': 0.95
            },
            'professional': {
                'temperature': 0.4,  # 较确定性
                'max_tokens': 768,   # 较长
                'top_p': 0.85
            }
        }
        return params.get(style, params['balanced'])

    def _auto_call_tool(self, prompt, user_id, session_id):
        """
        v0.4.0: 智能工具调用
        分析用户消息，自动识别意图并调用相应工具
        """
        # 使用AI分析用户意图
        intent_analysis = self._analyze_intent(prompt)

        if not intent_analysis.get("needs_tool"):
            return None

        tool_name = intent_analysis.get("tool_name")
        params = intent_analysis.get("parameters", {})

        if not tool_name:
            return None

        # 添加调试日志
        logger.info(f"🔧 准备调用工具: {tool_name}")
        logger.info(f"📋 工具参数: {params}")

        # 调用工具（异步方法需要同步执行）
        try:
            # 使用asyncio.run()在同步上下文中执行异步工具调用
            result = asyncio.run(self.tool_registry.execute(
                tool_name=tool_name,
                params=params,
                user_id=user_id,
                session_id=session_id
            ))
            logger.info(
                f"✅ 工具调用成功: {tool_name} -> {result.get('success')}"
            )
            return result
        except Exception as e:
            logger.error(f"❌ 工具调用失败: {tool_name} - {e}")
            return None

    def _analyze_intent(self, prompt):
        """
        v0.6.0: 优化的意图识别算法
        使用AI分析用户消息，判断是否需要调用工具及具体参数

        改进点：
        1. 更清晰的工具分类和优先级
        2. 精简prompt减少token消耗
        3. 添加快速规则匹配（减少AI调用）
        4. 改进参数提取逻辑

        返回: {"needs_tool": bool, "tool_name": str, "parameters": dict}
        """
        # v0.6.0: 快速规则匹配 - 常见模式直接识别，无需AI
        quick_match = self._quick_intent_match(prompt)
        if quick_match:
            logger.info(f"✅ 快速规则匹配: {quick_match['tool_name']}")
            return quick_match

        # 获取可用工具列表
        tools_info = []
        for tool_name in self.tool_registry.get_tool_names():
            tool = self.tool_registry.get(tool_name)
            if tool and tool.enabled:
                params_desc = ", ".join([
                    f"{p.name}({p.param_type})"
                    for p in tool.parameters
                ])
                tools_info.append(
                    f"- {tool_name}: {tool.description}"
                    f"{' [参数: ' + params_desc + ']' if params_desc else ''}"
                )

        if not tools_info:
            return {"needs_tool": False}

        # 获取用户的位置信息（从记忆中查找）
        user_context = ""
        try:
            # 从facts标签中查找城市、地点相关信息
            location_memories = self.memory.recall(tag="facts", limit=20)
            if location_memories:
                user_context = (
                    "\n\n用户背景信息（从记忆库提取）：\n"
                    + "\n".join(location_memories)
                )
        except Exception as e:
            logger.warning(f"获取用户位置信息失败: {e}")

        # v0.6.0: 精简的意图分析 prompt（减少50% token消耗）
        analysis_prompt = f"""用户: "{prompt}"{user_context}

工具: {chr(10).join(tools_info)}

规则:
1. weather工具 - 需要城市名: city(城市名), query_type(now/3d/7d)
2. system_info - info_type(cpu/memory/disk/all)
3. time - format(full/date/time)
4. calculator - expression(数学表达式)
5. reminder - content(内容), time_desc(时间), title(可选)
6. search - query(关键词), max_results(可选)
7. file - operation(read/write/list/search), path(路径),
   content(写入内容), pattern(搜索模式), recursive(可选)
8. 普通对话 -> needs_tool=false

**search工具优先级最高** - 以下情况必须使用:
- 用户明确要求"搜索"、"查一下"、"帮我找"
- 询问最新/实时信息(产品发布、新闻、价格)
- 涉及2024年9月后的信息(iPhone 17/16等新产品)
- 询问"什么时候发布"、"上市时间"等
- 你的知识可能过时的内容

天气规则:
- 用户指定城市 -> 使用该城市
- 从位置信息提取城市名（只提取城市名如"深圳"）
- 无城市信息 -> needs_tool=false
- query_type: "明天"/"后天"=3d, "未来几天"/"本周"=7d, 其他=now

返回JSON（无markdown）:
{{
  "needs_tool": bool,
  "tool_name": "工具名或null",
  "parameters": {{"参数": "值"}},
  "reason": "简短理由"
}}"""

        try:
            if self.api_type == "deepseek":
                result = self._call_deepseek(
                    system_prompt="你是智能工具选择助手，精准识别用户意图并返回JSON格式分析结果。",
                    user_prompt=analysis_prompt
                )
            else:
                result = self._call_claude(
                    system_prompt="你是智能工具选择助手，精准识别用户意图并返回JSON格式分析结果。",
                    user_prompt=analysis_prompt
                )

            # 解析JSON结果
            import json
            # 清理可能的markdown代码块标记
            result = result.strip()
            if result.startswith("```"):
                result = result.split("```")[1]
                if result.startswith("json"):
                    result = result[4:]
            result = result.strip()

            analysis = json.loads(result)
            logger.info(f"意图分析: {analysis.get('reason', 'N/A')}")
            return analysis

        except Exception as e:
            logger.warning(f"意图分析失败: {e}")
            return {"needs_tool": False}

    def _think_with_context(self, prompt, history, tool_result=None,
                            response_style="balanced"):
        """
        v0.6.0: 带上下文的思考方法（支持响应风格）

        同时使用会话历史、长期记忆、工具结果和响应风格配置
        """
        if not self.client:
            return f"（占位模式）你说的是：{prompt}"

        try:
            # 获取当前时间和星期
            now = datetime.now()
            current_datetime = now.strftime("%Y年%m月%d日 %H:%M")
            weekday_names = ['周一', '周二', '周三', '周四',
                             '周五', '周六', '周日']
            current_weekday = weekday_names[now.weekday()]

            # v0.6.0: 根据响应风格调整系统提示词
            style_instructions = self._get_style_instruction(response_style)

            system_prompt = (
                f"你是小乐AI管家，一个诚实、友好的个人助手。\n\n"
                f"核心原则：\n"
                f"1. 你是对话助手，没有连接智能设备（无手环/摄像头/传感器）\n"
                f"2. 优先使用对话历史中的上下文信息\n"
                f"3. 同时参考下方记忆库中的长期信息（用户的基本资料、喜好等）\n"
                f"4. 记忆库按时间倒序排列，最新信息在前，优先使用最新信息\n"
                f"5. 如果记忆库和对话历史都没有相关信息，诚实说'您还没告诉我'\n"
                f"6. 绝不编造数据、假装有设备、或推测未知信息\n"
                f"7. 【课程表回答规则】：\n"
                f"   - 时段划分：上午=晨读+第1-4节，下午=第5-7节，晚上=课后辅导\n"
                f"   - 只列出有课的时段，跳过\"无课\"的节次\n"
                f"   - 格式：时段+课程名称，例如\"晨读：科学(6)、第4节：科学(5)\"\n"
                f"   - 如果某个时间段完全没课，明确说明\n"
                f"   - 示例：\"今天上午有晨读的科学(6)和第4节的科学(5)\"\n"
                f"{style_instructions}\n"
                f"当前时间：{current_datetime}（{current_weekday}）\n"
            )

            # v0.4.0: 如果有工具执行结果，添加到系统提示词
            if tool_result and tool_result.get('success'):
                # 格式化工具结果
                tool_data = tool_result.get('data') or tool_result
                if isinstance(tool_data, dict):
                    # 去除不需要显示的字段
                    display_data = {
                        k: v for k, v in tool_data.items()
                        if k not in ['success', 'user_id', 'session_id']
                    }
                    tool_info_text = str(display_data)
                else:
                    tool_info_text = str(tool_data)

                tool_info = (
                    f"\n\n📊 工具执行结果：\n"
                    f"{tool_info_text}\n"
                    f"请根据这个工具结果，用自然友好的语言回答用户的问题。"
                )
                system_prompt += tool_info

            # 添加长期记忆到系统提示词
            # 1. 优先获取 facts 标签的关键事实（用户主动告知的真实信息）
            facts_memories = self.memory.recall(tag="facts", limit=20)

            # 2. 使用语义搜索查找相关记忆（不限标签，搜索所有记忆）
            semantic_memories = []
            if hasattr(self.memory, 'semantic_recall'):
                # 语义搜索用户问题相关的记忆（包括图片、事实等所有内容）
                semantic_memories = self.memory.semantic_recall(
                    query=prompt,
                    tag=None,  # 不限制标签，搜索所有记忆
                    limit=10,
                    min_score=0.05  # 降低阈值，增加召回
                )

            # 3. 获取最近的 image 记忆（课程表等重要信息）
            image_memories = []
            try:
                from db_setup import Memory
                recent_images = self.memory.session.query(Memory).filter(
                    Memory.tag.like('image:%')
                ).order_by(Memory.created_at.desc()).limit(3).all()
                image_memories = [mem.content for mem in recent_images]
            except Exception as e:
                logger.warning(f"获取图片记忆失败: {e}")

            # 4. 获取最近的对话摘要（了解之前聊了什么）
            conversation_memories = []
            try:
                from db_setup import Memory
                recent_conversations = self.memory.session.query(
                    Memory
                ).filter(
                    Memory.tag.like('conversation:%')
                ).order_by(Memory.created_at.desc()).limit(3).all()
                conversation_memories = [
                    mem.content for mem in recent_conversations
                ]
            except Exception as e:
                logger.warning(f"获取对话摘要失败: {e}")

            # 5. 获取最近的 general 记忆（补充上下文）
            recent_memories = self.memory.recall(tag="general", limit=3)

            # 6. 合并去重：图片记忆 > facts > 对话摘要 > 语义相关 > 最近记忆
            all_memories = []
            seen = set()

            # 🔝 最高优先级：图片记忆（课程表等重要信息）- 提到最前面！
            for mem in image_memories:
                if mem not in seen:
                    all_memories.append(mem)
                    seen.add(mem)

            # 第二优先级：facts 标签（关键事实，但限制数量）
            facts_count = 0
            for mem in facts_memories:
                if mem not in seen and facts_count < 10:  # 最多10条facts
                    all_memories.append(mem)
                    seen.add(mem)
                    facts_count += 1

            # 第三优先级：对话摘要（了解之前的对话上下文）
            for mem in conversation_memories:
                if mem not in seen and len(all_memories) < 30:
                    all_memories.append(mem)
                    seen.add(mem)

            # 第四优先级：语义相关记忆（问题相关）
            # semantic_memories可能是字典列表，需要提取content
            for mem in semantic_memories:
                mem_content = (
                    mem if isinstance(mem, str)
                    else mem.get('content', str(mem))
                )
                if mem_content not in seen and len(all_memories) < 30:
                    all_memories.append(mem_content)
                    seen.add(mem_content)

            # 第五优先级：最近记忆（补充上下文）
            for mem in recent_memories:
                if mem not in seen and len(all_memories) < 30:
                    all_memories.append(mem)
                    seen.add(mem)

            # 调试：打印召回的记忆
            logger.info(f"📚 召回了 {len(all_memories)} 条记忆")
            for i, mem in enumerate(all_memories[:20], 1):  # 打印前20条
                preview = mem[:150] if isinstance(mem, str) else str(mem)[:150]
                logger.info(f"  记忆{i}: {preview}...")
                # 特别标记图片记忆（真正的课程表内容）
                if isinstance(mem, str) and len(mem) > 200:
                    # 课程表内容通常很长，且包含多个"节"和"课程"
                    course_indicators = mem.count('节') + mem.count('科学') + \
                        mem.count('数学') + mem.count('语文')
                    if course_indicators >= 3:  # 至少出现3次课程相关词
                        logger.info("    ⭐ [课程表内容]")

            if all_memories:
                context = "记忆库（按时间倒序，最新在前）：\n" + \
                          "\n".join(all_memories)
                system_prompt += f"\n\n{context}"

            # 构建消息列表（包含历史）
            messages = []
            for msg in history:
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
            messages.append({"role": "user", "content": prompt})

            # v0.6.0: 根据API类型调用（传递响应风格）
            if self.api_type == "deepseek":
                return self._call_deepseek_with_history(
                    system_prompt, messages, response_style
                )
            elif self.api_type == "claude":
                return self._call_claude_with_history(
                    system_prompt, messages, response_style
                )

        except Exception as e:
            return f"抱歉，我遇到了一些问题：{str(e)}"

    @retry_with_backoff(
        max_retries=3,
        initial_delay=1.0,
        exceptions=(requests.Timeout, requests.ConnectionError)
    )
    @handle_api_errors
    @log_execution
    def _call_deepseek_with_history(
        self, system_prompt, messages, response_style="balanced"
    ):
        """
        v0.6.0: DeepSeek API 多轮对话（支持响应风格）
        """
        logger.info(f"调用 DeepSeek 多轮对话 - 消息数: {len(messages)}")

        # v0.6.0: 获取风格参数
        llm_params = self._get_llm_parameters(response_style)

        headers = {
            "Authorization": f"Bearer {self.deepseek_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt}
            ] + messages,
            "temperature": llm_params['temperature'],
            "max_tokens": llm_params['max_tokens'],
            "top_p": llm_params.get('top_p', 0.9)
        }

        response = requests.post(
            self.deepseek_url,
            headers=headers,
            json=data,
            timeout=60
        )

        response.raise_for_status()
        result = response.json()
        reply = result["choices"][0]["message"]["content"]
        logger.info(
            f"DeepSeek 多轮对话响应成功 - 回复长度: {len(reply)}, "
            f"风格: {response_style}"
        )
        return reply

    def _format_reminders(self, reminders: list) -> str:
        """
        格式化提醒消息

        Args:
            reminders: 提醒列表

        Returns:
            格式化后的提醒文本
        """
        if not reminders:
            return ""

        reminder_texts = []
        for reminder in reminders:
            priority_emoji = {
                1: "🔴",  # 最高优先级
                2: "🟠",
                3: "🟡",
                4: "🟢",
                5: "⚪"   # 最低优先级
            }.get(reminder.get('priority', 3), "🔔")

            title = reminder.get('title', '提醒')
            content = reminder.get('content', '')

            reminder_texts.append(f"{priority_emoji} **{title}**：{content}")

        if len(reminders) == 1:
            header = "🔔 **提醒** "
        else:
            header = f"🔔 **你有 {len(reminders)} 条提醒** "

        return header + "\n" + "\n".join(reminder_texts)

    @retry_with_backoff(
        max_retries=3,
        initial_delay=1.0,
        exceptions=(Exception,)
    )
    @handle_api_errors
    @log_execution
    @retry_with_backoff(
        max_retries=3,
        initial_delay=1.0,
        exceptions=(Exception,)
    )
    @handle_api_errors
    @log_execution
    def _call_claude_with_history(
        self, system_prompt, messages, response_style="balanced"
    ):
        """
        v0.6.0: Claude API 多轮对话（支持响应风格）
        """
        logger.info(f"调用 Claude 多轮对话 - 消息数: {len(messages)}")

        # v0.6.0: 获取风格参数
        llm_params = self._get_llm_parameters(response_style)

        response = self.client.messages.create(
            model=self.model,
            max_tokens=llm_params['max_tokens'],
            temperature=llm_params['temperature'],
            top_p=llm_params.get('top_p', 0.9),
            system=system_prompt,
            messages=messages
        )
        reply = response.content[0].text
        logger.info(
            f"Claude 多轮对话响应成功 - 回复长度: {len(reply)}, "
            f"风格: {response_style}"
        )
        return reply

    # ==================== v0.8.0 任务管理功能 ====================

    def identify_complex_task(self, user_input: str, user_id: str) -> dict:
        """
        识别用户输入是否为复杂任务

        Args:
            user_input: 用户输入
            user_id: 用户ID

        Returns:
            包含is_task和task_info的字典
        """
        prompt = f"""
请分析用户的输入是否为一个需要多步骤执行的复杂任务。

复杂任务的特征:
1. 需要多个步骤才能完成
2. 涉及多个工具或操作
3. 步骤之间有依赖关系
4. 需要一定时间完成

用户输入: {user_input}

请以JSON格式回答:
{{
    "is_task": true/false,
    "confidence": 0.0-1.0,
    "title": "任务标题",
    "description": "任务描述",
    "reasoning": "判断理由"
}}

例子:
- "帮我准备周末的野餐" -> is_task: true (需要查天气、列物品、设提醒)
- "今天天气怎么样" -> is_task: false (单个查询)
- "提醒我明天9点开会" -> is_task: false (单个提醒)
- "帮我规划下周的学习计划" -> is_task: true (需要多步分析和安排)
"""

        try:
            response = self._call_deepseek(prompt)
            # 提取JSON
            import json
            import re
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                result = json.loads(json_match.group())
                logger.info(
                    f"任务识别: {result.get('title', 'N/A')} - "
                    f"是否为任务: {result.get('is_task')}"
                )
                return result
            else:
                return {"is_task": False, "reasoning": "无法解析响应"}

        except Exception as e:
            logger.error(f"任务识别失败: {e}")
            return {"is_task": False, "reasoning": f"错误: {str(e)}"}

    def decompose_task(
        self,
        task_title: str,
        task_description: str,
        user_id: str
    ) -> dict:
        """
        将复杂任务拆解为多个步骤

        Args:
            task_title: 任务标题
            task_description: 任务描述
            user_id: 用户ID

        Returns:
            包含success和steps的字典
        """
        # 获取可用工具信息
        tools_info = "\n".join([
            f"- {tool['name']}: {tool['description']}"
            for tool in self.tool_registry.list_tools()
        ])

        prompt = f"""
请将以下任务拆解为具体的执行步骤:

任务标题: {task_title}
任务描述: {task_description}

可用工具:
{tools_info}

要求:
1. 每个步骤要具体、可执行
2. 步骤之间要有逻辑顺序
3. 需要调用工具的要标明工具名称和参数
4. 需要用户确认的要标明
5. 每个步骤包含: 序号、描述、操作类型、所需参数

以JSON格式返回:
{{
    "steps": [
        {{
            "step_num": 1,
            "description": "步骤描述",
            "action_type": "tool_call/user_confirm/wait/info",
            "action_params": {{
                "tool_name": "工具名",
                "params": {{}},
                "notes": "备注"
            }}
        }}
    ]
}}

示例任务"准备周末野餐":
{{
    "steps": [
        {{
            "step_num": 1,
            "description": "查询周末天气预报",
            "action_type": "tool_call",
            "action_params": {{
                "tool_name": "weather",
                "params": {{"city": "当前城市"}},
                "notes": "确定天气情况"
            }}
        }},
        {{
            "step_num": 2,
            "description": "列出野餐所需物品清单",
            "action_type": "info",
            "action_params": {{
                "notes": "生成物品清单供用户参考"
            }}
        }},
        {{
            "step_num": 3,
            "description": "设置购物提醒",
            "action_type": "user_confirm",
            "action_params": {{
                "question": "是否需要设置购物提醒?",
                "if_yes": "tool_call:reminder"
            }}
        }}
    ]
}}
"""

        try:
            response = self._call_deepseek(prompt)
            # 提取JSON
            import json
            import re
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                result = json.loads(json_match.group())
                steps = result.get('steps', [])
                logger.info(f"任务拆解完成: 共 {len(steps)} 个步骤")
                return {
                    'success': True,
                    'steps': steps,
                    'priority': result.get('priority', 0)
                }
            else:
                logger.error("无法解析任务拆解结果")
                return {'success': False, 'error': '无法解析结果'}

        except Exception as e:
            logger.error(f"任务拆解失败: {e}")
            return {'success': False, 'error': str(e)}
