"""
Cloudflare Images Service
Optimized image delivery with automatic WebP/AVIF conversion
"""

import os
import logging
import httpx
from typing import Optional

logger = logging.getLogger(__name__)

class CloudflareImagesService:
    def __init__(self):
        """Initialize Cloudflare Images client"""
        self.account_id = os.environ.get('CLOUDFLARE_ACCOUNT_ID')
        self.api_token = os.environ.get('CLOUDFLARE_IMAGES_TOKEN')
        self.account_hash = os.environ.get('CLOUDFLARE_ACCOUNT_HASH')
        
        if not all([self.account_id, self.api_token, self.account_hash]):
            logger.warning("Cloudflare Images not configured")
            self.enabled = False
            return
        
        self.base_url = f"https://api.cloudflare.com/client/v4/accounts/{self.account_id}/images/v1"
        self.delivery_url = f"https://imagedelivery.net/{self.account_hash}"
        self.enabled = True
        
        logger.info("Cloudflare Images initialized")
    
    async def upload_image(self, image_data: bytes, filename: str, metadata: dict = None) -> dict:
        """
        Upload image to Cloudflare Images
        
        Returns optimized image variants
        """
        if not self.enabled:
            return {"success": False, "error": "Cloudflare Images not configured"}
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.base_url,
                    headers={
                        'Authorization': f'Bearer {self.api_token}'
                    },
                    files={
                        'file': (filename, image_data)
                    },
                    data={
                        'metadata': str(metadata) if metadata else None,
                        'requireSignedURLs': 'false'  # Public images
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    image_id = result['result']['id']
                    
                    return {
                        "success": True,
                        "image_id": image_id,
                        "variants": {
                            "public": f"{self.delivery_url}/{image_id}/public",
                            "thumbnail": f"{self.delivery_url}/{image_id}/thumbnail",
                            "medium": f"{self.delivery_url}/{image_id}/medium",
                            "large": f"{self.delivery_url}/{image_id}/large"
                        },
                        "uploaded_at": result['result']['uploaded']
                    }
                else:
                    logger.error(f"Cloudflare Images upload failed: {response.text}")
                    return {
                        "success": False,
                        "error": response.text
                    }
                    
        except Exception as e:
            logger.error(f"Failed to upload to Cloudflare Images: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def delete_image(self, image_id: str) -> bool:
        """Delete image from Cloudflare Images"""
        if not self.enabled:
            return False
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.delete(
                    f"{self.base_url}/{image_id}",
                    headers={
                        'Authorization': f'Bearer {self.api_token}'
                    }
                )
                
                return response.status_code == 200
                
        except Exception as e:
            logger.error(f"Failed to delete image: {e}")
            return False
    
    def get_image_url(self, image_id: str, variant: str = 'public') -> str:
        """Get optimized image URL"""
        if not self.enabled:
            return ""
        
        return f"{self.delivery_url}/{image_id}/{variant}"
    
    def get_responsive_srcset(self, image_id: str) -> dict:
        """Generate responsive image srcset"""
        if not self.enabled:
            return {}
        
        return {
            "srcset": f"{self.get_image_url(image_id, 'thumbnail')} 320w, "
                     f"{self.get_image_url(image_id, 'medium')} 640w, "
                     f"{self.get_image_url(image_id, 'large')} 1280w",
            "src": self.get_image_url(image_id, 'public'),
            "sizes": "(max-width: 320px) 320px, (max-width: 640px) 640px, 1280px"
        }

# Global instance
cloudflare_images = CloudflareImagesService()
