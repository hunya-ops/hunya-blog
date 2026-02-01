# Hunya Blog (昏鸦博客)

> **"Pulp is polished storytelling, Uncut is raw reality."**
> 纸浆是打磨后的叙事，原片是未剪辑的真实。

**Hunya Blog** 是一个专为创作者打造的极简主义现代化博客系统。它的命名与内核融合了对传统印刷媒介与电影工业的致敬，重新定义了“记录”的双重属性：

## 核心理念

我们认为，数字生活不应只有一种表达。Hunya Blog 独创了双轨道内容流：

*   **Pulp (文章)**：致敬《低俗小说》与纸浆杂志。它是经过深度思考、文字沉淀与精心剪辑后的“成品”输出。通过完整的 Markdown 体验，将碎片化的信息聚合成有逻辑、有质感的叙事。
*   **Uncut (动态)**：致敬电影工业中的“未剪辑版”。它捕捉的是那些未经过渡打磨、最接近生活原貌的瞬时状态与灵感碎片。支持文字 + 9张原图，保留最真实、粗粝的情绪纹理。

## 功能特性

*   **双模内容**：**Pulp**（长文 + Markdown）与 **Uncut**（短文 + 多图）并存，通过精简的 `/pulp` 与 `/uncut` 路径访问。
*   **高度可配置**：内置系统设置面板，无需修改代码即可定义**自定义首页 Markdown 内容**、归档/标签云开关等。
*   **现代设计**：采用 **Apple Pro Inspired** 设计语言，融合 **Glassmorphism**（毛玻璃）与弹性卡片布局，视觉体验轻盈通透。
*   **交互体验**：移动端深度优化（融合导航、动态屏高），支持 **Lightbox** 全屏图片预览、文章列表全区域点击。
*   **可视化系统**：动态标签云（Treemap）、年度发文统计图表，直观呈现创作历程。
*   **图片处理**：支持粘贴/拖拽上传，**支持 HEIC 格式秒转 JPEG**，内置防缓存图片处理与清理功能。
*   **极简部署**：原生 Docker 支持，数据自动持久化，内置 CSRF 保护与密钥自动管理。
*   **RSS 订阅**：内置符合标准的 RSS 源支持。

## 快速开始

### 方式一：使用 Docker (推荐)

最简单的部署方式，只需几分钟即可上线。

1. **克隆项目**
   ```bash
   git clone https://github.com/hunya-ops/hunya-blog.git
   cd hunya-blog
   ```

2. **初始化配置**
   运行设置脚本，自动创建配置文件：
   ```bash
   ./setup.sh
   # 或者手动复制：cp env.example env
   ```
   **必填配置项** (编辑生成的 `env` 文件):
   - `ADMIN_PASSWORD`: 管理员后台登录密码
   - `BLOG_TITLE`: 博客标题

   *注：数据库文件会自动保存在 `data/` 目录下，该目录已挂载到 Docker 容器，确保数据持久化。*

3. **启动服务**
   ```bash
   docker compose up -d --build
   ```
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
   cp env.example env
   # 编辑 env 文件
   ```

4. **运行**
   ```bash
   python run.py
   ```

## 配置说明

所有的配置都通过环境变量 (`env`) 管理，不需要修改代码。

| 变量名 | 说明 | 默认值 |
| :--- | :--- | :--- |
| `ADMIN_PASSWORD` | 管理后台登录密码 | `admin` |
| `BLOG_TITLE` | 博客网站标题 | `昏鸦博客` |
| `BLOG_DESCRIPTION` | 博客网站描述 | `一个充满梦想的博客` |
| `SECRET_KEY` | Session 加密密钥 | (推荐不配置，系统会自动生成并持久化在 `data/.secret_key`) |
| `API_KEY` | API 访问密钥 (用于 iOS 快捷指令发布动态等) | `dev-token-123` |
| `DOCKER_BIND` | Docker 监听地址 | `0.0.0.0` |
| `PORT` | 容器映射端口 | `5000` |
| `FLASK_ENV` | 运行环境 | `production` |

## API 文档

Hunya Blog 提供了简单的 REST API，配合 **快捷指令 (Shortcuts)** 或自动化脚本，可快速发布动态。

所有 API 请求头需包含：`X-API-Key: <你的 API_KEY>`

### 1. 上传图片

*   **URL**: `POST /api/upload`
*   **Body**: `form-data`
    *   `image`: 图片文件
*   **Response**: `{"success": true, "url": "/static/uploads/..."}`

### 2. 发布动态 (Uncut)

*   **URL**: `POST /api/posts`
*   **Body**: `application/json`
    ```json
    {
      "content": "此刻的想法...",
      "image_urls": "http://img1.jpg,http://img2.jpg", 
      "tags": ["生活", "随笔"]
    }
    ```
    *注：`image_urls` 可留空，多张图片用逗号分隔（图片需先上传获取 URL）。*

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

### 2. 安全建议

为了安全，您可以让 Docker 只监听本地回环地址（`127.0.0.1`），防止通过 IP 直接访问：

在 `env` 文件中添加：
```properties
DOCKER_BIND=127.0.0.1
```

## 目录结构

```
hunya-blog/
├── app/                  # 应用源码
│   ├── routes/           # 视图路由
│   ├── models.py         # 数据库模型
│   ├── templates/        # HTML 模板
│   └── static/           # 静态资源 (CSS/JS/Uploads)
├── data/                 # 数据存储 (DB, Keys) - 自动创建，需备份
├── config.py             # 配置加载逻辑
├── Dockerfile            # Docker 构建文件
├── docker-compose.yml    # Docker Compose编排
├── requirements.txt      # Python依赖
└── run.py                # 启动入口
```

## License

MIT
