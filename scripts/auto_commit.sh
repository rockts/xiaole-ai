#!/bin/bash

# 自动 Git 提交工具
# 功能：自动检测修改、生成提交信息、更新 CHANGELOG

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

# 检查是否在 develop 分支
current_branch=$(git branch --show-current)
if [ "$current_branch" != "develop" ]; then
    echo -e "${YELLOW}⚠️  警告: 当前不在 develop 分支 (当前: $current_branch)${NC}"
    read -p "是否继续? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# 检查是否有修改
if git diff --quiet && git diff --cached --quiet; then
    echo -e "${YELLOW}📭 没有检测到任何修改${NC}"
    exit 0
fi

echo -e "${BLUE}═══════════════════════════════════════${NC}"
echo -e "${BLUE}  自动 Git 提交工具${NC}"
echo -e "${BLUE}═══════════════════════════════════════${NC}"

# 显示修改文件
echo -e "\n${GREEN}📝 检测到以下修改:${NC}"
git status --short

# 分析修改类型
modified_files=$(git status --short)
commit_type=""
commit_scope=""
files_changed=()

# 解析修改文件
while IFS= read -r line; do
    if [ -z "$line" ]; then continue; fi
    
    status="${line:0:2}"
    file="${line:3}"
    files_changed+=("$file")
    
    # 根据文件类型判断提交类型
    if [[ "$file" == *.md ]]; then
        commit_type="docs"
    elif [[ "$file" == test_*.py ]] || [[ "$file" == tests/* ]]; then
        commit_type="test"
    elif [[ "$file" == *.py ]]; then
        if [ -z "$commit_type" ] || [ "$commit_type" == "docs" ]; then
            commit_type="feat"
        fi
    elif [[ "$file" == *.html ]] || [[ "$file" == *.css ]] || [[ "$file" == *.js ]]; then
        commit_type="style"
    elif [[ "$file" == *.sh ]]; then
        commit_type="chore"
    elif [[ "$file" == .env* ]] || [[ "$file" == *.json ]] || [[ "$file" == *.yaml ]]; then
        commit_type="config"
    fi
done <<< "$modified_files"

# 智能推断提交范围
if echo "${files_changed[@]}" | grep -q "agent.py"; then
    commit_scope="agent"
elif echo "${files_changed[@]}" | grep -q "memory.py"; then
    commit_scope="memory"
elif echo "${files_changed[@]}" | grep -q "conversation.py"; then
    commit_scope="conversation"
elif echo "${files_changed[@]}" | grep -q "main.py"; then
    commit_scope="api"
elif echo "${files_changed[@]}" | grep -q "index.html"; then
    commit_scope="ui"
fi

# 默认提交类型
if [ -z "$commit_type" ]; then
    commit_type="chore"
fi

echo -e "\n${BLUE}═══════════════════════════════════════${NC}"
echo -e "${GREEN}📋 提交类型建议:${NC}"
echo -e "  ${YELLOW}推荐类型: $commit_type${NC}"
[ -n "$commit_scope" ] && echo -e "  ${YELLOW}推荐范围: $commit_scope${NC}"

# 提交类型选项
echo -e "\n${GREEN}请选择提交类型:${NC}"
echo "  1) feat     - ✨ 新功能"
echo "  2) fix      - 🐛 Bug修复"
echo "  3) docs     - 📝 文档更新"
echo "  4) style    - 🎨 代码格式/样式"
echo "  5) refactor - ♻️  代码重构"
echo "  6) perf     - ⚡ 性能优化"
echo "  7) test     - 🧪 测试相关"
echo "  8) chore    - 🔧 构建/工具"
echo "  9) config   - ⚙️  配置修改"

read -p "输入选项 (1-9, 回车使用推荐): " type_choice

case $type_choice in
    1) commit_type="feat" ;;
    2) commit_type="fix" ;;
    3) commit_type="docs" ;;
    4) commit_type="style" ;;
    5) commit_type="refactor" ;;
    6) commit_type="perf" ;;
    7) commit_type="test" ;;
    8) commit_type="chore" ;;
    9) commit_type="config" ;;
    "") ;; # 使用推荐
    *) echo -e "${RED}❌ 无效选项${NC}"; exit 1 ;;
esac

# 输入提交范围（可选）
if [ -z "$commit_scope" ]; then
    read -p "输入提交范围 (可选，如 agent/memory/api): " commit_scope
fi

# 输入提交描述
echo -e "\n${GREEN}📝 输入提交描述:${NC}"
read -p "> " commit_message

if [ -z "$commit_message" ]; then
    echo -e "${RED}❌ 提交描述不能为空${NC}"
    exit 1
fi

# 构建完整的提交信息
if [ -n "$commit_scope" ]; then
    full_commit_message="$commit_type($commit_scope): $commit_message"
else
    full_commit_message="$commit_type: $commit_message"
fi

# 可选：添加详细描述
echo -e "\n${YELLOW}是否添加详细描述? (回车跳过)${NC}"
read -p "> " detailed_description

if [ -n "$detailed_description" ]; then
    full_commit_message="$full_commit_message

$detailed_description"
fi

# 显示最终提交信息
echo -e "\n${BLUE}═══════════════════════════════════════${NC}"
echo -e "${GREEN}📦 最终提交信息:${NC}"
echo -e "${YELLOW}$full_commit_message${NC}"

# 确认提交
echo -e "\n${BLUE}═══════════════════════════════════════${NC}"
read -p "确认提交? (Y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Nn]$ ]]; then
    echo -e "${YELLOW}❌ 已取消提交${NC}"
    exit 0
fi

# 执行 git add
echo -e "\n${GREEN}📥 添加修改到暂存区...${NC}"
git add -A

# 执行提交
echo -e "${GREEN}💾 提交修改...${NC}"
git commit -m "$full_commit_message"

# 更新 CHANGELOG
echo -e "\n${GREEN}📋 更新 CHANGELOG...${NC}"

# 获取当前日期
current_date=$(date +%Y-%m-%d)

# 根据提交类型选择图标
case $commit_type in
    feat) icon="✨" ;;
    fix) icon="🐛" ;;
    docs) icon="📝" ;;
    style) icon="🎨" ;;
    refactor) icon="♻️" ;;
    perf) icon="⚡" ;;
    test) icon="🧪" ;;
    chore) icon="🔧" ;;
    config) icon="⚙️" ;;
    *) icon="📌" ;;
esac

# 准备 CHANGELOG 条目
changelog_entry="- $icon $commit_message"

# 检查今天的日期是否已存在
if grep -q "### $current_date" CHANGELOG.md; then
    # 在今天的日期下添加条目
    sed -i.bak "/### $current_date/a\\
#### $commit_type\\
$changelog_entry\\
" CHANGELOG.md
else
    # 创建新的日期条目
    sed -i.bak "/## \[Unreleased\]/a\\
\\
### $current_date\\
\\
#### $commit_type\\
$changelog_entry\\
" CHANGELOG.md
fi

# 清理备份文件
rm -f CHANGELOG.md.bak

# 提交 CHANGELOG 更新
git add CHANGELOG.md
git commit --amend --no-edit

echo -e "\n${GREEN}✅ 提交完成!${NC}"
echo -e "${BLUE}═══════════════════════════════════════${NC}"

# 显示最近的提交
echo -e "\n${GREEN}📜 最近的提交:${NC}"
git log --oneline -5

# 询问是否推送
echo -e "\n${BLUE}═══════════════════════════════════════${NC}"
read -p "是否推送到远程? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${GREEN}🚀 推送到远程...${NC}"
    git push origin "$current_branch"
    echo -e "${GREEN}✅ 推送完成!${NC}"
else
    echo -e "${YELLOW}ℹ️  可以稍后使用 'git push' 推送${NC}"
fi

echo -e "\n${GREEN}🎉 完成!${NC}"
