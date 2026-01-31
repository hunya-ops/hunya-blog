from app import create_app, db
from app.models import Post
import sqlite3
import os
import sys

def migrate_production():
    """
    Production migration script for short_id and URL security update.
    This script adds the short_id column and populates it for existing posts.
    """
    app = create_app()
    with app.app_context():
        # 1. Check database path
        db_uri = app.config['SQLALCHEMY_DATABASE_URI']
        db_path = db_uri.replace('sqlite:///', '')
        
        if not os.path.exists(db_path):
            print(f"❌ Error: Database not found at {db_path}")
            sys.exit(1)
            
        print(f"📦 Connecting to database: {db_path}")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 2. Add short_id column
        try:
            print("🛠 Adding short_id column to 'post' table...")
            cursor.execute("ALTER TABLE post ADD COLUMN short_id VARCHAR(12)")
            conn.commit()
            print("✅ Column added successfully.")
        except sqlite3.OperationalError:
            print("ℹ️ Column 'short_id' already exists, skipping...")
            
        # 3. Generate IDs for posts without one
        print("🔍 Searching for posts needing migration...")
        posts = Post.query.filter((Post.short_id == None) | (Post.short_id == '')).all()
        
        if not posts:
            print("✅ No posts need migration.")
        else:
            print(f"🚀 Migrating {len(posts)} posts...")
            for post in posts:
                # Keep generating until unique
                while True:
                    new_id = Post.generate_short_id()
                    if not Post.query.filter_by(short_id=new_id).first():
                        post.short_id = new_id
                        break
                print(f"   - Post {post.id} -> {post.short_id}")
            
            db.session.commit()
            print(f"✅ Successfully migrated {len(posts)} posts.")
            
        # 4. Create Index
        try:
            print("⚡️ Creating unique index for short_id...")
            cursor.execute("CREATE UNIQUE INDEX ix_post_short_id ON post (short_id)")
            conn.commit()
            print("✅ Index created.")
        except sqlite3.OperationalError:
            print("ℹ️ Index already exists, skipping...")
            
        conn.close()
        print("\n🎉 Production migration complete!")
        print("👉 You can now safely delete this script.")

if __name__ == '__main__':
    migrate_production()
