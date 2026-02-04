from flask import Blueprint, render_template, request, jsonify
from database import db, Post

history_bp = Blueprint('history', __name__)

@history_bp.route('/history')
def index():
    """Post history page"""
    posts = Post.query.order_by(
        Post.created_at.desc()
    ).paginate(page=request.args.get('page', 1, type=int), per_page=20)
    
    return render_template('history.html', posts=posts)

@history_bp.route('/api/posts', methods=['GET'])
def get_posts():
    """Get posts with filtering"""
    status = request.args.get('status')
    
    query = Post.query
    
    if status:
        query = query.filter_by(status=status)
    
    posts = query.order_by(Post.created_at.desc()).all()
    
    return jsonify([{
        'id': p.id,
        'content': p.content[:100],
        'platforms': p.get_platforms(),
        'status': p.status,
        'created_at': p.created_at.isoformat(),
        'posted_at': p.posted_at.isoformat() if p.posted_at else None,
        'scheduled_at': p.scheduled_at.isoformat() if p.scheduled_at else None
    } for p in posts])

@history_bp.route('/api/posts/<int:post_id>', methods=['GET', 'DELETE'])
def post_detail(post_id):
    """Get or delete post"""
    post = Post.query.get(post_id)
    
    if not post:
        return {'error': 'Post not found'}, 404
    
    if request.method == 'DELETE':
        db.session.delete(post)
        db.session.commit()
        return {'success': True}
    
    return jsonify({
        'id': post.id,
        'content': post.content,
        'image_path': post.image_path,
        'platforms': post.get_platforms(),
        'status': post.status,
        'created_at': post.created_at.isoformat(),
        'posted_at': post.posted_at.isoformat() if post.posted_at else None,
        'scheduled_at': post.scheduled_at.isoformat() if post.scheduled_at else None,
        'post_results': post.get_post_results()
    })
