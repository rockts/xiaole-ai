#!/bin/bash

# 小乐 AI 环境检查脚本
# 用法: ./check_env.sh

echo "🔍 检查小乐 AI 运行环境"
echo "========================================"
echo ""

# 检查脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查函数
check_pass() {
    echo -e "${GREEN}✅ $1${NC}"
}

check_fail() {
    echo -e "${RED}❌ $1${NC}"
}

check_warn() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# 1. 检查 nvm
echo "1️⃣  检查 nvm..."
if command -v nvm &> /dev/null; then
    check_pass "nvm 已安装"
elif [ -s "$HOME/.nvm/nvm.sh" ]; then
    source "$HOME/.nvm/nvm.sh"
    check_pass "nvm 已安装 (通过 .nvm/nvm.sh 加载)"
else
    check_fail "nvm 未安装"
    echo "   💡 安装方法: curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash"
fi
echo ""

# 2. 检查 Node 版本
echo "2️⃣  检查 Node.js 版本..."
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    REQUIRED_VERSION="20.19.5"
    NVMRC_VERSION=$(cat .nvmrc 2>/dev/null || echo "未找到")
    
    echo "   当前版本: $NODE_VERSION"
    echo "   要求版本: v$REQUIRED_VERSION"
    echo "   .nvmrc: $NVMRC_VERSION"
    
    if [[ "$NODE_VERSION" == "v$REQUIRED_VERSION" ]]; then
        check_pass "Node 版本正确"
    elif [[ "${NODE_VERSION:1:2}" -ge "18" ]]; then
        check_warn "Node 版本可用,但建议使用 $REQUIRED_VERSION"
    else
        check_fail "Node 版本过低,需要 >= 18.0.0"
        echo "   💡 切换版本: nvm use $REQUIRED_VERSION"
    fi
else
    check_fail "Node.js 未安装"
fi
echo ""

# 3. 检查 npm 版本
echo "3️⃣  检查 npm 版本..."
if command -v npm &> /dev/null; then
    NPM_VERSION=$(npm --version)
    echo "   当前版本: $NPM_VERSION"
    
    if [[ "${NPM_VERSION%%.*}" -ge "9" ]]; then
        check_pass "npm 版本符合要求 (>= 9.0.0)"
    else
        check_warn "npm 版本较低,建议升级到 >= 9.0.0"
        echo "   💡 升级 npm: npm install -g npm@latest"
    fi
else
    check_fail "npm 未安装"
fi
echo ""

# 4. 检查 Python 版本
echo "4️⃣  检查 Python 版本..."
if [ -f ".venv/bin/python" ]; then
    PYTHON_VERSION=$(.venv/bin/python --version)
    check_pass "虚拟环境 Python: $PYTHON_VERSION"
elif command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    check_warn "系统 Python: $PYTHON_VERSION (建议使用虚拟环境)"
else
    check_fail "Python 未安装"
fi
echo ""

# 5. 检查前端依赖
echo "5️⃣  检查前端依赖..."
if [ -d "frontend/node_modules" ]; then
    check_pass "前端依赖已安装"
else
    check_warn "前端依赖未安装"
    echo "   💡 安装依赖: cd frontend && npm install"
fi
echo ""

# 6. 检查配置文件
echo "6️⃣  检查配置文件..."
[ -f ".nvmrc" ] && check_pass ".nvmrc 存在" || check_warn ".nvmrc 不存在"
[ -f "frontend/.nvmrc" ] && check_pass "frontend/.nvmrc 存在" || check_warn "frontend/.nvmrc 不存在"
[ -f ".env" ] && check_pass ".env 存在" || check_warn ".env 不存在"
[ -f "backend/.env" ] && check_pass "backend/.env 存在" || check_warn "backend/.env 不存在"
echo ""

# 7. 检查端口占用
echo "7️⃣  检查端口占用..."
if lsof -i :8000 -sTCP:LISTEN &> /dev/null; then
    check_pass "后端端口 8000 已被占用 (服务可能在运行)"
else
    echo "   ℹ️  后端端口 8000 空闲"
fi

if lsof -i :3000 -sTCP:LISTEN &> /dev/null; then
    check_pass "前端端口 3000 已被占用 (服务可能在运行)"
else
    echo "   ℹ️  前端端口 3000 空闲"
fi
echo ""

# 总结
echo "========================================"
echo "📋 检查完成!"
echo ""
echo "📖 详细说明: 查看 README_NODE_VERSION.md"
echo "🚀 启动服务: ./start.sh"
echo "🛑 停止服务: ./stop.sh"
echo ""
