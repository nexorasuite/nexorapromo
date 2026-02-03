import threading
import time
from datetime import datetime
from flask import current_app
from database import db, Post
from services.factory import PostingServiceFactory
import json

class PostScheduler:
    """Background scheduler for scheduled posts using threading"""
    
    def __init__(self, app=None):
        self.app = app
        self.running = False
        self.thread = None
        self.check_interval = 30  # Check every 30 seconds
    
    def init_app(self, app):
        """Initialize scheduler with Flask app"""
        self.app = app
        self.check_interval = app.config.get('SCHEDULER_CHECK_INTERVAL', 30)
    
    def start(self):
        """Start the scheduler thread"""
        if self.running:
            return
        
        if not self.app:
            raise RuntimeError("Scheduler not initialized with app")
        
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        print("✓ Post scheduler started")
    
    def stop(self):
        """Stop the scheduler thread"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        print("✓ Post scheduler stopped")
    
    def _run(self):
        """Main scheduler loop"""
        while self.running:
            try:
                with self.app.app_context():
                    self._check_and_post()
            except Exception as e:
                print(f"✗ Scheduler error: {e}")
            
            # Sleep before next check
            time.sleep(self.check_interval)
    
    def _check_and_post(self):
        """Check for scheduled posts that should be posted now"""
        now = datetime.utcnow()
        
        # Find posts scheduled for posting
        pending_posts = Post.query.filter(
            Post.status == 'pending',
            Post.scheduled_at <= now
        ).all()
        
        for post in pending_posts:
            self._post_content(post)
    
    def _post_content(self, post):
        """Post content to all selected platforms"""
        try:
            results = {}
            platforms = post.get_platforms()
            
            for platform in platforms:
                try:
                    service = PostingServiceFactory.get_service(platform)
                    
                    # Post based on content type
                    if post.image_path:
                        success = service.post_image(
                            caption=post.content,
                            image_path=post.image_path,
                            user_id=post.user_id
                        )
                    else:
                        success = service.post_text(
                            content=post.content,
                            user_id=post.user_id
                        )
                    
                    results[platform] = {
                        'status': 'success' if success else 'failed',
                        'posted_at': datetime.utcnow().isoformat(),
                        'message': 'Posted successfully' if success else 'Posting failed'
                    }
                    
                except Exception as e:
                    results[platform] = {
                        'status': 'failed',
                        'error': str(e)
                    }
            
            # Update post status
            post.status = 'posted'
            post.posted_at = datetime.utcnow()
            post.set_post_results(results)
            db.session.commit()
            
            print(f"✓ Posted content (ID: {post.id})")
            
        except Exception as e:
            print(f"✗ Error posting content (ID: {post.id}): {e}")
            post.status = 'failed'
            db.session.commit()

# Global scheduler instance
scheduler = PostScheduler()

def init_scheduler(app):
    """Initialize and start scheduler"""
    scheduler.init_app(app)
    scheduler.start()
