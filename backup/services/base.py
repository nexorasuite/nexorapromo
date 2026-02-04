from abc import ABC, abstractmethod

class BasePostingService(ABC):
    """Abstract base class for platform posting services"""
    
    def __init__(self, platform_name):
        self.platform_name = platform_name
    
    @abstractmethod
    def authenticate(self, credentials=None):
        """
        Authenticate with the platform
        
        Args:
            credentials: Dictionary with auth credentials
        
        Returns:
            bool: True if authenticated
        """
        pass
    
    @abstractmethod
    def post_text(self, content, **kwargs):
        """
        Post text content to the platform
        
        Args:
            content: Text content to post
            **kwargs: Additional arguments
        
        Returns:
            bool: True if posted successfully
        """
        pass
    
    @abstractmethod
    def post_image(self, caption, image_path, **kwargs):
        """
        Post image with caption to the platform
        
        Args:
            caption: Text caption for the image
            image_path: Path to the image file
            **kwargs: Additional arguments
        
        Returns:
            bool: True if posted successfully
        """
        pass
    
    @abstractmethod
    def get_status(self):
        """
        Get connection status with the platform
        
        Returns:
            dict: Status information
        """
        pass
    
    def _get_credentials(self):
        """Get platform credentials from database"""
        from database import PlatformCredential
        cred = PlatformCredential.query.filter_by(
            platform=self.platform_name
        ).first()
        return cred
