#!/bin/bash

# 群晖Docker运行PostgreSQL脚本
# 使用方法：SSH连接NAS后执行此脚本

echo "================================================"
echo "小乐AI - 群晖Docker PostgreSQL安装"
echo "================================================"

# 配置变量
POSTGRES_PASSWORD="Xiaole2025Admin"  # PostgreSQL管理员密码
DB_NAME="xiaole_ai"
DB_USER="xiaole_user"
DB_PASS="Xiaole2025User"  # 小乐数据库用户密码

echo ""
echo "第1步：创建数据存储目录"
sudo mkdir -p /volume1/docker/postgresql/data
sudo chmod 777 /volume1/docker/postgresql/data

echo ""
echo "第2步：启动PostgreSQL容器"
sudo docker run -d \
  --name xiaole-postgresql \
  --restart always \
  -e POSTGRES_PASSWORD=$POSTGRES_PASSWORD \
  -e POSTGRES_DB=$DB_NAME \
  -e POSTGRES_USER=$DB_USER \
  -e POSTGRES_INITDB_ARGS="--encoding=UTF8" \
  -p 5432:5432 \
  -v /volume1/docker/postgresql/data:/var/lib/postgresql/data \
  postgres:13-alpine

echo ""
echo "第3步：等待PostgreSQL启动..."
sleep 10

echo ""
echo "第4步：创建用户和授权"
sudo docker exec xiaole-postgresql psql -U postgres -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASS';"
sudo docker exec xiaole-postgresql psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"
sudo docker exec xiaole-postgresql psql -U postgres -d $DB_NAME -c "GRANT ALL ON SCHEMA public TO $DB_USER;"

echo ""
echo "第5步：测试连接"
sudo docker exec xiaole-postgresql psql -U $DB_USER -d $DB_NAME -c "SELECT version();"

echo ""
echo "================================================"
echo "✅ PostgreSQL安装完成！"
echo "================================================"
echo ""
echo "容器名称: xiaole-postgresql"
echo "数据库信息："
echo "  主机: $(hostname -I | awk '{print $1}')"
echo "  端口: 5432"
echo "  数据库: $DB_NAME"
echo "  用户: $DB_USER"
echo "  密码: $DB_PASS"
echo ""
echo "管理命令："
echo "  查看状态: sudo docker ps | grep xiaole-postgresql"
echo "  查看日志: sudo docker logs xiaole-postgresql"
echo "  重启容器: sudo docker restart xiaole-postgresql"
echo "  进入容器: sudo docker exec -it xiaole-postgresql psql -U $DB_USER -d $DB_NAME"
echo ""
