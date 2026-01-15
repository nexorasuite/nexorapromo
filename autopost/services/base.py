from abc import ABC, abstractmethod

class BasePostingService(ABC):
    """Abstract base class for platform posting services"""
    
    def __init__(self, platform_name):
        self.platform_name = platform_name
    
    @abstractmethod
    def authenticate(self, user_id, credentials=None):
        """
        Authenticate with the platform
        
        Args:
            user_id: ID of the user
            credentials: Dictionary with auth credentials
        
        Returns:
            bool: True if authenticated
        """
        pass
    
    @abstractmethod
    def post_text(self, content, user_id, **kwargs):
        """
        Post text content to the platform
        
        Args:
            content: Text content to post
            user_id: ID of the user
            **kwargs: Additional arguments
        
        Returns:
            bool: True if posted successfully
        """
        pass
    
    @abstractmethod
    def post_image(self, caption, image_path, user_id, **kwargs):
        """
        Post image with caption to the platform
        
        Args:
            caption: Text caption for the image
            image_path: Path to the image file
            user_id: ID of the user
            **kwargs: Additional arguments
        
        Returns:
            bool: True if posted successfully
        """
        pass
    
    @abstractmethod
    def get_status(self, user_id):
        """
        Get connection status with the platform
        
        Args:
            user_id: ID of the user
        
        Returns:
            dict: Status information
        """
        pass
    
    def _get_credentials(self, user_id):
        """Get platform credentials from database"""
        from database import PlatformCredential
        cred = PlatformCredential.query.filter_by(
            user_id=user_id,
            platform=self.platform_name
        ).first()
        return cred
