#!/bin/bash

# 快速提交工具 - 自动检测并提交
# 用法: ./scripts/quick_commit.sh "提交描述" [类型] [范围]

set -e

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# 脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

# 检查参数
if [ $# -lt 1 ]; then
    echo -e "${RED}❌ 用法: $0 \"提交描述\" [类型] [范围]${NC}"
    echo -e "${YELLOW}示例:${NC}"
    echo -e "  $0 \"修复记忆查询bug\" fix memory"
    echo -e "  $0 \"添加语音功能\" feat agent"
    echo -e "  $0 \"更新文档\""
    exit 1
fi

commit_message="$1"
commit_type="${2:-feat}"  # 默认 feat
commit_scope="$3"

# 检查是否有修改
if git diff --quiet && git diff --cached --quiet; then
    echo -e "${YELLOW}📭 没有检测到任何修改${NC}"
    exit 0
fi

# 显示修改
echo -e "${GREEN}📝 修改文件:${NC}"
git status --short

# 构建提交信息
if [ -n "$commit_scope" ]; then
    full_message="$commit_type($commit_scope): $commit_message"
else
    full_message="$commit_type: $commit_message"
fi

echo -e "\n${BLUE}提交信息: ${YELLOW}$full_message${NC}"

# 提交
git add -A
git commit -m "$full_message"

# 更新 CHANGELOG
current_date=$(date +%Y-%m-%d)

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

changelog_entry="- $icon $commit_message"

# 更新 CHANGELOG（简化版）
if grep -q "### $current_date" CHANGELOG.md; then
    # 在最后一个类型下添加
    sed -i.bak "0,/^### $current_date/,/^###/{/^- /a\\
$changelog_entry
}" CHANGELOG.md
else
    sed -i.bak "/## \[Unreleased\]/a\\
\\
### $current_date\\
$changelog_entry\\
" CHANGELOG.md
fi

rm -f CHANGELOG.md.bak

git add CHANGELOG.md
git commit --amend --no-edit

echo -e "${GREEN}✅ 提交完成!${NC}"
git log --oneline -1
