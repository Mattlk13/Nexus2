"""
NEXUS Hybrid: GPT Image 1.5 Generation
OpenAI GPT Image 1.5 (DALL-E successor) integration
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, List
import os
import base64
from dotenv import load_dotenv
from emergentintegrations.llm.openai.image_generation import OpenAIImageGeneration
import logging

load_dotenv()
logger = logging.getLogger(__name__)

class ImageRequest(BaseModel):
    prompt: str
    model: str = "gpt-image-1"
    number_of_images: int = 1

class GPTImageEngine:
    def __init__(self, db):
        self.db = db
        self.api_key = os.getenv('EMERGENT_LLM_KEY')
        if not self.api_key:
            raise ValueError("EMERGENT_LLM_KEY not found in environment")
    
    def get_capabilities(self) -> Dict:
        return {
            "name": "GPT Image 1.5",
            "description": "OpenAI's latest image generation model (DALL-E 3 successor)",
            "category": "image_generation",
            "provider": "OpenAI",
            "models": ["gpt-image-1", "dall-e-3"],
            "features": [
                "High-quality image generation",
                "Complex prompt understanding",
                "Photorealistic output",
                "Text rendering in images",
                "Multiple aspect ratios"
            ],
            "pricing": "Via Emergent LLM Key",
            "status": "active",
            "note": "DALL-E 3 deprecated May 2026, use gpt-image-1"
        }
    
    async def generate_image(self, request: ImageRequest) -> Dict:
        """Generate image with GPT Image 1.5"""
        try:
            image_gen = OpenAIImageGeneration(api_key=self.api_key)
            
            images = await image_gen.generate_images(
                prompt=request.prompt,
                model=request.model,
                number_of_images=request.number_of_images
            )
            
            if not images or len(images) == 0:
                raise HTTPException(status_code=500, detail="No image generated")
            
            # Convert first image to base64
            image_base64 = base64.b64encode(images[0]).decode('utf-8')
            
            return {
                "success": True,
                "image_base64": image_base64,
                "model": request.model,
                "prompt": request.prompt
            }
        except Exception as e:
            logger.error(f"GPT Image generation error: {e}")
            raise HTTPException(status_code=500, detail=str(e))

def create_gpt_image_engine(db):
    return GPTImageEngine(db)

# Create global instance for ultimate controller
hybrid_gpt_image = None
def init_hybrid(db):
    global hybrid_gpt_image
    hybrid_gpt_image = create_gpt_image_engine(db)
    return hybrid_gpt_image

def register_routes(db, get_current_user, require_admin):
    router = APIRouter(tags=["GPT Image"])
    engine = create_gpt_image_engine(db)
    
    @router.get("/capabilities")
    async def get_capabilities():
        return engine.get_capabilities()
    
    @router.post("/generate")
    async def generate_image(request: ImageRequest):
        return await engine.generate_image(request)
    
    return router
