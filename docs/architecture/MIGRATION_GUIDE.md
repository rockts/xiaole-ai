# v0.6.0 Phase 3 数据库迁移说明

## 问题描述

Phase 3 添加了记忆重要性评分功能,需要在 `memories` 表中添加4个新字段:
- `importance_score` (REAL): 重要性评分 0.0-1.0
- `access_count` (INTEGER): 访问次数
- `last_accessed_at` (TIMESTAMP): 最后访问时间  
- `is_archived` (BOOLEAN): 是否归档

当前问题: 应用用户 `xiaole_user` 没有 ALTER TABLE 权限,无法自动执行迁移。

## 解决方案

### 方案1: 使用pgAdmin图形界面 (推荐)

1. 在NAS上打开pgAdmin (通常在 http://192.168.88.188:5050)
2. 连接到 `xiaole_ai` 数据库
3. 找到 `memories` 表,右键 → Properties → Columns → Add
4. 添加以下4个字段:

```
字段名: importance_score
类型: real
默认值: 0.0
允许NULL: 是

字段名: access_count  
类型: integer
默认值: 0
允许NULL: 是

字段名: last_accessed_at
类型: timestamp without time zone
默认值: CURRENT_TIMESTAMP
允许NULL: 是

字段名: is_archived
类型: boolean
默认值: false
允许NULL: 是
```

5. 点击Save保存

6. 创建索引以优化查询:
```sql
CREATE INDEX idx_memories_importance_score ON memories(importance_score DESC);
CREATE INDEX idx_memories_is_archived ON memories(is_archived);
```

### 方案2: 使用postgres超级用户执行SQL

如果你有NAS的SSH访问权限和postgres密码:

```bash
# SSH连接到NAS
ssh admin@192.168.88.188

# 以postgres用户登录
sudo -u postgres psql xiaole_ai

# 执行以下SQL:
\i /path/to/db_migrations/003_add_memory_importance_fields.sql

# 或手动执行:
ALTER TABLE memories ADD COLUMN importance_score REAL DEFAULT 0.0;
ALTER TABLE memories ADD COLUMN access_count INTEGER DEFAULT 0;
ALTER TABLE memories ADD COLUMN last_accessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE memories ADD COLUMN is_archived BOOLEAN DEFAULT FALSE;

CREATE INDEX idx_memories_importance_score ON memories(importance_score DESC);
CREATE INDEX idx_memories_is_archived ON memories(is_archived);

-- 为现有数据设置初始值
UPDATE memories SET importance_score = 0.5;
UPDATE memories SET last_accessed_at = created_at;

# 退出
\q
```

### 方案3: 授予xiaole_user ALTER权限

连接到PostgreSQL后:

```sql
-- 以postgres超级用户身份执行:
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO xiaole_user;
ALTER TABLE memories OWNER TO xiaole_user;
ALTER TABLE conversations OWNER TO xiaole_user;
ALTER TABLE proactive_qa OWNER TO xiaole_user;
ALTER TABLE behavior_analytics OWNER TO xiaole_user;
ALTER TABLE pattern_learning OWNER TO xiaole_user;
```

然后重新运行:
```bash
python scripts/run_migration.py
```

## 验证迁移

迁移完成后,运行验证脚本:

```bash
python scripts/check_db_permissions.py
```

应该看到4个新字段已添加:
```
✓ importance_score: real
✓ access_count: integer  
✓ last_accessed_at: timestamp without time zone
✓ is_archived: boolean
```

## 迁移后操作

1. 启用代码中的Phase 3功能:
   - 取消 `db_setup.py` 中 Memory 模型的字段注释
   - 取消 `memory.py` 中相关方法的注释

2. 重启服务器:
```bash
python main.py
```

3. 测试Phase 3功能:
```bash
python tests/test_phase3_features.py
```

## 为什么会出现权限问题?

数据库表的所有者是 `postgres` 超级用户,但应用使用 `xiaole_user` 连接。PostgreSQL默认只允许表所有者执行ALTER TABLE等DDL操作。

解决这个问题的最佳实践是:
- 开发环境: 使用SQLite或授予应用用户完整权限  
- 生产环境: 由DBA手动执行迁移,或使用专门的迁移工具(如Alembic)

## 相关文件

- 迁移脚本: `db_migrations/003_add_memory_importance_fields.sql`
- 权限检查: `scripts/check_db_permissions.py`
- 执行脚本: `scripts/run_migration.py`
- 测试脚本: `tests/test_phase3_features.py`
