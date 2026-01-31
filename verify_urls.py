from app import create_app
from flask import url_for

def verify():
    app = create_app()
    with app.app_context():
        from app.models import Post
        post = Post.query.first()
        if post:
            url = url_for('main.post_detail', short_id=post.short_id)
            print(f"Sample Post Detail URL: {url}")
            if post.short_id in url:
                print("SUCCESS: URL contains short_id")
            else:
                print("FAILURE: URL does not contain short_id")
        else:
            print("No posts found to verify.")

if __name__ == '__main__':
    verify()
