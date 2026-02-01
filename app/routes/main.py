from flask import Blueprint, render_template, request, current_app
from app import db
from app.models import Post, Tag
from sqlalchemy import extract

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Homepage now shows Uncut (Dynamic) posts only"""
    page = request.args.get('page', 1, type=int)
    posts = Post.get_published_posts(post_type='uncut').paginate(page=page, per_page=current_app.config['POSTS_PER_PAGE'])
    return render_template('index.html', posts=posts, page_title='动态')


@main_bp.route('/pulp')
def articles():
    """Pulp articles only"""
    page = request.args.get('page', 1, type=int)
    posts = Post.get_published_posts(post_type='pulp').paginate(page=page, per_page=current_app.config['POSTS_PER_PAGE'])
    return render_template('index.html', posts=posts, page_title='文章')


@main_bp.route('/uncut')
def feeds():
    """Redirect old /uncut to homepage"""
    return redirect(url_for('main.index'))


@main_bp.route('/pulp/<short_id>', endpoint='pulp_detail')
@main_bp.route('/uncut/<short_id>', endpoint='uncut_detail')
def post_detail(short_id):
    post = Post.query.filter_by(short_id=short_id).first_or_404()
    # Redirect if accessed with wrong prefix for SEO and consistency
    if request.path.startswith('/pulp/') and post.post_type != 'pulp':
        return redirect(post.url)
    if request.path.startswith('/uncut/') and post.post_type != 'uncut':
        return redirect(post.url)
    return render_template('post.html', post=post)


@main_bp.route('/tag/<tag_name>')
def tag_posts(tag_name):
    # Special case for untagged posts
    if tag_name == '无标签':
        return untagged_posts()
    
    tag = Tag.query.filter_by(name=tag_name).first_or_404()
    posts = tag.posts.filter_by(is_published=True).order_by(Post.created_at.desc()).all()
    
    # Group posts by month
    months_data = {}
    for post in posts:
        month_key = post.created_at.strftime('%Y-%m')
        if month_key not in months_data:
            months_data[month_key] = {
                'year': post.created_at.year,
                'month': post.created_at.month,
                'posts': []
            }
        months_data[month_key]['posts'].append(post)
    
    # Sort months by date descending
    sorted_months = sorted(months_data.values(), key=lambda x: (x['year'], x['month']), reverse=True)
    
    return render_template('tag.html', tag=tag, months=sorted_months, total_count=len(posts))


def untagged_posts():
    """Posts without any tags"""
    # Get all published posts that have no tags
    posts = Post.query.filter_by(is_published=True).filter(~Post.tags.any()).order_by(Post.created_at.desc()).all()
    
    # Group by month
    months_data = {}
    for post in posts:
        month_key = post.created_at.strftime('%Y-%m')
        if month_key not in months_data:
            months_data[month_key] = {
                'year': post.created_at.year,
                'month': post.created_at.month,
                'posts': []
            }
        months_data[month_key]['posts'].append(post)
    
    sorted_months = sorted(months_data.values(), key=lambda x: (x['year'], x['month']), reverse=True)
    
    # Create a fake tag object for template compatibility
    class FakeTag:
        name = '无标签'
    
    return render_template('tag.html', tag=FakeTag(), months=sorted_months, total_count=len(posts))


@main_bp.route('/archive')
def archive():
    # 1. Get all distinct years from DB for the sidebar (Articles/Pulp only)
    years_query = db.session.query(extract('year', Post.created_at)).filter_by(is_published=True, post_type='pulp').distinct().all()
    all_years = sorted([int(y[0]) for y in years_query], reverse=True)
    
    # 2. Determine which year to show
    current_year = request.args.get('year', type=int)
    if not current_year and all_years:
        current_year = all_years[0]
    
    if not current_year:
        return render_template('archive.html', years_data={}, sorted_years=[], current_year=None)

    # 3. Fetch posts ONLY for the current_year (Articles/Pulp only)
    posts = Post.query.filter(
        extract('year', Post.created_at) == current_year, 
        Post.is_published == True,
        Post.post_type == 'pulp'
    ).order_by(Post.created_at.desc()).all()

    # 4. Process data
    years_data = {
        current_year: {
            'months': {m: [] for m in range(1, 13)},
            'total_count': 0,
            'stats': []
        }
    }
    
    for post in posts:
        month = post.created_at.month
        years_data[current_year]['months'][month].append(post)
        years_data[current_year]['total_count'] += 1

    # Prepare stats
    stats = []
    for m in range(1, 13):
        month_posts = years_data[current_year]['months'][m]
        pulp_count = len(month_posts) # Only pulp posts are fetched
        stats.append({'short': 0, 'long': pulp_count, 'total': pulp_count})
    years_data[current_year]['stats'] = stats
    
    return render_template('archive.html', 
                           years_data=years_data, 
                           sorted_years=[current_year], 
                           all_years=all_years,
                           current_year=current_year)


@main_bp.route('/tags')
def all_tags():
    # Get total published posts count
    total_posts = Post.query.filter_by(is_published=True).count()
    
    if total_posts == 0:
        return render_template('tags.html', tag_data=[], total_posts=0, untagged_count=0)
    
    # Get all tags with their post counts
    tags = Tag.query.all()
    tag_data = []
    tagged_post_ids = set()
    
    for tag in tags:
        count = tag.post_count
        if count > 0:
            # Collect post IDs that have this tag
            for post in tag.posts.filter_by(is_published=True).all():
                tagged_post_ids.add(post.id)
            
            percentage = (count / total_posts) * 100
            tag_data.append({
                'name': tag.name,
                'count': count,
                'percentage': percentage
            })
    
    tag_data.sort(key=lambda x: x['count'], reverse=True)
    
    untagged_count = total_posts - len(tagged_post_ids)
    untagged_percentage = (untagged_count / total_posts) * 100 if untagged_count > 0 else 0
    
    return render_template('tags.html', 
                           tag_data=tag_data, 
                           total_posts=total_posts,
                           untagged_count=untagged_count,
                           untagged_percentage=untagged_percentage)
