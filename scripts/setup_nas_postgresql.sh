#!/bin/bash

# 群晖NAS PostgreSQL配置脚本
# 使用方法：
# 1. SSH连接到你的群晖NAS
# 2. 执行以下命令

echo "================================================"
echo "小乐AI - 群晖PostgreSQL配置脚本"
echo "================================================"

# 设置变量（请修改为你的信息）
DB_NAME="xiaole_ai"
DB_USER="xiaole_user"
DB_PASS="你的密码"  # 修改这里！

echo ""
echo "第1步：创建数据库"
sudo -u postgres psql -c "CREATE DATABASE $DB_NAME WITH ENCODING='UTF8' LC_COLLATE='zh_CN.UTF-8' LC_CTYPE='zh_CN.UTF-8';"

echo ""
echo "第2步：创建用户"
sudo -u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASS';"

echo ""
echo "第3步：授权"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"

echo ""
echo "第4步：允许远程连接"
echo "host    $DB_NAME    $DB_USER    0.0.0.0/0    md5" | sudo tee -a /var/services/pgsql/pg_hba.conf

echo ""
echo "第5步：重启PostgreSQL"
sudo synoservicectl --restart pgsql

echo ""
echo "================================================"
echo "✅ 配置完成！"
echo "================================================"
echo ""
echo "数据库信息："
echo "  主机: $(hostname -I | awk '{print $1}')"
echo "  端口: 5432"
echo "  数据库: $DB_NAME"
echo "  用户: $DB_USER"
echo "  密码: $DB_PASS"
echo ""
echo "测试连接："
echo "  psql -h $(hostname -I | awk '{print $1}') -p 5432 -U $DB_USER -d $DB_NAME"
echo ""
