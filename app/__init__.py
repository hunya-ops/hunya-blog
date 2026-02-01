import os
import markdown
from flask import Flask
from markupsafe import Markup
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from config import Config
from werkzeug.middleware.proxy_fix import ProxyFix
from pillow_heif import register_heif_opener

register_heif_opener()

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'admin.login'
csrf = CSRFProtect()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Use ProxyFix to handle X-Forwarded-* headers from Nginx
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Markdown 过滤器
    @app.template_filter('markdown')
    def markdown_filter(text):
        if not text:
            return ''
        return Markup(markdown.markdown(text, extensions=['fenced_code', 'tables']))

    # 确保上传目录存在
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # 注册蓝图
    from app.routes.main import main_bp
    from app.routes.admin import admin_bp
    from app.routes.api import api_bp
    from app.routes.feed import feed_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(feed_bp)

    # 豁免 API 蓝图的 CSRF 保护
    csrf.exempt(api_bp)

    # 注入模板全局变量
    @app.context_processor
    def inject_globals():
        from app.models import Setting
        return {
            'blog_title': Setting.get('blog_title', app.config['BLOG_TITLE']),
            'blog_description': Setting.get('blog_description', app.config['BLOG_DESCRIPTION'])
        }

    with app.app_context():
        db.create_all()

    # 注册错误处理器
    @app.errorhandler(404)
    def page_not_found(e):
        from flask import render_template
        return render_template('404.html'), 404

    return app
