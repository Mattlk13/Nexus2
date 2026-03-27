"""
Creation Studio Routes - AI-powered content generation with REAL integrations
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, Optional
import logging
import os
from datetime import datetime, timezone
from uuid import uuid4

from .dependencies import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Creation Studio"])

class GenerateRequest(BaseModel):
    prompt: str
    style: Optional[str] = None

class PublishRequest(BaseModel):
    content_id: str
    title: str
    description: str
    price: float
    category: str

def get_creation_studio_router(db):
    """Create creation studio router with REAL AI integrations"""
    
    @router.post("/studio/generate-music")
    async def generate_music(
        request: GenerateRequest,
        current_user: dict = Depends(get_current_user)
    ):
        """Generate music composition using Hybrid LLM"""
        try:
            from services.nexus_hybrid_llm import hybrid_llm
            
            prompt = f"""Create a complete music composition for: {request.prompt}

Include:
1. Title
2. Genre and style
3. Tempo (BPM)
4. Key signature
5. Song structure (verse, chorus, bridge)
6. Chord progression
7. Melody description
8. Lyrics (if applicable)
9. Instrumentation

Make it professional and ready for production."""
            
            # Use hybrid LLM with smart routing
            result = await hybrid_llm.generate(
                prompt=prompt,
                task_type="creative",  # Routes to Claude for best quality
                max_tokens=4096
            )
            
            if not result['success']:
                raise HTTPException(status_code=500, detail=result.get('error'))
            
            # Save to database
            content_id = str(uuid4())
            content_doc = {
                "id": content_id,
                "type": "music",
                "user_id": current_user["id"],
                "prompt": request.prompt,
                "content": result['content'],
                "model_used": result['model'],
                "provider": result['provider'],
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            await db.created_content.insert_one(content_doc)
            
            return {
                "id": content_id,
                "type": "music",
                "prompt": request.prompt,
                "status": "generated",
                "content": result['content'],
                "model": result['model'],
                "provider": result['provider'],
                "created_at": content_doc["created_at"]
            }
        except Exception as e:
            logger.error(f"Failed to generate music: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.post("/studio/generate-video")
    async def generate_video(
        request: GenerateRequest,
        current_user: dict = Depends(get_current_user)
    ):
        """Generate video using Sora 2 or Runway"""
        try:
            from services.text_to_video_service import text_to_video_service
            
            # Generate video using Sora 2
            result = await text_to_video_service.generate_video(
                prompt=request.prompt,
                model="sora-2",
                size="1280x720",
                duration=5,
                output_filename=f"video_{current_user['id']}_{uuid4().hex[:8]}"
            )
            
            if not result["success"]:
                raise HTTPException(status_code=500, detail=result.get("error", "Video generation failed"))
            
            # Save to database
            content_id = str(uuid4())
            content_doc = {
                "id": content_id,
                "type": "video",
                "user_id": current_user["id"],
                "prompt": request.prompt,
                "video_url": result["video_url"],
                "video_path": result["video_path"],
                "model": result["model"],
                "size": result["size"],
                "duration": result["duration"],
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            await db.created_content.insert_one(content_doc)
            
            return {
                "id": content_id,
                "type": "video",
                "prompt": request.prompt,
                "status": "generated",
                "video_url": result["video_url"],
                "duration": result["duration"],
                "provider": "sora_2",
                "created_at": content_doc["created_at"]
            }
        except Exception as e:
            logger.error(f"Failed to generate video: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.post("/studio/generate-ebook")
    async def generate_ebook(
        request: GenerateRequest,
        current_user: dict = Depends(get_current_user)
    ):
        """Generate ebook content using Hybrid LLM"""
        try:
            from services.nexus_hybrid_llm import hybrid_llm
            
            prompt = f"""Write a complete ebook about: {request.prompt}

Structure:
1. Title and subtitle
2. Table of contents
3. Introduction (2 paragraphs)
4. 5 Main chapters (each with 3-4 paragraphs)
5. Conclusion
6. About the author section

Make it professional, engaging, and informative. Each chapter should be substantial."""
            
            # Use hybrid LLM - routes to Claude for best long-form content
            result = await hybrid_llm.generate(
                prompt=prompt,
                task_type="ebook",  # Routes to Claude
                max_tokens=8192
            )
            
            if not result['success']:
                raise HTTPException(status_code=500, detail=result.get('error'))
            
            # Save to database
            content_id = str(uuid4())
            content_doc = {
                "id": content_id,
                "type": "ebook",
                "user_id": current_user["id"],
                "prompt": request.prompt,
                "content": result['content'],
                "model_used": result['model'],
                "provider": result['provider'],
                "word_count": len(result['content'].split()),
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            await db.created_content.insert_one(content_doc)
            
            return {
                "id": content_id,
                "type": "ebook",
                "prompt": request.prompt,
                "status": "generated",
                "content": result['content'],
                "model": result['model'],
                "provider": result['provider'],
                "word_count": content_doc["word_count"],
                "created_at": content_doc["created_at"]
            }
        except Exception as e:
            logger.error(f"Failed to generate ebook: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/studio/created-content")
    async def get_created_content(current_user: dict = Depends(get_current_user)):
        """Get all user's created content"""
        try:
            content = await db.created_content.find(
                {"user_id": current_user["id"]},
                {"_id": 0}
            ).sort("created_at", -1).to_list(100)
            
            return {
                "content": content,
                "count": len(content)
            }
        except Exception as e:
            logger.error(f"Failed to fetch content: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.post("/studio/publish-to-marketplace")
    async def publish_to_marketplace(
        request: PublishRequest,
        current_user: dict = Depends(get_current_user)
    ):
        """Publish created content to marketplace"""
        try:
            # Get the content
            content = await db.created_content.find_one(
                {"id": request.content_id, "user_id": current_user["id"]},
                {"_id": 0}
            )
            
            if not content:
                raise HTTPException(status_code=404, detail="Content not found")
            
            # Auto-upgrade user to vendor if not already
            if current_user.get("role") not in ["vendor", "admin"]:
                await db.users.update_one(
                    {"id": current_user["id"]},
                    {"$set": {"role": "vendor"}}
                )
                logger.info(f"Upgraded user {current_user['id']} to vendor")
            
            # Create product listing
            product_id = str(uuid4())
            product_doc = {
                "id": product_id,
                "title": request.title,
                "description": request.description,
                "price": request.price,
                "category": request.category,
                "content_type": content["type"],
                "content_id": request.content_id,
                "is_ai_generated": True,
                "vendor_id": current_user["id"],
                "vendor_name": current_user["username"],
                "likes": 0,
                "views": 0,
                "sales": 0,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            
            # Add type-specific fields
            if content["type"] == "video":
                product_doc["file_url"] = content.get("video_url")
                product_doc["image_url"] = content.get("video_url")  # Use first frame as thumbnail
            elif content["type"] == "music":
                product_doc["tags"] = ["AI Music", "Generated", request.category]
            elif content["type"] == "ebook":
                product_doc["tags"] = ["AI eBook", "Digital Book", request.category]
                product_doc["word_count"] = content.get("word_count", 0)
            
            await db.products.insert_one(product_doc)
            
            return {
                "success": True,
                "product_id": product_id,
                "message": "Content published to marketplace",
                "upgraded_to_vendor": current_user.get("role") != "vendor"
            }
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to publish to marketplace: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    return router
