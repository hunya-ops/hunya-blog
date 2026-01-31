from datetime import datetime
import re
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import random
import string
from app import db, login_manager

# 文章-标签关联表
post_tags = db.Table('post_tags',
    db.Column('post_id', db.Integer, db.ForeignKey('post.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True)
)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    short_id = db.Column(db.String(12), unique=True, index=True)
    post_type = db.Column(db.String(10), default='short')  # 'long' or 'short'
    title = db.Column(db.String(200), nullable=True)
    content = db.Column(db.Text, nullable=False)
    image_urls = db.Column(db.Text, nullable=True)  # 多图URL，逗号分隔
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    is_published = db.Column(db.Boolean, default=True)

    def __init__(self, **kwargs):
        super(Post, self).__init__(**kwargs)
        if not self.short_id:
            self.short_id = self.generate_short_id()

    @staticmethod
    def generate_short_id():
        characters = string.ascii_letters + string.digits
        return ''.join(random.choices(characters, k=12))

    tags = db.relationship('Tag', secondary=post_tags, backref=db.backref('posts', lazy='dynamic'))
    images = db.relationship('Image', backref='post', lazy='dynamic')

    def get_image_list(self):
        """获取图片URL列表"""
        if not self.image_urls:
            return []
        return [url.strip() for url in self.image_urls.split(',') if url.strip()]

    def get_excerpt(self, length=140):
        """获取纯文本摘要"""
        text = self.content
        # 移除 markdown 图片 ![alt](url)
        text = re.sub(r'!\[.*?\]\(.*?\)', '', text)
        # 移除 HTML 标签
        text = re.sub(r'<[^>]+>', '', text)
        # 移除多余空白
        text = re.sub(r'\s+', ' ', text).strip()
        return text[:length] + '...' if len(text) > length else text

    @property
    def tags_string(self):
        """返回逗号分隔的标签字符串"""
        return ', '.join([tag.name for tag in self.tags])

    def set_tags(self, tags_str):
        """通过逗号分隔的字符串设置标签"""
        if not tags_str:
            self.tags = []
            return
        
        # 支持中英文逗号
        tags_str = tags_str.replace('，', ',')
        tag_names = [name.strip() for name in tags_str.split(',') if name.strip()]
        
        new_tags = []
        for name in tag_names:
            tag = Tag.query.filter_by(name=name).first()
            if not tag:
                tag = Tag(name=name)
                db.session.add(tag)
            new_tags.append(tag)
        self.tags = new_tags

    @classmethod
    def get_published_posts(cls, post_type=None):
        query = cls.query.filter_by(is_published=True)
        if post_type:
            query = query.filter_by(post_type=post_type)
        return query.order_by(cls.created_at.desc())


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

    @property
    def post_count(self):
        return self.posts.filter_by(is_published=True).count()


class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)


class Setting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), unique=True, nullable=False)
    value = db.Column(db.Text, nullable=True)

    @staticmethod
    def get(key, default=None):
        s = Setting.query.filter_by(key=key).first()
        return s.value if s else default

    @staticmethod
    def set(key, value):
        s = Setting.query.filter_by(key=key).first()
        if s:
            s.value = str(value)
        else:
            s = Setting(key=key, value=str(value))
            db.session.add(s)
        db.session.commit()


class Admin(UserMixin):
    """简单的管理员用户类"""
    def __init__(self, id):
        self.id = id


@login_manager.user_loader
def load_user(user_id):
    if user_id == 'admin':
        return Admin('admin')
    return None
