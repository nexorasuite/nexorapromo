from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class Post(db.Model):
    """Post model"""
    __tablename__ = 'posts'
    
    id = db.Column(db.Integer, primary_key=True)
    
    content = db.Column(db.Text, nullable=False)
    image_path = db.Column(db.String(255))
    
    # Platform targeting
    platforms = db.Column(db.String(255))  # JSON array: '["linkedin","facebook"]'
    selected_pages = db.Column(db.String(500))  # JSON array of Facebook page IDs for this post
    
    # Status
    status = db.Column(db.String(20), default='draft')  # draft, pending, posted, failed
    
    # Scheduling
    scheduled_at = db.Column(db.DateTime)  # UTC
    posted_at = db.Column(db.DateTime)
    
    # Campaign
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'))
    campaign = db.relationship('Campaign', backref='posts')
    
    # Posting results
    post_results = db.Column(db.Text)  # JSON with per-platform results
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_platforms(self):
        if not self.platforms:
            return []
        return json.loads(self.platforms)
    
    def set_platforms(self, platforms):
        self.platforms = json.dumps(platforms)
    
    def get_selected_pages(self):
        if not self.selected_pages:
            return []
        return json.loads(self.selected_pages)
    
    def set_selected_pages(self, pages):
        self.selected_pages = json.dumps(pages)
    
    def get_post_results(self):
        if not self.post_results:
            return {}
        return json.loads(self.post_results)
    
    def set_post_results(self, results):
        self.post_results = json.dumps(results)
    
    def __repr__(self):
        return f'<Post {self.id}>'

class PostTemplate(db.Model):
    """Post template model"""
    __tablename__ = 'post_templates'
    
    id = db.Column(db.Integer, primary_key=True)
    
    name = db.Column(db.String(120), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image_path = db.Column(db.String(255))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<PostTemplate {self.name}>'

class HashtagSet(db.Model):
    """Hashtag set model"""
    __tablename__ = 'hashtag_sets'
    
    id = db.Column(db.Integer, primary_key=True)
    
    name = db.Column(db.String(120), nullable=False)
    hashtags = db.Column(db.Text, nullable=False)  # Newline-separated hashtags
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def get_hashtags(self):
        if not self.hashtags:
            return []
        return [tag.strip() for tag in self.hashtags.split('\n') if tag.strip()]
    
    def set_hashtags(self, hashtags):
        if isinstance(hashtags, list):
            self.hashtags = '\n'.join(hashtags)
        else:
            self.hashtags = hashtags
    
    def __repr__(self):
        return f'<HashtagSet {self.name}>'

class Campaign(db.Model):
    """Campaign model for multi-platform posting"""
    __tablename__ = 'campaign'
    
    id = db.Column(db.Integer, primary_key=True)
    
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    
    # Platforms
    platforms = db.Column(db.String(255))  # JSON array
    
    # Posting interval in minutes (0 = post all at once)
    posting_interval = db.Column(db.Integer, default=0)
    
    status = db.Column(db.String(20), default='active')  # active, completed, cancelled
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_platforms(self):
        if not self.platforms:
            return []
        return json.loads(self.platforms)
    
    def set_platforms(self, platforms):
        self.platforms = json.dumps(platforms)
    
    def __repr__(self):
        return f'<Campaign {self.name}>'

class PlatformCredential(db.Model):
    """Platform API credentials"""
    __tablename__ = 'platform_credentials'
    
    id = db.Column(db.Integer, primary_key=True)
    
    platform = db.Column(db.String(50), nullable=False)  # linkedin, facebook, instagram, telegram, twitter
    
    # Encrypted credentials (use proper encryption in production)
    api_key = db.Column(db.String(500))
    api_secret = db.Column(db.String(500))
    access_token = db.Column(db.String(500))
    refresh_token = db.Column(db.String(500))
    username = db.Column(db.String(255))
    password = db.Column(db.String(500))
    
    is_active = db.Column(db.Boolean, default=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<PlatformCredential {self.platform}>'

def init_db(app, force=False):
    """Initialize database"""
    with app.app_context():
        if force:
            db.drop_all()
        
        db.create_all()
        
        print("✓ Database initialized successfully")
