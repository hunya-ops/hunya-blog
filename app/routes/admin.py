from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import platform
import sys
import os
import re
from datetime import datetime
from app import db, cache
from app.models import Post, Tag, Admin, Setting, Image

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard'))

    if request.method == 'POST':
        password = request.form.get('password')
        admin_pwd = Setting.get('admin_password', current_app.config['ADMIN_PASSWORD'])

        # 支持明文迁移到哈希
        is_valid = False
        if admin_pwd.startswith(('pbkdf2:', 'scrypt:', 'sha256:')):
            is_valid = check_password_hash(admin_pwd, password)
        else:
            is_valid = (password == admin_pwd)
            if is_valid:
                # 自动升级为哈希
                Setting.set('admin_password', generate_password_hash(password, method='pbkdf2:sha256'))

        if is_valid:
            user = Admin('admin')
            login_user(user)
            return redirect(url_for('admin.dashboard'))
        flash('密码错误', 'error')

    return render_template('admin/login.html')


@admin_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@admin_bp.route('/')
@login_required
def dashboard():
    stats = {
        'total_posts': Post.query.filter_by(post_type='pulp').count(),
        'total_weibo': Post.query.filter_by(post_type='uncut').count(),
        'total_tags': Tag.query.count()
    }
    recent_posts = Post.query.order_by(Post.updated_at.desc()).limit(5).all()
    return render_template('admin/dashboard.html', stats=stats, recent_posts=recent_posts, now=datetime.now())


def get_posts_by_type(post_type, title):
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', 'all')
    query = Post.query.filter_by(post_type=post_type)
    
    if status == 'published':
        query = query.filter_by(is_published=True)
    elif status == 'draft':
        query = query.filter_by(is_published=False)
        
    posts = query.order_by(Post.created_at.desc()).paginate(page=page, per_page=15)
    return render_template('admin/posts.html', posts=posts, title=title, current_status=status)


@admin_bp.route('/pulp')
@login_required
def pulp():
    return get_posts_by_type('pulp', '文章管理')


@admin_bp.route('/uncut')
@login_required
def uncut():
    return get_posts_by_type('uncut', '动态管理')


@admin_bp.route('/new', methods=['GET', 'POST'])
@admin_bp.route('/new/<post_type>', methods=['GET', 'POST'])
@login_required
def new_post(post_type='uncut'):
    if request.method == 'POST':
        # 解析发布时间
        created_at_str = request.form.get('created_at')
        created_at = None
        if created_at_str:
            try:
                created_at = datetime.strptime(created_at_str, '%Y-%m-%dT%H:%M')
            except ValueError:
                pass
        
        # 过滤掉无效的图片地址
        image_urls_raw = request.form.get('image_urls', '')
        image_urls = None
        if image_urls_raw:
            image_urls = ','.join([url.strip() for url in image_urls_raw.split(',') 
                                 if url.strip() and url.strip() != 'None'])
        
        action = request.form.get('action')
        post = Post(
            post_type=request.form.get('post_type', post_type),
            title=request.form.get('title') or None,
            content=request.form.get('content'),
            image_urls=image_urls,
            is_published=(action == 'publish')
        )
        if created_at:
            post.created_at = created_at
        post.set_tags(request.form.get('tags', ''))
        
        db.session.add(post)
        db.session.commit()
        cache.clear()
        
        if post.is_published:
            flash('已发布', 'success')
        else:
            flash('已存为草稿', 'success')
        return redirect(url_for('admin.pulp') if post.post_type == 'pulp' else url_for('admin.uncut'))

    return render_template('admin/editor.html', post=None, post_type=post_type, now=datetime.now())


@admin_bp.route('/edit/<int:post_id>', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)

    if request.method == 'POST':
        post.post_type = request.form.get('post_type', post.post_type)
        post.title = request.form.get('title') or None
        post.content = request.form.get('content')
        # 过滤掉无效的图片地址
        image_urls_raw = request.form.get('image_urls', '')
        if image_urls_raw:
            post.image_urls = ','.join([url.strip() for url in image_urls_raw.split(',') 
                                      if url.strip() and url.strip() != 'None'])
        else:
            post.image_urls = None
            
        action = request.form.get('action')
        post.set_tags(request.form.get('tags', ''))
        
        # 解析并更新发布时间
        created_at_str = request.form.get('created_at')
        if created_at_str:
            try:
                post.created_at = datetime.strptime(created_at_str, '%Y-%m-%dT%H:%M')
            except ValueError:
                pass

        # 根据动作更新发布状态
        if action == 'publish':
            post.is_published = True
            msg = '已发布'
        elif action == 'unpublish':
            post.is_published = False
            msg = '已取消发布'
        else: # action == 'save' / 'draft'
            # 保持原有状态不变
            msg = '已更新' if post.is_published else '草稿已更新'

        db.session.commit()
        cache.clear()
        
        flash(msg, 'success')
        return redirect(url_for('admin.pulp') if post.post_type == 'pulp' else url_for('admin.uncut'))

    return render_template('admin/editor.html', post=post, post_type=post.post_type)


@admin_bp.route('/delete/<int:post_id>', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    post_type = post.post_type
    db.session.delete(post)
    db.session.commit()
    cache.clear()
    flash('已删除', 'success')
    return redirect(url_for('admin.pulp') if post_type == 'pulp' else url_for('admin.uncut'))


@admin_bp.route('/toggle/<int:post_id>', methods=['POST'])
@login_required
def toggle_publish(post_id):
    post = Post.query.get_or_404(post_id)
    post.is_published = not post.is_published
    db.session.commit()
    cache.clear()
    status = '已发布' if post.is_published else '已取消发布'
    flash(status, 'success')
    return redirect(request.referrer or url_for('admin.dashboard'))


# ========== 标签管理 ==========
@admin_bp.route('/tags')
@login_required
def tags():
    all_tags = Tag.query.all()
    tags_data = []
    for tag in all_tags:
        tags_data.append({'tag': tag, 'count': tag.posts.count()})
    tags_data.sort(key=lambda x: x['count'], reverse=True)
    empty_count = sum(1 for t in tags_data if t['count'] == 0)
    return render_template('admin/tags.html', tags_data=tags_data, empty_count=empty_count)


@admin_bp.route('/tags/clean', methods=['POST'])
@login_required
def clean_empty_tags():
    empty_tags = Tag.query.filter(~Tag.posts.any()).all()
    count = len(empty_tags)
    for tag in empty_tags:
        db.session.delete(tag)
    db.session.commit()
    cache.clear()
    flash(f'已删除 {count} 个空标签', 'success')
    return redirect(url_for('admin.tags'))


# ========== 图片管理 ==========
def get_all_content_text():
    """获取所有可能包含图片引用的文本内容（用于暴力匹配）"""
    text_content = ""
    
    # 1. 扫描文章
    posts = Post.query.all()
    for post in posts:
        if post.image_urls:
            text_content += post.image_urls
        if post.content:
            text_content += post.content
            
    # 2. 扫描设置
    settings = Setting.query.all()
    for s in settings:
        if s.value:
            text_content += s.value
            
    return text_content


@admin_bp.route('/images')
@login_required
def images():
    upload_folder = current_app.config['UPLOAD_FOLDER']
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
        
    all_files = []
    # 扫描文件系统
    with os.scandir(upload_folder) as entries:
        for entry in entries:
            if entry.is_file() and not entry.name.startswith('.'):
                stat = entry.stat()
                all_files.append({
                    'name': entry.name,
                    'size': stat.st_size,
                    'mtime': stat.st_mtime,
                    'url': url_for('static', filename=f'uploads/{entry.name}')
                })
    
    # 按时间倒序排序
    all_files.sort(key=lambda x: x['mtime'], reverse=True)
    
    # 扫描使用情况
    all_text = get_all_content_text()
    used_count = 0
    
    # 标记状态
    for f in all_files:
        # 暴力匹配：只要文件名出现在任何文本中，就算被使用
        # 对于UUID文件名，这极其准确；对于短文件名，宁可误判为使用也不能误删
        f['is_used'] = (f['name'] in all_text)
        if f['is_used']:
            used_count += 1
            
        f['size_fmt'] = f"{f['size']/1024:.1f} KB" if f['size'] < 1024*1024 else f"{f['size']/(1024*1024):.1f} MB"
        f['date_fmt'] = datetime.fromtimestamp(f['mtime']).strftime('%Y-%m-%d %H:%M')

    return render_template('admin/images.html', files=all_files, total=len(all_files), used_count=used_count)


@admin_bp.route('/images/delete/<filename>', methods=['POST'])
@login_required
def delete_image(filename):
    fp = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(fp):
        os.remove(fp)
    
    img = Image.query.filter_by(filename=filename).first()
    if img:
        db.session.delete(img)
        db.session.commit()
        
    flash('图片已删除', 'success')
    return redirect(url_for('admin.images'))


@admin_bp.route('/images/clean', methods=['POST'])
@login_required
def clean_unused_images():
    all_text = get_all_content_text()
    upload_folder = current_app.config['UPLOAD_FOLDER']
    
    count = 0
    with os.scandir(upload_folder) as entries:
        for entry in entries:
            # 只有当文件名完全不出现在文本中时，才删除
            if entry.is_file() and not entry.name.startswith('.') and entry.name not in all_text:
                os.remove(entry.path)
                # 同步清理数据库记录
                img = Image.query.filter_by(filename=entry.name).first()
                if img:
                    db.session.delete(img)
                count += 1
    
    db.session.commit()
    flash(f'已清理 {count} 张未使用图片', 'success')
    return redirect(url_for('admin.images'))


# ========== 系统设置 ==========
@admin_bp.route('/settings')
@login_required
def settings():
    return render_template('admin/settings/index.html')


@admin_bp.route('/settings/home', methods=['GET', 'POST'])
@login_required
def settings_home():
    if request.method == 'POST':
        content = request.form.get('content', '')
        Setting.set('home_content', content)
        cache.clear()
        flash('首页内容已保存', 'success')
        return redirect(url_for('admin.settings_home'))

    content = Setting.get('home_content', '')
    return render_template('admin/settings/home.html', content=content)


@admin_bp.route('/settings/basic', methods=['GET', 'POST'])
@login_required
def settings_basic():
    if request.method == 'POST':
        Setting.set('blog_title', request.form.get('blog_title', ''))
        Setting.set('blog_description', request.form.get('blog_description', ''))
        Setting.set('api_key', request.form.get('api_key', ''))
        # Posts per page setting
        posts_per_page = request.form.get('posts_per_page', '20')
        try:
            posts_per_page = max(5, min(100, int(posts_per_page)))
        except ValueError:
            posts_per_page = 20
        Setting.set('posts_per_page', str(posts_per_page))
        # Navigation visibility settings
        Setting.set('show_archive', '1' if request.form.get('show_archive') else '0')
        Setting.set('show_tags', '1' if request.form.get('show_tags') else '0')
        # New: Uncut posts visibility settings
        Setting.set('archive_show_uncut', '1' if request.form.get('archive_show_uncut') else '0')
        Setting.set('tag_show_uncut', '1' if request.form.get('tag_show_uncut') else '0')
        cache.clear()
        flash('设置已保存', 'success')
        return redirect(url_for('admin.settings_basic'))

    return render_template('admin/settings/basic.html',
        blog_title=Setting.get('blog_title', current_app.config['BLOG_TITLE']),
        blog_description=Setting.get('blog_description', current_app.config['BLOG_DESCRIPTION']),
        api_key=Setting.get('api_key', current_app.config.get('API_KEY', '')),
        posts_per_page=int(Setting.get('posts_per_page', str(current_app.config.get('POSTS_PER_PAGE', 20)))),
        show_archive=Setting.get('show_archive', '1') == '1',
        show_tags=Setting.get('show_tags', '1') == '1',
        archive_show_uncut=Setting.get('archive_show_uncut', '1') == '1',
        tag_show_uncut=Setting.get('tag_show_uncut', '1') == '1'
    )


@admin_bp.route('/settings/password', methods=['GET', 'POST'])
@login_required
def settings_password():
    if request.method == 'POST':
        old_pwd = request.form.get('old_password')
        new_pwd = request.form.get('new_password')
        confirm_pwd = request.form.get('confirm_password')

        current_pwd_record = Setting.get('admin_password', current_app.config['ADMIN_PASSWORD'])

        # 验证原密码
        is_old_valid = False
        if current_pwd_record.startswith(('pbkdf2:', 'scrypt:', 'sha256:')):
            is_old_valid = check_password_hash(current_pwd_record, old_pwd)
        else:
            is_old_valid = (old_pwd == current_pwd_record)

        if not is_old_valid:
            flash('原密码错误', 'error')
        elif new_pwd != confirm_pwd:
            flash('两次输入的新密码不一致', 'error')
        elif len(new_pwd) < 6:
            flash('新密码长度至少6位', 'error')
        else:
            Setting.set('admin_password', generate_password_hash(new_pwd, method='pbkdf2:sha256'))
            flash('密码修改成功', 'success')
            return redirect(url_for('admin.settings_password'))

    return render_template('admin/settings/password.html')


@admin_bp.route('/settings/system')
@login_required
def settings_system():
    import flask
    
    # 统计数据库大小
    db_path = current_app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
    db_size = "未知"
    if os.path.exists(db_path):
        size_bytes = os.path.getsize(db_path)
        db_size = f"{size_bytes / (1024*1024):.2f} MB" if size_bytes > 1024*1024 else f"{size_bytes / 1024:.2f} KB"

    # 统计上传文件大小
    upload_path = current_app.config['UPLOAD_FOLDER']
    upload_size = "0 KB"
    if os.path.exists(upload_path):
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(upload_path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                total_size += os.path.getsize(fp)
        upload_size = f"{total_size / (1024*1024):.2f} MB" if total_size > 1024*1024 else f"{total_size / 1024:.2f} KB"

    info = {
        'python_version': sys.version.split()[0],
        'flask_version': flask.__version__,
        'platform': platform.platform(),
        'processor': platform.processor() or '未知',
        'database_size': db_size,
        'upload_size': upload_size,
        'total_posts': Post.query.filter_by(post_type='pulp').count(),
        'total_weibo': Post.query.filter_by(post_type='uncut').count(),
        'server_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'debug_mode': '开启' if current_app.debug else '关闭'
    }
    return render_template('admin/settings/system.html', info=info)
def get_all_used_images():
    used = set()
    # 1. 扫描 Setting
    # 2. 扫描 Post.image_urls
    # 3. 扫描 Post.content
    return used
