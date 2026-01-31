import os
from dotenv import load_dotenv

if os.path.exists(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'env')):
    load_dotenv('env')
else:
    load_dotenv()


basedir = os.path.abspath(os.path.dirname(__file__))

# Data directory for persistence
DATA_DIR = os.path.join(basedir, 'data')
os.makedirs(DATA_DIR, exist_ok=True)

def get_secret_key():
    secret_key = os.environ.get('SECRET_KEY')
    if secret_key:
        return secret_key
    
    secret_file = os.path.join(DATA_DIR, '.secret_key')
    if os.path.exists(secret_file):
        with open(secret_file, 'r') as f:
            return f.read().strip()
    
    # Generate new key
    try:
        new_key = os.urandom(24).hex()
        with open(secret_file, 'w') as f:
            f.write(new_key)
        return new_key
    except IOError:
        return 'dev-secret-key'

class Config:
    SECRET_KEY = get_secret_key()
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(DATA_DIR, 'blog.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Security Headers & Cookies
    SESSION_COOKIE_SECURE = os.environ.get('FLASK_ENV') == 'production'
    REMEMBER_COOKIE_SECURE = os.environ.get('FLASK_ENV') == 'production'
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True

    # Upload Configuration
    UPLOAD_FOLDER = os.path.join(basedir, 'app', 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

    # Admin Configuration
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD') or 'admin'

    # Blog Configuration
    BLOG_TITLE = os.environ.get('BLOG_TITLE') or '我的博客'
    BLOG_DESCRIPTION = os.environ.get('BLOG_DESCRIPTION') or '一个简单的博客'
    POSTS_PER_PAGE = 20
