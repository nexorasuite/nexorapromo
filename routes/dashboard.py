from flask import Blueprint, render_template
from database import db, Post
from datetime import datetime, timedelta

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
def index():
    """Dashboard home page"""
    # Get stats
    total_posts = Post.query.count()
    posted_count = Post.query.filter_by(status='posted').count()
    pending_count = Post.query.filter_by(status='pending').count()
    draft_count = Post.query.filter_by(status='draft').count()
    
    # Get recent posts
    recent_posts = Post.query.order_by(
        Post.created_at.desc()
    ).limit(5).all()
    
    # Get posts from last 7 days for chart
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    daily_posts = db.session.query(
        db.func.date(Post.created_at).label('date'),
        db.func.count(Post.id).label('count')
    ).filter(
        Post.created_at >= seven_days_ago
    ).group_by(
        db.func.date(Post.created_at)
    ).all()
    
    chart_data = {
        'dates': [str(d[0]) for d in daily_posts],
        'counts': [d[1] for d in daily_posts]
    }
    
    return render_template('dashboard.html', 
        total_posts=total_posts,
        posted_count=posted_count,
        pending_count=pending_count,
        draft_count=draft_count,
        recent_posts=recent_posts,
        chart_data=chart_data
    )

@dashboard_bp.route('/api/dashboard/stats')
def get_stats():
    """Get dashboard statistics"""
    stats = {
        'total': Post.query.count(),
        'posted': Post.query.filter_by(status='posted').count(),
        'pending': Post.query.filter_by(status='pending').count(),
        'draft': Post.query.filter_by(status='draft').count(),
        'failed': Post.query.filter_by(status='failed').count(),
    }
    
    return stats
