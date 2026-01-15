from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify
from database import db, Post, Campaign, User
from datetime import datetime

campaigns_bp = Blueprint('campaigns', __name__)

@campaigns_bp.route('/campaigns')
def index():
    """Campaigns page"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    user_id = session['user_id']
    campaigns = Campaign.query.filter_by(user_id=user_id).order_by(
        Campaign.created_at.desc()
    ).all()
    
    return render_template('campaigns.html', campaigns=campaigns)

@campaigns_bp.route('/api/campaigns', methods=['GET', 'POST'])
def manage_campaigns():
    """Create and list campaigns"""
    if 'user_id' not in session:
        return {'error': 'Unauthorized'}, 401
    
    user_id = session['user_id']
    
    if request.method == 'GET':
        campaigns = Campaign.query.filter_by(user_id=user_id).all()
        return jsonify([{
            'id': c.id,
            'name': c.name,
            'description': c.description,
            'platforms': c.get_platforms(),
            'status': c.status,
            'post_count': len(c.posts),
            'created_at': c.created_at.isoformat()
        } for c in campaigns])
    
    # POST - Create new campaign
    name = request.get_json().get('name')
    description = request.get_json().get('description')
    platforms = request.get_json().get('platforms', [])
    
    if not name:
        return {'error': 'Campaign name required'}, 400
    
    if not platforms:
        return {'error': 'At least one platform required'}, 400
    
    campaign = Campaign(
        user_id=user_id,
        name=name,
        description=description
    )
    campaign.set_platforms(platforms)
    
    db.session.add(campaign)
    db.session.commit()
    
    return {'success': True, 'campaign_id': campaign.id}, 201

@campaigns_bp.route('/api/campaigns/<int:campaign_id>/posts', methods=['POST'])
def add_to_campaign(campaign_id):
    """Add post to campaign"""
    if 'user_id' not in session:
        return {'error': 'Unauthorized'}, 401
    
    user_id = session['user_id']
    campaign = Campaign.query.get(campaign_id)
    
    if not campaign or campaign.user_id != user_id:
        return {'error': 'Campaign not found'}, 404
    
    content = request.get_json().get('content')
    if not content:
        return {'error': 'Content required'}, 400
    
    post = Post(
        user_id=user_id,
        campaign_id=campaign_id,
        content=content,
        status='draft'
    )
    post.set_platforms(campaign.get_platforms())
    
    db.session.add(post)
    db.session.commit()
    
    return {'success': True, 'post_id': post.id}, 201
