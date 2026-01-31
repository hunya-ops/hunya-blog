import re
from flask import Blueprint, Response, current_app, url_for
from app.models import Post

feed_bp = Blueprint('feed', __name__)


@feed_bp.route('/feed.xml')
def rss_feed():
    posts = Post.query.filter_by(is_published=True)\
        .order_by(Post.created_at.desc())\
        .limit(20).all()

    blog_title = current_app.config['BLOG_TITLE']
    blog_desc = current_app.config['BLOG_DESCRIPTION']
    
    # Dynamically generate absolute URL based on request headers
    blog_home_url = url_for('main.index', _external=True)

    items = []
    for post in posts:
        title = post.title or post.get_excerpt(50)
        pub_date = post.created_at.strftime('%a, %d %b %Y %H:%M:%S +0000')
        # Dynamic absolute URL for post
        link = url_for('main.pulp_detail' if post.post_type == 'pulp' else 'main.uncut_detail', short_id=post.short_id, _external=True)
        
        items.append(f'''    <item>
      <title>{escape_xml(title)}</title>
      <link>{link}</link>
      <guid>{link}</guid>
      <pubDate>{pub_date}</pubDate>
      <description><![CDATA[{post.content.replace(']]>', ']]]]><![CDATA[>')}]]></description>
    </item>''')

    xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>{escape_xml(blog_title)}</title>
    <link>{blog_home_url}</link>
    <description>{escape_xml(blog_desc)}</description>
    <language>zh-CN</language>
{chr(10).join(items)}
  </channel>
</rss>'''

    return Response(xml, mimetype='application/rss+xml')


def escape_xml(text):
    """转义 XML 特殊字符"""
    if not text:
        return ''
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    text = text.replace('"', '&quot;')
    return text
