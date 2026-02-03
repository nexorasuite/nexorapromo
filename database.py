from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import json

db = SQLAlchemy()

class User(db.Model):
    """Admin user model"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(120), unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    posts = db.relationship('Post', backref='user', lazy=True, cascade='all, delete-orphan')
    templates = db.relationship('PostTemplate', backref='user', lazy=True, cascade='all, delete-orphan')
    hashtag_sets = db.relationship('HashtagSet', backref='user', lazy=True, cascade='all, delete-orphan')
    credentials = db.relationship('PlatformCredential', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Post(db.Model):
    """Post model"""
    __tablename__ = 'posts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    content = db.Column(db.Text, nullable=False)
    image_path = db.Column(db.String(255))
    
    # Platform targeting
    platforms = db.Column(db.String(255))  # JSON array: '["linkedin","facebook"]'
    
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
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    name = db.Column(db.String(120), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image_path = db.Column(db.String(255))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'name', name='unique_user_template_name'),)
    
    def __repr__(self):
        return f'<PostTemplate {self.name}>'

class HashtagSet(db.Model):
    """Hashtag set model"""
    __tablename__ = 'hashtag_sets'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    name = db.Column(db.String(120), nullable=False)
    hashtags = db.Column(db.Text, nullable=False)  # Newline-separated hashtags
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'name', name='unique_user_hashtag_set_name'),)
    
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
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    
    # Platforms
    platforms = db.Column(db.String(255))  # JSON array
    
    status = db.Column(db.String(20), default='active')  # active, completed, cancelled
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = db.relationship('User', backref='campaigns')
    
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
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
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
    
    __table_args__ = (db.UniqueConstraint('user_id', 'platform', name='unique_user_platform_cred'),)
    
    def __repr__(self):
        return f'<PlatformCredential {self.platform}>'

def init_db(app, force=False):
    """Initialize database and create default admin user"""
    with app.app_context():
        if force:
            db.drop_all()
        
        db.create_all()
        
        # Create default admin user if doesn't exist
        from config import config
        admin = User.query.filter_by(username=config.DEFAULT_ADMIN_USERNAME).first()
        if not admin:
            admin = User(
                username=config.DEFAULT_ADMIN_USERNAME,
                email='admin@autopost.local'
            )
            admin.set_password(config.DEFAULT_ADMIN_PASSWORD)
            db.session.add(admin)
            db.session.commit()
            print(f"✓ Created default admin user: {config.DEFAULT_ADMIN_USERNAME}")
        
        print("✓ Database initialized successfully")
