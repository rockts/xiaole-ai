# 小乐 AI 管家开发计划

## 一、项目目标
- 打造一款专属 AI 管家“小乐”，能理解用户需求、记忆信息、执行任务、提供建议。
- 数据长期存储在本地 NAS，保障隐私。
- AI 大脑通过 Claude 4.5 Sonnet 处理核心逻辑，Gemini 2.5 Pro 处理多模态任务。
- 可持续迭代升级，随着使用不断优化性能和理解能力。

## 二、项目架构
```
             ┌────────────────────┐
             │   Claude 4.5 Sonnet│  ← 核心大脑，推理与代码生成
             └──────────┬─────────┘
                        │
                        ▼
             ┌────────────────────┐
             │ Gemini 2.5 Pro      │  ← 感知层，处理图像/音频/多模态
             └──────────┬─────────┘
                        │
                        ▼
             ┌────────────────────┐
             │ NAS 数据库          │  ← 长期记忆与数据存储
             └────────────────────┘
                        │
                        ▼
             ┌────────────────────┐
             │ Mac Studio (开发/API)│
             │ i9-4090 PC (本地模型)│
             └────────────────────┘
```

## 三、开发阶段计划

### 阶段 1：基础架构搭建（1-2天）
- 环境搭建：Mac Studio + Python + 虚拟环境
- 安装依赖：FastAPI、SQLAlchemy、psycopg2-binary、python-dotenv
- 搭建本地 SQLite 数据库（测试阶段）
- 搭建 FastAPI 主服务 (`main.py`)
- 搭建 memory.py、agent.py 模块
- 测试接口：`/think`、`/act`、`/memory`

### 阶段 2：NAS 数据接入（1天）
- 配置 NAS PostgreSQL 数据库
- 修改 memory.py/db_setup.py 指向 NAS
- 数据迁移：将 SQLite 数据导入 NAS
- 确认接口可正常读取/写入 NAS 数据

### 阶段 3：AI Agent 功能集成（2-3天）
- agent.py 接入 Claude 4.5 Sonnet API
- think() 调用 Sonnet 生成响应
- act() 执行命令并记录记忆
- 可扩展 Gemini 2.5 Pro 多模态模块（图像/音频任务）
- 编写自动测试脚本 test_api.py

### 阶段 4：开发迭代与优化（持续）
- 反馈机制：运行测试脚本，收集接口输出
- 我（GPT-5）分析输出，优化代码、任务执行逻辑
- 数据库结构优化，支持长记忆与上下文检索
- 功能迭代：增加自动学习、任务总结、建议生成等

### 阶段 5：未来扩展
- 语音交互模块（Speech-to-Text / Text-to-Speech）
- 智能家居/PC控制模块
- 复杂决策与规划模块
- 混合云本地 AI 架构优化（本地轻量 + 云端高智商）

## 四、开发工具与资源
- **开发环境**：VS Code / Mac Studio / Python 3.11+ / 虚拟环境
- **依赖库**：FastAPI, SQLAlchemy, psycopg2-binary, python-dotenv, requests
- **AI 模型**：Claude 4.5 Sonnet（主脑）、Gemini 2.5 Pro（多模态感知）
- **数据库**：NAS PostgreSQL / SQLite（测试）
- **测试工具**：test_api.py, test_simple.sh, Postman 或 curl

## 五、迭代协作流程
1. 本地开发或 Claude/Gemini 写好功能模块。
2. 运行本地接口测试脚本 test_api.py。
3. 把测试输出 JSON 或关键代码发给 GPT-5 我。
4. 我分析输出，生成下一步代码或优化建议。
5. 本地执行，循环迭代，逐步完善小乐。

---
*备注：此文档作为小乐 AI 管家开发全程参考，可持续更新迭代。*