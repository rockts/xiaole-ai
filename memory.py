from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, func, or_
from db_setup import Memory
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from semantic_search import SemanticSearchManager

load_dotenv()

# 优先使用 DATABASE_URL，如果没有则构建PostgreSQL URL
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
Session = sessionmaker(bind=engine)


class MemoryManager:
    def __init__(self, enable_vector_search=True):  # 默认启用语义搜索
        self.session = Session()
        self.enable_vector_search = enable_vector_search

        # 初始化语义搜索管理器
        if self.enable_vector_search:
            try:
                self.semantic_search = SemanticSearchManager()
                print("✅ 语义搜索已启用")
            except Exception as e:
                print(f"⚠️ 语义搜索初始化失败: {e}，降级到关键词搜索")
                self.enable_vector_search = False
                self.semantic_search = None
        else:
            self.semantic_search = None

    def remember(self, content, tag="general", initial_importance=0.5):
        """
        存储记忆（v0.6.0: 支持初始重要性分数）

        Args:
            content: 记忆内容
            tag: 标签
            initial_importance: 初始重要性评分 (0-1)
        """
        memory = Memory(
            content=content,
            tag=tag,
            importance_score=initial_importance
        )
        self.session.add(memory)
        self.session.commit()

        # 添加到语义搜索索引
        if self.enable_vector_search and self.semantic_search:
            try:
                self.semantic_search.add_memory(memory.id, content, tag)
            except Exception as e:
                print(f"添加语义索引失败: {e}")
            tag: 标签
            initial_importance: 初始重要性分数(0-1)
        """
        mem = Memory(
            content=content,
            tag=tag,
            importance_score=initial_importance
        )
        self.session.add(mem)
        self.session.commit()
        return mem.id

    def recall(self, tag="general", keyword=None, limit=None):
        """
        召回记忆
        tag: 记忆标签
        keyword: 关键词搜索（可选）
        limit: 限制返回数量（可选）
        """
        query = self.session.query(Memory).filter(Memory.tag == tag)

        # 如果有关键词，进行模糊搜索
        if keyword:
            query = query.filter(Memory.content.contains(keyword))

        # 按时间倒序
        query = query.order_by(Memory.created_at.desc())

        # 限制数量
        if limit:
            query = query.limit(limit)

        memories = query.all()
        return [m.content for m in memories]

    def recall_recent(self, hours=24, tag=None, limit=10):
        """
        召回最近时间段的记忆
        hours: 最近N小时（默认24小时）
        tag: 可选标签过滤
        limit: 返回数量限制
        """
        time_threshold = datetime.now() - timedelta(hours=hours)

        query = self.session.query(Memory).filter(
            Memory.created_at >= time_threshold
        )

        if tag:
            query = query.filter(Memory.tag == tag)

        query = query.order_by(Memory.created_at.desc()).limit(limit)
        memories = query.all()
        return [m.content for m in memories]

    def recall_by_keywords(self, keywords, tag=None, limit=10):
        """
        通过多个关键词搜索记忆（OR 逻辑）
        keywords: 关键词列表
        tag: 可选标签过滤
        limit: 返回数量限制
        返回: 包含完整信息的字典列表
        """
        if not keywords:
            return []

        # 构建关键词过滤条件
        keyword_filters = [
            Memory.content.contains(kw) for kw in keywords
        ]

        query = self.session.query(Memory).filter(or_(*keyword_filters))

        if tag:
            query = query.filter(Memory.tag == tag)

        query = query.order_by(Memory.created_at.desc()).limit(limit)
        memories = query.all()

        # 返回完整的记忆信息
        return [{
            'content': m.content,
            'tag': m.tag,
            'timestamp': m.created_at.strftime('%Y-%m-%d %H:%M:%S')
        } for m in memories]

    def get_stats(self):
        """获取记忆统计信息"""
        # 总记忆数
        total = self.session.query(func.count(Memory.id)).scalar()

        # 按标签统计
        tag_stats = self.session.query(
            Memory.tag,
            func.count(Memory.id)
        ).group_by(Memory.tag).all()

        return {
            "total": total,
            "by_tag": {tag: count for tag, count in tag_stats}
        }

    def semantic_recall(self, query, tag=None, limit=10, min_score=0.15):
        """
        语义搜索记忆（基于TF-IDF + 余弦相似度）

        Args:
            query: 查询文本（例如："我几岁"、"运动爱好"）
            tag: 可选标签过滤
            limit: 返回数量限制
            min_score: 最低相似度阈值（0-1）

        Returns:
            [{content, tag, timestamp}] 按相似度排序
        """
        if not self.enable_vector_search or not self.semantic_search:
            # 降级到关键词搜索
            print("⚠️ 语义搜索不可用，使用关键词搜索")
            keywords = query.split()
            return self.recall_by_keywords(keywords, tag=tag, limit=limit)

        try:
            # 查询所有记忆
            query_obj = self.session.query(Memory)
            if tag:
                query_obj = query_obj.filter(Memory.tag == tag)

            all_memories = query_obj.all()

            if not all_memories:
                return []

            # 构建文档列表：(id, content)
            documents = [(m.id, m.content) for m in all_memories]

            # 执行语义搜索
            results = self.semantic_search.search(
                query=query,
                documents=documents,
                top_k=limit,
                min_score=min_score
            )

            if not results:
                return []

            # 获取匹配的记忆详情
            result_ids = [mem_id for mem_id, _ in results]
            id_to_score = {mem_id: score for mem_id, score in results}

            matched_memories = self.session.query(Memory).filter(
                Memory.id.in_(result_ids)
            ).all()

            # v0.6.0: 更新访问记录 (需要数据库迁移后启用)
            # for mem in matched_memories:
            #     self._update_access(mem.id)

            # 按相似度排序并返回
            memories_with_scores = [
                {
                    'content': m.content,
                    'tag': m.tag,
                    'timestamp': m.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'score': id_to_score.get(m.id, 0)
                }
                for m in matched_memories
            ]

            # 按分数降序排序
            memories_with_scores.sort(key=lambda x: x['score'], reverse=True)

            return memories_with_scores

        except Exception as e:
            print(f"⚠️ 语义搜索失败: {e}，降级到关键词搜索")
            keywords = query.split()
            return self.recall_by_keywords(keywords, tag=tag, limit=limit)

    # v0.6.0 Phase 3方法: 需要数据库迁移后启用
    # def _update_access(self, memory_id):
    #     """更新记忆访问记录"""
    #     mem = self.session.query(Memory).filter(
    #         Memory.id == memory_id
    #     ).first()
    #     if mem:
    #         mem.access_count = (mem.access_count or 0) + 1
    #         mem.last_accessed_at = datetime.now()
    #         self.session.commit()
    #
    # def calculate_importance(self, memory_id):
    #     """计算记忆的重要性分数"""
    #     ...
    #
    # def update_all_importance_scores(self):
    #     """批量更新所有记忆的重要性分数"""
    #     ...
    #
    # def get_top_memories(self, limit=20, tag=None):
    #     """获取最重要的记忆"""
    #     ...
    #
    # def auto_archive_low_importance(self, threshold=0.1, min_age_days=30):
    #     """自动归档低重要性记忆"""
    #     ...

    def calculate_importance(self, memory_id):
        """
        v0.6.0: 计算记忆的重要性分数

        考虑因素:
        1. 访问频率 (40 %)
        2. 时间衰减 (30 %)
        3. 标签类型 (30 %)

        Returns:
            float: 重要性分数(0-1)
        """
        mem = self.session.query(Memory).filter(
            Memory.id == memory_id
        ).first()

        if not mem:
            return 0.0

        # 1. 访问频率分数 (0-1)
        # 访问次数越多越重要，使用对数函数避免线性增长
        import math
        access_score = min(
            math.log(mem.access_count + 1) / math.log(100),
            1.0
        )

        # 2. 时间衰减分数 (0-1)
        # 最近的记忆更重要，使用指数衰减
        days_ago = (datetime.now() - mem.created_at).days
        time_score = math.exp(-days_ago / 30.0)  # 30天半衰期

        # 3. 标签权重 (0-1)
        tag_weights = {
            'facts': 1.0,      # 用户明确告知的事实最重要
            'task': 0.8,       # 任务记录次重要
            'general': 0.5,    # 普通对话中等重要
            'system': 0.3      # 系统日志较不重要
        }
        tag_score = tag_weights.get(mem.tag, 0.5)

        # 综合计算（加权平均）
        importance = (
            access_score * 0.4 +
            time_score * 0.3 +
            tag_score * 0.3
        )

        # 更新数据库
        mem.importance_score = importance
        self.session.commit()

        return importance

    def update_all_importance_scores(self):
        """
        v0.6.0: 批量更新所有记忆的重要性分数

        Returns:
            int: 更新的记忆数量
        """
        all_memories = self.session.query(Memory).filter(
            Memory.is_archived == False  # noqa: E712
        ).all()

        updated_count = 0
        for mem in all_memories:
            self.calculate_importance(mem.id)
            updated_count += 1

        print(f"✅ 已更新 {updated_count} 条记忆的重要性分数")
        return updated_count

    def get_top_memories(self, limit=20, tag=None):
        """
        v0.6.0: 获取最重要的记忆

        Args:
            limit: 返回数量
            tag: 可选标签过滤

        Returns:
            [{content, tag, importance_score, access_count}]
        """
        query = self.session.query(Memory).filter(
            Memory.is_archived == False  # noqa: E712
        )

        if tag:
            query = query.filter(Memory.tag == tag)

        query = query.order_by(
            Memory.importance_score.desc()
        ).limit(limit)

        memories = query.all()

        return [{
            'content': m.content,
            'tag': m.tag,
            'importance_score': m.importance_score,
            'access_count': m.access_count,
            'created_at': m.created_at.strftime('%Y-%m-%d %H:%M:%S')
        } for m in memories]

    def auto_archive_low_importance(self, threshold=0.1, min_age_days=30):
        """
        v0.6.0: 自动归档低重要性记忆

        归档策略:
        - 重要性分数 < threshold
        - 创建时间 > min_age_days 天
        - 访问次数 <= 1

        Args:
            threshold: 重要性阈值(0-1)
            min_age_days: 最小年龄（天）

        Returns:
            int: 归档数量
        """
        from datetime import timedelta

        cutoff_date = datetime.now() - timedelta(days=min_age_days)

        # 查找需要归档的记忆
        low_importance_memories = self.session.query(Memory).filter(
            Memory.is_archived == False,  # noqa: E712
            Memory.importance_score < threshold,
            Memory.created_at < cutoff_date,
            Memory.access_count <= 1
        ).all()

        archived_count = 0
        for mem in low_importance_memories:
            mem.is_archived = True
            archived_count += 1

        self.session.commit()

        if archived_count > 0:
            print(f"✅ 已归档 {archived_count} 条低重要性记忆")

        return archived_count

    def get_memory_stats(self):
        """
        v0.6.0: 获取记忆统计信息（包含重要性分析）

        Returns:
            dict: 统计信息
        """
        # 基础统计
        total = self.session.query(func.count(Memory.id)).scalar()
        archived = self.session.query(func.count(Memory.id)).filter(
            Memory.is_archived == True  # noqa: E712
        ).scalar()
        active = total - archived

        # 按标签统计
        tag_stats = self.session.query(
            Memory.tag,
            func.count(Memory.id)
        ).filter(
            Memory.is_archived == False  # noqa: E712
        ).group_by(Memory.tag).all()

        # 重要性分布
        high_importance = self.session.query(func.count(Memory.id)).filter(
            Memory.is_archived == False,  # noqa: E712
            Memory.importance_score >= 0.7
        ).scalar()

        medium_importance = self.session.query(func.count(Memory.id)).filter(
            Memory.is_archived == False,  # noqa: E712
            Memory.importance_score >= 0.3,
            Memory.importance_score < 0.7
        ).scalar()

        low_importance = self.session.query(func.count(Memory.id)).filter(
            Memory.is_archived == False,  # noqa: E712
            Memory.importance_score < 0.3
        ).scalar()

        return {
            "total": total,
            "active": active,
            "archived": archived,
            "by_tag": {tag: count for tag, count in tag_stats},
            "importance_distribution": {
                "high (≥0.7)": high_importance,
                "medium (0.3-0.7)": medium_importance,
                "low (<0.3)": low_importance
            }
        }
