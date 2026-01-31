#!/bin/bash

# 检查 .env 是否存在
if [ ! -f .env ]; then
    echo "正在初始化配置文件..."
    cp env.example .env
    echo "✅ 配置文件 .env 已创建！"
    echo "👉 请编辑 .env 文件，修改默认密码和其他配置。"
else
    echo "⚠️ .env 文件已存在，跳过创建。"
fi

echo ""
echo "配置完成后，运行以下命令启动博客："
echo "docker compose up -d --build"
