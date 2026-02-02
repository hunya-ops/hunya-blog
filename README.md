# Hunya Blog (昏鸦博客)

> **"Pulp is polished storytelling, Uncut is raw reality."**
> 纸浆是打磨后的叙事，原片是未剪辑的真实。

**Hunya Blog** 是一个专为创作者打造的极简主义现代化博客系统。它的命名与内核融合了对传统印刷媒介与电影工业的致敬，重新定义了“记录”的双重属性。

## ✨ 核心特性

*   **双模内容流**：
    *   **Pulp (文章)**：深度思考的 Markdown 长文，致敬纸浆杂志的质感。
    *   **Uncut (动态)**：捕捉瞬时灵感的短文 + 多图（支持 9 张），致敬电影原片。
*   **Apple Pro 设计**：融合 Glassmorphism（毛玻璃）、弹性布局与沉浸式 UI，移动端体验极佳。
*   **开箱即用**：原生 Docker 支持，内置数据持久化、CSRF 保护与自动密钥管理。
*   **高度可配置**：所有核心设置（标题、描述、可见性）均可在后台可视化管理，优先读取数据库配置。
*   **极致性能**：集成 Flask-Caching + Redis，支持智能缓存策略 (`HIT/MISS` 监控)。
*   **API 支持**：内置 REST API，完美支持通过 iOS 快捷指令 (Shortcuts) 快速发布动态。

---

## 🚀 快速开始 (Docker 推荐)

最简单的部署方式，只需几分钟即可上线。

### 1. 克隆项目
```bash
git clone https://github.com/hunya-ops/hunya-blog.git
cd hunya-blog
```

### 2. 初始化配置
复制示例配置文件：
```bash
cp env.example .env
```

**⚠️ 关键安全设置**：
使用编辑器打开 `.env` 文件，务必修改以下默认值：
*   `ADMIN_PASSWORD`: 设置您的后台管理员密码。
*   `API_KEY`: 设置一个复杂的 API 密钥（**若不修改默认值，API 功能将自动禁用**）。

### 3. 启动服务
```bash
docker compose up -d --build
```
访问 `http://localhost:5000` 即可看到博客。

---

## 🛠️ 本地开发运行 (手动安装)

如果您是开发者，希望在本地调试代码：

1.  **准备环境**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # macOS/Linux
    # venv\Scripts\activate   # Windows
    
    pip install -r requirements.txt
    ```

2.  **配置**
    ```bash
    cp env.example .env
    # 编辑 .env 修改配置
    ```

3.  **运行**
    ```bash
    python run.py
    ```
    开发服务器将运行在 `http://127.0.0.1:5000`。

---

## ⚙️ 配置说明

项目使用 `.env` 文件管理所有基础设施配置。

详细说明请参考 [env.example](env.example) 文件，其中包含：
*   **部署与网络**：`DOCKER_BIND` (安全绑定 IP) 与 `PORT`。
*   **Docker 调优**：`GUNICORN_WORKERS` 进程数计算。
*   **博客设置**：`BLOG_TITLE` 等初始默认值。

**注意**：博客站点的标题、描述等业务配置，建议在 **后台 -> 设置** 中进行修改，数据库中的配置优先级高于环境变量。

---

## 🔌 API 与 快捷指令

Hunya Blog 提供了用于发布的 REST API，您可以通过 iOS 快捷指令或脚本实现自动化发布。

**安全须知**：所有 API 请求头必须包含 `X-API-Key`。如果 `.env` 中的 `API_KEY` 为默认值或空，API 将返回 `403 Forbidden`。

### 1. 上传图片
*   **URL**: `POST /api/upload`
*   **Headers**: `X-API-Key: <your_api_key>`
*   **Body**: `form-data` (`image`: 文件)

### 2. 发布动态 (Uncut)
*   **URL**: `POST /api/posts`
*   **Headers**: `X-API-Key: <your_api_key>`
*   **Body** (JSON):
    ```json
    {
      "content": "此刻的想法...",
      "image_urls": "http://example.com/1.jpg,http://example.com/2.jpg",
      "tags": ["生活", "灵感"]
    }
    ```

---

## 🌐 高级部署 (Nginx 反向代理)

生产环境建议使用 Nginx 作为反向代理，并配置 SSL。

### 1. Docker 安全配置
在 `.env` 中确保 Docker 只监听本地回环地址（防止端口直接暴露）：
```bash
DOCKER_BIND=127.0.0.1
```

### 2. Nginx 配置示例
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## License

MIT
