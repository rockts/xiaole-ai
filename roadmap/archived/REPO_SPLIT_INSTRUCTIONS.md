# 《Xiaole 项目仓库拆分与文档系统重构说明（Agent 执行版）》

版本：v1.0
用途：供 VSCode Agent / 本地开发 Agent 理解与执行
目标：自动完成仓库拆分、目录初始化、文档库创建、部署配置等任务。

---

# 🎯 总目标

将现有 `rockts/xiaole-ai` 仓库拆分成三个仓库：

1. `xiaole-web` —— 前端 UI 工程
2. `xiaole-backend` —— 小乐后端 + Agent 逻辑
3. `xiaole-docs` —— 所有文档集中存储库

拆分完成后：

* 前端部署到 Cloudflare Pages
* 后端部署到 NAS，通过 Cloudflare Tunnel 暴露
* 文档可部署为静态站点

---

# 🧩 一、仓库拆分要求

## 1. 前端（xiaole-web）

需要从旧仓库提取的内容：

* `/static/`
* `/templates/`
* HTML / CSS / JS
* 任何 UI 与资源文件

目标目录结构：

```
xiaole-web/
│── public/
│── src/
│── pages/
│── components/
│── styles/
│── package.json
│── README.md
```

部署：Cloudflare Pages

---

## 2. 后端（xiaole-backend）

需要从旧仓库提取的内容：

* `main.py`
* `agent/`
* `conversation.py`
* `memory.py`
* `/tools/`
* `/deploy/`
* `/scheduler/`
* 数据库相关文件
* 所有 Python 后端逻辑

目标目录结构：

```
xiaole-backend/
│── api/
│── agent/
│   ├── persona/
│   ├── prompts/
│   ├── tools/
│   ├── pipelines/
│── memory/
│── tasks/
│── scheduler/
│── db/
│── utils/
│── deploy/
│── main.py
│── requirements.txt
│── README.md
```

部署：NAS 后端 + Cloudflare Tunnel

---

## 3. 文档库（xiaole-docs）

集中存储所有文档：

* 小乐世界观
* Persona
* 记忆规范
* 任务系统设计
* 主动提醒系统
* API 文档
* 前端规范
* 部署文档
* 开发规范
* 架构说明
* 路线图

目录结构：

```
xiaole-docs/
│── architecture/
│── backend/
│── frontend/
│── product/
│── dev/
│── README.md
```

可选：Cloudflare Pages 部署成文档站

---

# 🧭 二、Agent 需要执行的步骤（强执行性）

## Step 1：克隆旧仓库

```
git clone https://github.com/rockts/xiaole-ai
cd xiaole-ai
```

## Step 2：创建三个新仓库（需用户在 GitHub 建好）

* xiaole-web
* xiaole-backend
* xiaole-docs

然后继续下一步。

## Step 3：初始化前端目录

```
mkdir ../xiaole-web
# 移动 static/ templates/ index.html CSS/ JS/ 等所有前端内容
```

## Step 4：初始化后端目录

```
mkdir ../xiaole-backend
# 移动 main.py agent/ tools/ memory/ scheduler/ api/ 等所有后端内容
```

## Step 5：初始化 docs 目录

```
mkdir ../xiaole-docs
mkdir ../xiaole-docs/architecture
mkdir ../xiaole-docs/backend
mkdir ../xiaole-docs/frontend
mkdir ../xiaole-docs/product
mkdir ../xiaole-docs/dev
```

## Step 6：三个仓库分别初始化 Git 并 push

示例（前端）：

```
cd ../xiaole-web
git init
git add .
git commit -m "init xiaole-frontend"
git remote add origin git@github.com:rockts/xiaole-frontend.git
git push -u origin main
```

后端与 docs 相同。

## Step 7：更新旧仓库 README

说明项目已拆分、新仓库地址、迁移方式。

## Step 8：（可选）为 Cloudflare Pages 创建构建配置

---

# 🧨 三、Agent 执行限制（请严格遵守）

1. 不得删除任何用户文件
2. 移动操作需提示用户确认
3. 不得修改业务逻辑文件（如 main.py）
4. 文档内容仅复制不改动
5. 所有新建目录必须先提示用户

---

# 📦 四、Agent 任务完成后需生成的输出

* 拆分完成报告
* 三个仓库的目录树
* Git push 历史
* 后端启动成功截图或日志
* 前端 Cloudflare Pages 构建成功记录
* 文档站（如部署）的访问地址

---

# ✔ 结束语

此文件为 Agent 执行 Xiaole 项目拆分与文档重构的完整、结构化、可操作说明书。
