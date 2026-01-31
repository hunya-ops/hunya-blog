#!/bin/bash

# 检查 env 文件是否存在
if [ ! -f env ]; then
    echo "正在初始化配置文件..."
    cat << EOF > env.example
# 部署配置
DOCKER_BIND=0.0.0.0
PORT=5000
FLASK_ENV=production

# 管理员密码
ADMIN_PASSWORD=admin

# 博客配置
BLOG_TITLE=昏鸦博客
BLOG_DESCRIPTION=一个充满梦想的博客
EOF
    cp env.example env
    echo "✅ 配置文件 env 已创建！"
    echo "👉 请编辑 env 文件，修改默认密码和其他配置。"
else
    echo "💡 配置文件 env 已存在，跳过初始化。"
fi

echo ""
echo "配置完成后，运行以下命令启动博客："
echo "docker compose up -d --build"
