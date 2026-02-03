from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify
from database import db, User, PlatformCredential
from services.factory import PostingServiceFactory

settings_bp = Blueprint('settings', __name__)

@settings_bp.route('/settings')
def index():
    """Settings page"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    user_id = session['user_id']
    user = User.query.get(user_id)
    
    platforms = PostingServiceFactory.get_platform_config()
    credentials = PlatformCredential.query.filter_by(user_id=user_id).all()
    
    cred_map = {c.platform: c for c in credentials}
    
    return render_template('settings.html', user=user, platforms=platforms, credentials=cred_map)

@settings_bp.route('/api/platforms/status', methods=['GET'])
def platform_status():
    """Get platform connection status"""
    if 'user_id' not in session:
        return {'error': 'Unauthorized'}, 401
    
    user_id = session['user_id']
    statuses = {}
    
    for platform in PostingServiceFactory.get_all_platforms():
        try:
            service = PostingServiceFactory.get_service(platform)
            statuses[platform] = service.get_status(user_id)
        except Exception as e:
            statuses[platform] = {
                'connected': False,
                'platform': platform,
                'error': str(e)
            }
    
    return statuses

@settings_bp.route('/api/platforms/<platform>/credentials', methods=['POST', 'GET', 'DELETE'])
def manage_credentials(platform):
    """Manage platform credentials"""
    if 'user_id' not in session:
        return {'error': 'Unauthorized'}, 401
    
    user_id = session['user_id']
    
    if platform not in PostingServiceFactory.get_all_platforms():
        return {'error': 'Invalid platform'}, 400
    
    cred = PlatformCredential.query.filter_by(
        user_id=user_id,
        platform=platform
    ).first()
    
    if request.method == 'GET':
        if not cred:
            return {'error': 'No credentials found'}, 404
        
        return {
            'platform': cred.platform,
            'username': cred.username,
            'is_active': cred.is_active
        }
    
    elif request.method == 'DELETE':
        if cred:
            db.session.delete(cred)
            db.session.commit()
        return {'success': True}
    
    # POST - Create/update credentials
    data = request.get_json()
    
    if not cred:
        cred = PlatformCredential(
            user_id=user_id,
            platform=platform
        )
        db.session.add(cred)
    
    # Update credentials (store them securely in production)
    if 'api_key' in data:
        cred.api_key = data['api_key']
    if 'api_secret' in data:
        cred.api_secret = data['api_secret']
    if 'access_token' in data:
        cred.access_token = data['access_token']
    if 'username' in data:
        cred.username = data['username']
    if 'password' in data:
        cred.password = data['password']
    
    cred.is_active = data.get('is_active', True)
    
    db.session.commit()
    
    return {'success': True, 'platform': platform}
