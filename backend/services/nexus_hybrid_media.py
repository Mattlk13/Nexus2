"""
NEXUS Hybrid Media Generation Service
Combines image, video, and audio generation with intelligent provider selection

Features:
- Image: Gemini Nano Banana, Fal.ai, fallbacks
- Video: Sora 2, Runway, fallbacks  
- Audio: ElevenLabs, OpenAI TTS, fallbacks
- Smart provider selection
- Automatic failover
"""

import os
import logging
from typing import Optional, Dict, List
import time
import httpx

logger = logging.getLogger(__name__)

class HybridMediaService:
    def __init__(self):
        """Initialize all media generation providers"""
        self.emergent_key = os.environ.get('EMERGENT_LLM_KEY')
        self.elevenlabs_key = os.environ.get('ELEVENLABS_API_KEY')
        self.fal_key = os.environ.get('FAL_KEY')
        
        self.providers = {
            "image": {
                "nano_banana": {"available": bool(self.emergent_key), "priority": 1, "cost": "low"},
                "fal_ai": {"available": bool(self.fal_key), "priority": 2, "cost": "medium"}
            },
            "video": {
                "sora_2": {"available": bool(self.emergent_key), "priority": 1, "cost": "high"},
                "runway": {"available": False, "priority": 2, "cost": "high"}
            },
            "audio": {
                "elevenlabs": {"available": bool(self.elevenlabs_key), "priority": 1, "cost": "low"},
                "openai_tts": {"available": bool(self.emergent_key), "priority": 2, "cost": "low"}
            }
        }
        
        logger.info("Hybrid Media Service initialized")
    
    async def generate_image(
        self,
        prompt: str,
        size: str = "1024x1024",
        style: str = "vivid",
        provider: Optional[str] = None
    ) -> Dict:
        """Generate image with best available provider"""
        
        # Nano Banana (via Emergent LLM Key)
        if (provider == "nano_banana" or not provider) and self.emergent_key:
            try:
                from emergentintegrations.image_generation import ImageGeneration
                
                start = time.time()
                image_gen = ImageGeneration(api_key=self.emergent_key)
                
                result = image_gen.generate(
                    prompt=prompt,
                    model="google",
                    model_name="gemini-nano-banana-2",
                    size=size,
                    output_format="url"
                )
                
                return {
                    "success": True,
                    "image_url": result.get("url"),
                    "provider": "nano_banana",
                    "model": "gemini-nano-banana-2",
                    "elapsed": round(time.time() - start, 2)
                }
            except Exception as e:
                logger.error(f"Nano Banana failed: {e}")
                if provider == "nano_banana":  # User specifically requested this
                    return {"success": False, "error": str(e)}
        
        # Fal.ai fallback
        if self.fal_key:
            try:
                from services.fal_ai_service import fal_ai_service
                
                result = await fal_ai_service.generate_image(
                    prompt=prompt,
                    model="fal-ai/flux-pro",
                    size=size
                )
                
                if result["success"]:
                    result["provider"] = "fal_ai"
                    return result
            except Exception as e:
                logger.error(f"Fal.ai failed: {e}")
        
        return {
            "success": False,
            "error": "No image generation providers available"
        }
    
    async def generate_video(
        self,
        prompt: str,
        duration: int = 5,
        size: str = "1280x720",
        provider: Optional[str] = None
    ) -> Dict:
        """Generate video with best available provider"""
        
        # Sora 2 (via Emergent LLM Key)
        if (provider == "sora_2" or not provider) and self.emergent_key:
            try:
                from services.text_to_video_service import text_to_video_service
                
                result = await text_to_video_service.generate_video(
                    prompt=prompt,
                    model="sora-2",
                    duration=duration,
                    size=size,
                    output_filename=f"video_{int(time.time())}"
                )
                
                if result["success"]:
                    result["provider"] = "sora_2"
                    return result
            except Exception as e:
                logger.error(f"Sora 2 failed: {e}")
                if provider == "sora_2":
                    return {"success": False, "error": str(e)}
        
        # Runway fallback (if available)
        if self.providers["video"]["runway"]["available"]:
            try:
                from services.runway_video_service import runway_video_service
                
                result = await runway_video_service.generate_video(
                    prompt=prompt,
                    duration=duration
                )
                
                if result["success"]:
                    result["provider"] = "runway"
                    return result
            except Exception as e:
                logger.error(f"Runway failed: {e}")
        
        return {
            "success": False,
            "error": "No video generation providers available"
        }
    
    async def generate_audio(
        self,
        text: str,
        voice: str = "alloy",
        provider: Optional[str] = None
    ) -> Dict:
        """Generate audio/TTS with best available provider"""
        
        # ElevenLabs (highest quality)
        if (provider == "elevenlabs" or not provider) and self.elevenlabs_key:
            try:
                from services.elevenlabs_service import elevenlabs_service
                
                result = await elevenlabs_service.text_to_speech(
                    text=text,
                    voice_id=voice
                )
                
                if result["success"]:
                    result["provider"] = "elevenlabs"
                    return result
            except Exception as e:
                logger.error(f"ElevenLabs failed: {e}")
                if provider == "elevenlabs":
                    return {"success": False, "error": str(e)}
        
        # OpenAI TTS fallback
        if self.emergent_key:
            try:
                # Use OpenAI TTS via Emergent Key
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        "https://api.openai.com/v1/audio/speech",
                        headers={
                            "Authorization": f"Bearer {self.emergent_key}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "model": "tts-1",
                            "input": text,
                            "voice": voice
                        },
                        timeout=60.0
                    )
                    
                    if response.status_code == 200:
                        audio_data = response.content
                        return {
                            "success": True,
                            "audio_data": audio_data,
                            "provider": "openai_tts",
                            "format": "mp3"
                        }
            except Exception as e:
                logger.error(f"OpenAI TTS failed: {e}")
        
        return {
            "success": False,
            "error": "No audio generation providers available"
        }
    
    async def get_available_providers(self) -> Dict:
        """Get status of all providers"""
        return {
            "image": {k: v["available"] for k, v in self.providers["image"].items()},
            "video": {k: v["available"] for k, v in self.providers["video"].items()},
            "audio": {k: v["available"] for k, v in self.providers["audio"].items()}
        }

# Global instance
hybrid_media = HybridMediaService()
