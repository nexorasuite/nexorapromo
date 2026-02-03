import os
import sys
from datetime import timedelta

# Get the directory where this config file is located
BASEDIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Paths
    INSTANCE_PATH = os.path.join(BASEDIR, 'instance')
    os.makedirs(INSTANCE_PATH, exist_ok=True)
    
    # Database - absolute path format for SQLite
    # For absolute paths on Unix: use sqlite:////absolute/path (4 slashes total)
    db_file_path = os.path.join(BASEDIR, "instance", "autopost.db")
    if db_file_path.startswith('/'):
        SQLALCHEMY_DATABASE_URI = 'sqlite:///' + db_file_path  # /path = sqlite:////path
    else:
        SQLALCHEMY_DATABASE_URI = f'sqlite:///{db_file_path}'  # relative path
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session configuration
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Upload configuration
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload
    UPLOAD_FOLDER = os.path.join(INSTANCE_PATH, 'uploads')
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    
    # Scheduler
    SCHEDULER_ENABLED = True
    SCHEDULER_CHECK_INTERVAL = 30  # seconds
    
    # Default admin user
    DEFAULT_ADMIN_USERNAME = 'admin'
    DEFAULT_ADMIN_PASSWORD = 'admin123'  # Change in production

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    SESSION_COOKIE_SECURE = True

class TermuxConfig(Config):
    """Termux-specific configuration"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:////data/data/com.termux/files/home/autopost/autopost.db'

# Set config based on environment
config_name = os.environ.get('FLASK_ENV', 'development')
if config_name == 'production':
    config = ProductionConfig()
elif config_name == 'termux':
    config = TermuxConfig()
else:
    config = DevelopmentConfig()
