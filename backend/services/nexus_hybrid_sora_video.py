"""
NEXUS Hybrid: Sora 2 Video Generation
OpenAI Sora 2 API integration for AI video generation
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Dict, List
import os
import base64
from dotenv import load_dotenv
from emergentintegrations.llm.openai.video_generation import OpenAIVideoGeneration
import logging

load_dotenv()
logger = logging.getLogger(__name__)

class VideoRequest(BaseModel):
    prompt: str
    model: str = "sora-2"
    size: str = "1280x720"
    duration: int = 4

class SoraVideoEngine:
    def __init__(self, db):
        self.db = db
        self.api_key = os.getenv('EMERGENT_LLM_KEY')
        if not self.api_key:
            raise ValueError("EMERGENT_LLM_KEY not found in environment")
    
    def get_capabilities(self) -> Dict:
        return {
            "name": "Sora 2 Video Generation",
            "description": "OpenAI Sora 2 - Generate cinematic AI videos from text",
            "category": "video_generation",
            "provider": "OpenAI",
            "models": ["sora-2", "sora-2-pro"],
            "max_duration": "60 seconds",
            "resolutions": ["1280x720", "1792x1024", "1024x1792", "1024x1024"],
            "durations": [4, 8, 12],
            "features": [
                "Text-to-video generation",
                "Cinematic quality",
                "Physics-accurate motion",
                "Character consistency",
                "Audio sync support"
            ],
            "pricing": "$0.10/second (via Emergent LLM Key)",
            "status": "active"
        }
    
    async def generate_video(self, request: VideoRequest) -> Dict:
        """Generate video with Sora 2"""
        try:
            video_gen = OpenAIVideoGeneration(api_key=self.api_key)
            
            video_bytes = video_gen.text_to_video(
                prompt=request.prompt,
                model=request.model,
                size=request.size,
                duration=request.duration,
                max_wait_time=600
            )
            
            if not video_bytes:
                raise HTTPException(status_code=500, detail="Video generation failed")
            
            # Convert to base64 for transfer
            video_base64 = base64.b64encode(video_bytes).decode('utf-8')
            
            return {
                "success": True,
                "video_base64": video_base64,
                "format": "mp4",
                "model": request.model,
                "size": request.size,
                "duration": request.duration
            }
        except Exception as e:
            logger.error(f"Sora video generation error: {e}")
            raise HTTPException(status_code=500, detail=str(e))

def create_sora_video_engine(db):
    return SoraVideoEngine(db)

# Create global instance for ultimate controller
hybrid_sora_video = None
def init_hybrid(db):
    global hybrid_sora_video
    hybrid_sora_video = create_sora_video_engine(db)
    return hybrid_sora_video

def register_routes(db, get_current_user, require_admin):
    router = APIRouter(tags=["Sora Video"])
    engine = create_sora_video_engine(db)
    
    @router.get("/capabilities")
    async def get_capabilities():
        return engine.get_capabilities()
    
    @router.post("/generate")
    async def generate_video(request: VideoRequest):
        return await engine.generate_video(request)
    
    return router
