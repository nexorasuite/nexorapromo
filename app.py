from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta
from config import config
from database import db, init_db
from scheduler import init_scheduler
from routes.dashboard import dashboard_bp
from routes.composer import composer_bp
from routes.campaigns import campaigns_bp
from routes.history import history_bp
from routes.settings import settings_bp
import os

def create_app(config_obj=None):
    """Create and configure Flask application"""
    
    app = Flask(__name__, 
                template_folder='templates',
                static_folder='static',
                static_url_path='/static')
    
    # Load config
    if config_obj is None:
        config_obj = config
    app.config.from_object(config_obj)
    
    # Ensure upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Initialize extensions
    db.init_app(app)
    
    # Register blueprints
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(composer_bp)
    app.register_blueprint(campaigns_bp)
    app.register_blueprint(history_bp)
    app.register_blueprint(settings_bp)
    
    # Session configuration
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
    
    @app.before_request
    def make_session_permanent():
        session.permanent = True
    
    # Initialize database
    with app.app_context():
        init_db(app)
        
        # Start scheduler
        if app.config.get('SCHEDULER_ENABLED', True):
            init_scheduler(app)
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
