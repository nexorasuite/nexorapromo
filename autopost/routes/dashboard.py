from flask import Blueprint, render_template, session, redirect, url_for
from database import db, Post, User
from datetime import datetime, timedelta

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
def index():
    """Dashboard home page"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    user_id = session['user_id']
    user = User.query.get(user_id)
    
    # Get stats
    total_posts = Post.query.filter_by(user_id=user_id).count()
    posted_count = Post.query.filter_by(user_id=user_id, status='posted').count()
    pending_count = Post.query.filter_by(user_id=user_id, status='pending').count()
    draft_count = Post.query.filter_by(user_id=user_id, status='draft').count()
    
    # Get recent posts
    recent_posts = Post.query.filter_by(user_id=user_id).order_by(
        Post.created_at.desc()
    ).limit(5).all()
    
    # Get posts from last 7 days for chart
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    daily_posts = db.session.query(
        db.func.date(Post.created_at).label('date'),
        db.func.count(Post.id).label('count')
    ).filter(
        Post.user_id == user_id,
        Post.created_at >= seven_days_ago
    ).group_by(
        db.func.date(Post.created_at)
    ).all()
    
    chart_data = {
        'dates': [str(d[0]) for d in daily_posts],
        'counts': [d[1] for d in daily_posts]
    }
    
    return render_template('dashboard.html', 
        user=user,
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
    if 'user_id' not in session:
        return {'error': 'Unauthorized'}, 401
    
    user_id = session['user_id']
    
    stats = {
        'total': Post.query.filter_by(user_id=user_id).count(),
        'posted': Post.query.filter_by(user_id=user_id, status='posted').count(),
        'pending': Post.query.filter_by(user_id=user_id, status='pending').count(),
        'draft': Post.query.filter_by(user_id=user_id, status='draft').count(),
        'failed': Post.query.filter_by(user_id=user_id, status='failed').count(),
    }
    
    return stats
