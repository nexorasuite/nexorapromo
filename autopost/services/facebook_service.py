from services.base import BasePostingService
import os
import requests
import json

class FacebookService(BasePostingService):
    """Facebook posting service - supports multiple pages"""
    
    def __init__(self):
        super().__init__('facebook')
        self.api_version = 'v18.0'
        self.base_url = f'https://graph.facebook.com/{self.api_version}'
    
    def _get_pages(self, user_id):
        """Get all pages and their tokens"""
        cred = self._get_credentials(user_id)
        if not cred or not cred.is_active:
            return {}
        
        # Pages stored as JSON in api_key field
        try:
            pages = json.loads(cred.api_key) if cred.api_key else {}
            return pages
        except:
            return {}
    
    def authenticate(self, user_id, credentials=None):
        """
        Authenticate with Facebook
        Verifies at least one page token is valid
        """
        pages = self._get_pages(user_id)
        if not pages:
            return False
        
        try:
            # Test with first page
            first_page_id = list(pages.keys())[0]
            first_page_token = pages[first_page_id]['token']
            
            response = requests.get(
                f'{self.base_url}/{first_page_id}',
                params={'access_token': first_page_token},
                timeout=5
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Facebook auth error: {e}")
            return False
    
    def post_text(self, content, user_id, **kwargs):
        """
        Post text content to all connected Facebook pages
        """
        pages = self._get_pages(user_id)
        if not pages:
            print(f"[Facebook] Error: No pages configured")
            return False
        
        results = {}
        success_count = 0
        
        for page_id, page_info in pages.items():
            try:
                page_name = page_info.get('name', 'Unknown')
                page_token = page_info.get('token')
                
                if not page_token:
                    results[page_id] = {'success': False, 'error': 'No token'}
                    continue
                
                # Post to page feed
                url = f'{self.base_url}/{page_id}/feed'
                payload = {
                    'message': content,
                    'access_token': page_token
                }
                
                response = requests.post(url, data=payload, timeout=10)
                response_data = response.json()
                
                if response.status_code == 200 and 'id' in response_data:
                    post_id = response_data['id']
                    print(f"[Facebook] ✅ {page_name} - Posted (ID: {post_id})")
                    results[page_id] = {'success': True, 'post_id': post_id}
                    success_count += 1
                else:
                    error_msg = response_data.get('error', {}).get('message', 'Unknown error')
                    print(f"[Facebook] ❌ {page_name} - Failed: {error_msg}")
                    results[page_id] = {'success': False, 'error': error_msg}
            
            except Exception as e:
                print(f"[Facebook] Error posting to {page_id}: {e}")
                results[page_id] = {'success': False, 'error': str(e)}
        
        # Return True if at least one post succeeded
        return success_count > 0
    
    def post_image(self, caption, image_path, user_id, **kwargs):
        """
        Post image with caption to all connected Facebook pages
        """
        if not os.path.exists(image_path):
            print(f"[Facebook] Error: Image file not found: {image_path}")
            return False
        
        pages = self._get_pages(user_id)
        if not pages:
            print(f"[Facebook] Error: No pages configured")
            return False
        
        results = {}
        success_count = 0
        
        for page_id, page_info in pages.items():
            try:
                page_name = page_info.get('name', 'Unknown')
                page_token = page_info.get('token')
                
                if not page_token:
                    results[page_id] = {'success': False, 'error': 'No token'}
                    continue
                
                # Prepare image upload
                url = f'{self.base_url}/{page_id}/photos'
                
                with open(image_path, 'rb') as img_file:
                    files = {'source': img_file}
                    payload = {
                        'caption': caption,
                        'access_token': page_token
                    }
                    
                    response = requests.post(url, files=files, data=payload, timeout=30)
                    response_data = response.json()
                
                if response.status_code == 200 and 'id' in response_data:
                    photo_id = response_data['id']
                    print(f"[Facebook] ✅ {page_name} - Image posted (ID: {photo_id})")
                    results[page_id] = {'success': True, 'photo_id': photo_id}
                    success_count += 1
                else:
                    error_msg = response_data.get('error', {}).get('message', 'Unknown error')
                    print(f"[Facebook] ❌ {page_name} - Image failed: {error_msg}")
                    results[page_id] = {'success': False, 'error': error_msg}
            
            except Exception as e:
                print(f"[Facebook] Error posting image to {page_id}: {e}")
                results[page_id] = {'success': False, 'error': str(e)}
        
        # Return True if at least one post succeeded
        return success_count > 0
    
    def get_status(self, user_id):
        """Get connection status for all pages"""
        pages = self._get_pages(user_id)
        if not pages:
            return {'connected': False, 'platform': 'facebook', 'pages': 0}
        
        is_auth = self.authenticate(user_id)
        return {
            'connected': is_auth,
            'platform': 'facebook',
            'pages': len(pages),
            'page_names': [p.get('name', 'Unknown') for p in pages.values()]
        }
