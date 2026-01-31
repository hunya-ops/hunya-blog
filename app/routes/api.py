import os
import uuid
from flask import Blueprint, request, jsonify, current_app, url_for
from flask_login import login_required
from werkzeug.utils import secure_filename
from PIL import Image as PILImage
from app import db
from app.models import Image

from functools import wraps
from app.models import Image, Post

api_bp = Blueprint('api', __name__)


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        from app.models import Setting
        token = request.headers.get('X-API-Key')
        # Priority: Database setting > config.py (env variable)
        configured_token = Setting.get('api_key') or current_app.config.get('API_KEY')
        if not token or token != configured_token:
            return jsonify({'error': '未授权'}), 401
        return f(*args, **kwargs)
    return decorated


def login_or_token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        from app.models import Setting
        # Check for API Key first
        token = request.headers.get('X-API-Key')
        configured_token = Setting.get('api_key') or current_app.config.get('API_KEY')
        if token and token == configured_token:
            return f(*args, **kwargs)
        # Fallback to session auth
        from flask_login import current_user
        if current_user.is_authenticated:
            return f(*args, **kwargs)
        return jsonify({'error': '未授权'}), 401
    return decorated


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


@api_bp.route('/upload', methods=['POST'])
@login_or_token_required
def upload_image():
    if 'image' not in request.files:
        return jsonify({'error': '没有上传文件'}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': '没有选择文件'}), 400

    if file and allowed_file(file.filename):
        # 生成唯一文件名
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{uuid.uuid4().hex}.{ext}"
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)

        # 保存并压缩图片
        img = PILImage.open(file)
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')

        # 限制最大尺寸
        max_size = (1920, 1920)
        img.thumbnail(max_size, PILImage.Resampling.LANCZOS)
        img.save(filepath, 'JPEG', quality=85, optimize=True)

        # 保存到数据库
        image = Image(filename=filename)
        db.session.add(image)
        db.session.commit()

        return jsonify({
            'success': True,
            'url': url_for('static', filename=f'uploads/{filename}')
        })

    return jsonify({'error': '不支持的文件格式'}), 400


@api_bp.route('/posts', methods=['POST'])
@token_required
def create_post():
    data = request.json
    if not data or 'content' not in data:
        return jsonify({'error': '缺少内容'}), 400

    content = data.get('content')
    image_urls = data.get('image_urls', '')
    tags = data.get('tags', [])

    post = Post(
        content=content,
        image_urls=image_urls,
        post_type='uncut',  # iOS Shortcuts are primarily for 'uncut'
        is_published=True
    )

    if tags:
        post.set_tags(','.join(tags))

    db.session.add(post)
    db.session.commit()

    return jsonify({
        'success': True,
        'short_id': post.short_id,
        'url': post.url
    }), 201
