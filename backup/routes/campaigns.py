from flask import Blueprint, render_template, request, jsonify
from database import db, Post, Campaign
from datetime import datetime

campaigns_bp = Blueprint('campaigns', __name__)

@campaigns_bp.route('/campaigns')
def index():
    """Campaigns page"""
    campaigns = Campaign.query.order_by(
        Campaign.created_at.desc()
    ).all()
    
    return render_template('campaigns.html', campaigns=campaigns)

@campaigns_bp.route('/api/campaigns', methods=['GET', 'POST'])
def manage_campaigns():
    """Create and list campaigns"""
    if request.method == 'GET':
        campaigns = Campaign.query.all()
        return jsonify([{
            'id': c.id,
            'name': c.name,
            'description': c.description,
            'platforms': c.get_platforms(),
            'posting_interval': c.posting_interval,
            'status': c.status,
            'post_count': len(c.posts),
            'created_at': c.created_at.isoformat()
        } for c in campaigns])
    
    # POST - Create new campaign
    name = request.get_json().get('name')
    description = request.get_json().get('description')
    platforms = request.get_json().get('platforms', [])
    posting_interval = request.get_json().get('posting_interval', 0)
    
    if not name:
        return {'error': 'Campaign name required'}, 400
    
    if not platforms:
        return {'error': 'At least one platform required'}, 400
    
    campaign = Campaign(
        name=name,
        description=description,
        posting_interval=posting_interval
    )
    campaign.set_platforms(platforms)
    
    db.session.add(campaign)
    db.session.commit()
    
    return {'success': True, 'campaign_id': campaign.id}, 201

@campaigns_bp.route('/api/campaigns/<int:campaign_id>/posts', methods=['POST'])
def add_to_campaign(campaign_id):
    """Add post to campaign"""
    campaign = Campaign.query.get(campaign_id)
    
    if not campaign:
        return {'error': 'Campaign not found'}, 404
    
    content = request.get_json().get('content')
    selected_pages = request.get_json().get('selected_pages', [])
    
    if not content:
        return {'error': 'Content required'}, 400
    
    post = Post(
        campaign_id=campaign_id,
        content=content,
        status='draft'
    )
    post.set_platforms(campaign.get_platforms())
    if selected_pages:
        post.set_selected_pages(selected_pages)
    
    db.session.add(post)
    db.session.commit()
    
    return {'success': True, 'post_id': post.id}, 201

@campaigns_bp.route('/api/campaigns/<int:campaign_id>/schedule', methods=['POST'])
def schedule_campaign(campaign_id):
    """Schedule a campaign for posting"""
    campaign = Campaign.query.get(campaign_id)
    
    if not campaign:
        return {'error': 'Campaign not found'}, 404
    
    scheduled_at_str = request.get_json().get('scheduled_at')
    if not scheduled_at_str:
        return {'error': 'Schedule time required'}, 400
    
    try:
        scheduled_at = datetime.fromisoformat(scheduled_at_str)
    except:
        return {'error': 'Invalid datetime format'}, 400
    
    # Get all draft posts in the campaign
    draft_posts = Post.query.filter_by(
        campaign_id=campaign_id,
        status='draft'
    ).all()
    
    if not draft_posts:
        return {'error': 'No draft posts in campaign'}, 400
    
    # Schedule posts with intervals
    current_time = scheduled_at
    interval_minutes = campaign.posting_interval
    
    for post in draft_posts:
        post.status = 'pending'
        post.scheduled_at = current_time
        
        # If Facebook is in platforms and post has selected pages, update platforms to only include Facebook
        # and store selected pages for the posting service
        if 'facebook' in post.get_platforms() and post.get_selected_pages():
            # Keep all platforms but the Facebook service will use selected pages
            pass
        
        # Move to next interval
        if interval_minutes > 0:
            current_time = current_time.replace(minute=current_time.minute + interval_minutes)
    
    db.session.commit()
    
    return {'success': True, 'scheduled_posts': len(draft_posts)}, 200
