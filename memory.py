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

    def remember(self, content, tag="general"):
        mem = Memory(content=content, tag=tag)
        self.session.add(mem)
        self.session.commit()

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
