import os
import logging
import fal_client
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from pathlib import Path
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).parent.parent
load_dotenv(ROOT_DIR / '.env')

logger = logging.getLogger(__name__)

# Set FAL_KEY in environment for fal_client
FAL_KEY = os.environ.get('FAL_KEY', '')
if FAL_KEY and 'demo' not in FAL_KEY.lower():
    os.environ['FAL_KEY'] = FAL_KEY

class FalAIService:
    """Service for fal.ai fast AI image generation"""
    
    def __init__(self):
        self.api_key = FAL_KEY
        self.is_active = self._check_active()
        
        if self.is_active:
            logger.info("✓ fal.ai client ready")
        else:
            logger.warning("⚠ fal.ai API key not configured - service in demo mode")
    
    def _check_active(self) -> bool:
        """Check if fal.ai is properly configured"""
        if not self.api_key:
            return False
        placeholder_terms = ['demo', 'placeholder', 'your_key']
        return not any(term in self.api_key.lower() for term in placeholder_terms)
    
    async def generate_image(
        self,
        prompt: str,
        model: str = "fal-ai/flux/dev",
        image_size: str = "landscape_4_3",
        num_images: int = 1,
        enable_safety_checker: bool = True
    ) -> Dict[str, Any]:
        """Generate image using fal.ai FLUX model"""
        
        if not self.is_active:
            logger.warning("fal.ai not configured - returning mock response")
            return {
                "success": False,
                "images": [],
                "mocked": True,
                "message": "fal.ai API key required. Get from: https://fal.ai/dashboard/keys"
            }
        
        try:
            # Submit async job to fal.ai
            handler = await fal_client.submit_async(
                model,
                arguments={
                    "prompt": prompt,
                    "image_size": image_size,
                    "num_images": num_images,
                    "enable_safety_checker": enable_safety_checker
                }
            )
            
            # Wait for result
            result = await handler.get()
            
            # Extract image URLs
            images = []
            if hasattr(result, 'images') and result.images:
                for img in result.images:
                    images.append({
                        "url": img.url if hasattr(img, 'url') else str(img),
                        "width": img.width if hasattr(img, 'width') else None,
                        "height": img.height if hasattr(img, 'height') else None,
                        "content_type": img.content_type if hasattr(img, 'content_type') else "image/jpeg"
                    })
            elif isinstance(result, dict) and 'images' in result:
                images = result['images']
            
            logger.info(f"✓ fal.ai generated {len(images)} images for prompt: {prompt[:50]}...")
            
            return {
                "success": True,
                "images": images,
                "prompt": prompt,
                "model": model,
                "mocked": False,
                "generated_at": datetime.now(timezone.utc).isoformat()
            }
        
        except Exception as e:
            logger.error(f"fal.ai generation error: {e}")
            return {
                "success": False,
                "error": str(e),
                "mocked": False
            }
    
    async def generate_image_fast(self, prompt: str) -> Dict[str, Any]:
        """Fast image generation using fal.ai FLUX-schnell model"""
        return await self.generate_image(
            prompt=prompt,
            model="fal-ai/flux/schnell",  # Faster model
            image_size="square_hd",
            num_images=1
        )
    
    async def generate_image_pro(self, prompt: str) -> Dict[str, Any]:
        """High-quality image generation using fal.ai FLUX-pro model"""
        return await self.generate_image(
            prompt=prompt,
            model="fal-ai/flux-pro",  # Best quality
            image_size="landscape_16_9",
            num_images=1
        )

fal_ai_service = FalAIService()
