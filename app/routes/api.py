import os
import uuid
from flask import Blueprint, request, jsonify, current_app, url_for
from flask_login import login_required
from werkzeug.utils import secure_filename
from PIL import Image as PILImage
from app import db
from app.models import Image

api_bp = Blueprint('api', __name__)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


@api_bp.route('/upload', methods=['POST'])
@login_required
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
