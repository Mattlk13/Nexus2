"""
CloudStack Integration - Cloudflare Power Suite
Combines: Workers AI + Images + Stream + Optimization
"""
import logging
import os
from typing import Dict, Any, Optional, List
import httpx
from datetime import datetime
import base64

logger = logging.getLogger(__name__)

class CloudStackService:
    """Elite Cloudflare integration for all optimization needs"""
    
    def __init__(self):
        self.account_id = os.getenv('CLOUDFLARE_ACCOUNT_ID', '')
        self.api_token = os.getenv('CLOUDFLARE_API_TOKEN', '')
        self.r2_enabled = bool(os.getenv('R2_ENABLED', 'true'))
        self.workers_ai_enabled = True
        
        logger.info("CloudStack initialized with full Cloudflare suite")
    
    # ==================== WORKERS AI ====================
    
    async def classify_image(self, image_url: str) -> Dict[str, Any]:
        """Classify image using Cloudflare Workers AI ResNet-50"""
        try:
            async with httpx.AsyncClient() as client:
                headers = {
                    'Authorization': f'Bearer {self.api_token}',
                    'Content-Type': 'application/json'
                }
                
                payload = {'image': image_url}
                
                response = await client.post(
                    f'https://api.cloudflare.com/client/v4/accounts/{self.account_id}/ai/run/@cf/microsoft/resnet-50',
                    json=payload,
                    headers=headers
                )
                response.raise_for_status()
                
                return {
                    'success': True,
                    'classifications': response.json()['result']
                }
        except Exception as e:
            logger.error(f"Image classification failed: {e}")
            return {'success': False, 'error': str(e)}
    
    async def generate_image_from_text(
        self,
        prompt: str,
        model: str = '@cf/stabilityai/stable-diffusion-xl-base-1.0'
    ) -> Dict[str, Any]:
        """Generate image using Cloudflare Workers AI"""
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                headers = {
                    'Authorization': f'Bearer {self.api_token}',
                    'Content-Type': 'application/json'
                }
                
                payload = {'prompt': prompt}
                
                response = await client.post(
                    f'https://api.cloudflare.com/client/v4/accounts/{self.account_id}/ai/run/{model}',
                    json=payload,
                    headers=headers
                )
                response.raise_for_status()
                
                result = response.json()['result']
                
                # Image is returned as base64
                return {
                    'success': True,
                    'image_base64': result.get('image'),
                    'model': model,
                    'prompt': prompt
                }
        except Exception as e:
            logger.error(f"Image generation failed: {e}")
            return {'success': False, 'error': str(e)}
    
    async def describe_image(
        self,
        image_url: str,
        model: str = '@cf/unum/uform-gen2-qwen-500m'
    ) -> Dict[str, Any]:
        """Generate description for image using Workers AI"""
        try:
            async with httpx.AsyncClient() as client:
                headers = {
                    'Authorization': f'Bearer {self.api_token}',
                    'Content-Type': 'application/json'
                }
                
                payload = {'image': image_url}
                
                response = await client.post(
                    f'https://api.cloudflare.com/client/v4/accounts/{self.account_id}/ai/run/{model}',
                    json=payload,
                    headers=headers
                )
                response.raise_for_status()
                
                return {
                    'success': True,
                    'description': response.json()['result']['description']
                }
        except Exception as e:
            logger.error(f"Image description failed: {e}")
            return {'success': False, 'error': str(e)}
    
    # ==================== CLOUDFLARE IMAGES ====================
    
    async def optimize_image(
        self,
        image_url: str,
        width: Optional[int] = None,
        height: Optional[int] = None,
        quality: str = 'auto',
        format: str = 'auto'
    ) -> Dict[str, Any]:
        """Optimize image using Cloudflare Images"""
        try:
            # Cloudflare Images transformation
            params = []
            if width:
                params.append(f'width={width}')
            if height:
                params.append(f'height={height}')
            params.append(f'quality={quality}')
            params.append(f'format={format}')
            
            optimized_url = f"{image_url}?{','.join(params)}"
            
            return {
                'success': True,
                'original_url': image_url,
                'optimized_url': optimized_url,
                'transformations': params
            }
        except Exception as e:
            logger.error(f"Image optimization failed: {e}")
            return {'success': False, 'error': str(e)}
    
    async def smart_crop(
        self,
        image_url: str,
        width: int,
        height: int,
        gravity: str = 'auto'
    ) -> Dict[str, Any]:
        """Smart crop using AI-powered focal point detection"""
        try:
            # Cloudflare Images smart crop with face detection
            transformations = f'width={width},height={height},gravity={gravity}'
            optimized_url = f"{image_url}?{transformations}"
            
            return {
                'success': True,
                'cropped_url': optimized_url,
                'gravity': gravity  # auto, face, center
            }
        except Exception as e:
            logger.error(f"Smart crop failed: {e}")
            return {'success': False, 'error': str(e)}
    
    async def remove_background(
        self,
        image_url: str
    ) -> Dict[str, Any]:
        """Remove background using Cloudflare Workers AI segmentation"""
        try:
            # Use Workers AI BiRefNet model for background removal
            async with httpx.AsyncClient() as client:
                headers = {
                    'Authorization': f'Bearer {self.api_token}',
                    'Content-Type': 'application/json'
                }
                
                payload = {'image': image_url}
                
                response = await client.post(
                    f'https://api.cloudflare.com/client/v4/accounts/{self.account_id}/ai/run/@cf/segment',
                    json=payload,
                    headers=headers
                )
                response.raise_for_status()
                
                return {
                    'success': True,
                    'transparent_image': response.json()['result']['image']
                }
        except Exception as e:
            logger.error(f"Background removal failed: {e}")
            return {'success': False, 'error': str(e)}
    
    # ==================== CLOUDFLARE STREAM ====================
    
    async def upload_video(
        self,
        video_url: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Upload video to Cloudflare Stream"""
        try:
            async with httpx.AsyncClient() as client:
                headers = {
                    'Authorization': f'Bearer {self.api_token}',
                    'Content-Type': 'application/json'
                }
                
                payload = {
                    'url': video_url,
                    'meta': metadata or {}
                }
                
                response = await client.post(
                    f'https://api.cloudflare.com/client/v4/accounts/{self.account_id}/stream/copy',
                    json=payload,
                    headers=headers
                )
                response.raise_for_status()
                
                result = response.json()['result']
                
                return {
                    'success': True,
                    'video_id': result['uid'],
                    'stream_url': f"https://videodelivery.net/{result['uid']}/manifest/video.m3u8",
                    'thumbnail': result.get('thumbnail'),
                    'duration': result.get('duration')
                }
        except Exception as e:
            logger.error(f"Video upload failed: {e}")
            return {'success': False, 'error': str(e)}
    
    async def get_video_analytics(
        self,
        video_id: str
    ) -> Dict[str, Any]:
        """Get video analytics from Cloudflare Stream"""
        try:
            async with httpx.AsyncClient() as client:
                headers = {'Authorization': f'Bearer {self.api_token}'}
                
                response = await client.get(
                    f'https://api.cloudflare.com/client/v4/accounts/{self.account_id}/stream/{video_id}/analytics',
                    headers=headers
                )
                response.raise_for_status()
                
                return {
                    'success': True,
                    'analytics': response.json()['result']
                }
        except Exception as e:
            logger.error(f"Video analytics failed: {e}")
            return {'success': False, 'error': str(e)}
    
    # ==================== UNIFIED OPTIMIZATION ====================
    
    async def optimize_media(
        self,
        media_url: str,
        media_type: str,
        optimizations: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Unified media optimization for images, videos, and AI processing.
        
        This combines:
        - Cloudflare Images for image optimization
        - Cloudflare Stream for video hosting
        - Workers AI for AI-powered enhancements
        """
        if media_type == 'image':
            return await self.optimize_image(media_url, **optimizations)
        elif media_type == 'video':
            return await self.upload_video(media_url, optimizations.get('metadata'))
        else:
            return {'success': False, 'error': 'Unsupported media type'}
    
    def get_cdn_url(self, asset_path: str) -> str:
        """Get optimized CDN URL for any asset"""
        return f"https://cdn.nexus.ai/{asset_path}"

# Singleton instance
cloudstack = CloudStackService()
