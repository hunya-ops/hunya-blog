# Hunya Blog (昏鸦博客)

一个轻量、现代化的 Flask 博客系统，支持长文章和微博（短内容）两种形式。支持 Docker 一键部署，专为“昏鸦”打造。

## 功能特性

- **长文章**：支持标题 + Markdown 编辑器
- **微博**：支持文字 + 多图（最多9张）
- **标签系统**：文章和微博都可添加标签
- **图片管理**：支持粘贴上传、拖拽上传
- **安全**：内置 CSRF 保护，支持安全 Cookie，**自动管理密钥**
- **部署**：原生支持 Docker 和 Docker Compose，**数据自动持久化**
- **RSS 订阅**
- **响应式设计**：纯 CSS 实现，无重型前端框架依赖

## 快速开始

### 方式一：使用 Docker (推荐)

最简单的部署方式。

1. **克隆项目**
   ```bash
   git clone https://github.com/hunya-ops/hunya-blog.git
   cd yipai-blog
   ```

2. **初始化配置**
   运行设置脚本，它会为您自动创建配置文件：
   ```bash
   ./setup.sh
   # 或者手动复制：cp env.example .env
   ```
   **必填配置项** (编辑生成的 `.env` 文件):
   - `ADMIN_PASSWORD`: 管理员后台登录密码
   - `BLOG_TITLE`: 博客标题
   - `BLOG_DESCRIPTION`: 博客描述

   *注：`SECRET_KEY` 和数据库文件会自动保存在 `data/` 目录下，该目录已挂载到 Docker 容器，确保数据持久化。*

3. **启动服务**
   ```bash
   docker compose up -d --build
   ```
   *注：如果是旧版 Docker Desktop，可能需要使用 `docker-compose` 命令。*

   访问 `http://localhost:5000` 即可看到博客。

### 方式二：本地开发运行

1. **创建虚拟环境**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # macOS/Linux
   # venv\Scripts\activate   # Windows
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **配置环境变量**
   ```bash
   cp .env.example .env
   # 编辑 .env 文件
   ```

4. **运行**
   ```bash
   python run.py
   ```

## 配置说明

所有的配置都通过环境变量 (`.env`) 管理，不需要修改代码。

| 变量名 | 说明 | 默认值 |
| :--- | :--- | :--- |
| `ADMIN_PASSWORD` | 管理后台登录密码 | `admin` |
| `BLOG_TITLE` | 博客网站标题 | `昏鸦博客` |
| `BLOG_DESCRIPTION` | 博客网站描述 | `一个充满梦想的博客` |
| `PORT` | 容器映射端口 | `5000` |
| `FLASK_ENV` | 运行环境 (`production`/`development`) | `production` |
| `SECRET_KEY` | Session 加密密钥 | (推荐不配置，系统会自动生成并持久化) |
| `DATABASE_URL` | 数据库连接地址 | `sqlite:///data/blog.db` |

## Nginx & HTTPS 配置 (可选)

建议在生产环境使用 Nginx 反向代理并配置 SSL 证书。本项目已内置 `ProxyFix` 中间件，完美支持反向代理。

### 1. Nginx 配置示例

请确保 Nginx 配置文件包含以下 `proxy_set_header` 指令，以便 Flask 正确识别客户端 IP 和 HTTPS 协议（由于 RSS 需生成绝对链接，这点尤为重要）：

```nginx
server {
    listen 80;
    server_name your-domain.com;  # 替换为你的域名

    location / {
        proxy_pass http://127.0.0.1:5000;  # 对应 docker 映射的端口
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;  # 关键！
    }
}
```

### 2. 使用 Certbot 开启 HTTPS

推荐使用 Certbot 自动申请免费证书：

```bash
# Ubuntu/Debian 安装
sudo apt update
sudo apt install certbot python3-certbot-nginx

# 一键申请并自动修改 Nginx 配置
sudo certbot --nginx -d your-domain.com
```

## 目录结构

```
yipai-blog/
├── app/                  # 应用源码
│   ├── routes/           # 视图路由
│   ├── models.py         # 数据库模型
│   ├── templates/        # HTML 模板
│   └── static/           # 静态资源 (CSS/JS/Uploads)
├── data/                 # 数据存储 (DB, Keys) - 自动创建
├── config.py             # 配置加载逻辑
├── Dockerfile            # Docker 构建文件
├── docker-compose.yml    # Docker Compose编排
├── requirements.txt      # Python依赖
└── run.py               # 启动入口
```

## License

MIT
