from flask import Blueprint, render_template, request, jsonify, current_app
from database import db, Post, PostTemplate
from datetime import datetime
from werkzeug.utils import secure_filename
import os

composer_bp = Blueprint('composer', __name__)

@composer_bp.route('/compose')
def compose():
    """Compose page"""
    templates = PostTemplate.query.all()
    
    return render_template('compose.html', templates=templates)

@composer_bp.route('/schedule')
def schedule():
    """Schedule page"""
    posts = Post.query.filter_by(status='pending').order_by(
        Post.scheduled_at
    ).all()
    
    return render_template('schedule.html', posts=posts)

@composer_bp.route('/api/post/manual', methods=['POST'])
def post_manual():
    """Create manual post"""
    content = request.form.get('content')
    platforms = request.form.getlist('platforms')
    save_as_template = request.form.get('save_template') == 'true'
    template_name = request.form.get('template_name')
    
    if not content:
        return {'error': 'Content required'}, 400
    
    if not platforms:
        return {'error': 'At least one platform required'}, 400
    
    # Handle image upload
    image_path = None
    if 'image' in request.files:
        file = request.files['image']
        if file and file.filename:
            filename = secure_filename(file.filename)
            upload_dir = current_app.config['UPLOAD_FOLDER']
            os.makedirs(upload_dir, exist_ok=True)
            image_path = os.path.join(upload_dir, f"{datetime.utcnow().timestamp()}_{filename}")
            file.save(image_path)
    
    # Create post
    post = Post(
        content=content,
        image_path=image_path,
        status='posted',
        posted_at=datetime.utcnow()
    )
    post.set_platforms(platforms)
    
    db.session.add(post)
    db.session.commit()
    
    # Save as template if requested
    if save_as_template and template_name:
        template = PostTemplate(
            name=template_name,
            content=content,
            image_path=image_path
        )
        db.session.add(template)
        db.session.commit()
    
    return {'success': True, 'post_id': post.id}, 201

@composer_bp.route('/api/post/schedule', methods=['POST'])
def post_schedule():
    """Schedule a post"""
    content = request.form.get('content')
    platforms = request.form.getlist('platforms')
    scheduled_at_str = request.form.get('scheduled_at')
    
    if not content:
        return {'error': 'Content required'}, 400
    
    if not platforms:
        return {'error': 'At least one platform required'}, 400
    
    if not scheduled_at_str:
        return {'error': 'Schedule time required'}, 400
    
    try:
        scheduled_at = datetime.fromisoformat(scheduled_at_str)
    except:
        return {'error': 'Invalid datetime format'}, 400
    
    # Handle image upload
    image_path = None
    if 'image' in request.files:
        file = request.files['image']
        if file and file.filename:
            filename = secure_filename(file.filename)
            upload_dir = current_app.config['UPLOAD_FOLDER']
            os.makedirs(upload_dir, exist_ok=True)
            image_path = os.path.join(upload_dir, f"{datetime.utcnow().timestamp()}_{filename}")
            file.save(image_path)
    
    # Create scheduled post
    post = Post(
        content=content,
        image_path=image_path,
        status='pending',
        scheduled_at=scheduled_at
    )
    post.set_platforms(platforms)
    
    db.session.add(post)
    db.session.commit()
    
    return {'success': True, 'post_id': post.id}, 201

@composer_bp.route('/api/templates', methods=['GET', 'POST'])
def templates():
    """Manage post templates"""
    if request.method == 'GET':
        templates = PostTemplate.query.all()
        return jsonify([{
            'id': t.id,
            'name': t.name,
            'content': t.content,
            'image_path': t.image_path
        } for t in templates])
    
    # POST - Create new template
    name = request.form.get('name')
    content = request.form.get('content')
    
    if not name or not content:
        return {'error': 'Name and content required'}, 400
    
    # Check if template name already exists
    existing = PostTemplate.query.filter_by(name=name).first()
    if existing:
        return {'error': 'Template name already exists'}, 400
    
    template = PostTemplate(
        name=name,
        content=content
    )
    db.session.add(template)
    db.session.commit()
    
    return {'success': True, 'template_id': template.id}, 201
