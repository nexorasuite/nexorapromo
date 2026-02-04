from services.linkedin_service import LinkedInService
from services.facebook_service import FacebookService
from services.instagram_service import InstagramService
from services.telegram_service import TelegramService
from services.twitter_service import TwitterService

class PostingServiceFactory:
    """Factory for creating platform-specific posting services"""
    
    _services = {
        'linkedin': LinkedInService,
        'facebook': FacebookService,
        'instagram': InstagramService,
        'telegram': TelegramService,
        'twitter': TwitterService,
    }
    
    @classmethod
    def get_service(cls, platform):
        """
        Get a service instance for the given platform
        
        Args:
            platform: Platform name (linkedin, facebook, instagram, telegram, twitter)
        
        Returns:
            Service instance
        
        Raises:
            ValueError: If platform not supported
        """
        if platform not in cls._services:
            raise ValueError(f"Unsupported platform: {platform}")
        
        return cls._services[platform]()
    
    @classmethod
    def get_all_platforms(cls):
        """Get list of all supported platforms"""
        return list(cls._services.keys())
    
    @classmethod
    def get_platform_config(cls):
        """Get platform configurations with colors and icons"""
        return {
            'linkedin': {
                'name': 'LinkedIn',
                'color': '#0A66C2',
                'icon': 'linkedin',
                'enabled': True
            },
            'facebook': {
                'name': 'Facebook',
                'color': '#1877F2',
                'icon': 'facebook',
                'enabled': True
            },
            'instagram': {
                'name': 'Instagram',
                'color': '#E4405F',
                'icon': 'instagram',
                'enabled': True
            },
            'telegram': {
                'name': 'Telegram',
                'color': '#0088cc',
                'icon': 'send',
                'enabled': True
            },
            'twitter': {
                'name': 'Twitter/X',
                'color': '#000000',
                'icon': 'twitter',
                'enabled': True
            },
        }
