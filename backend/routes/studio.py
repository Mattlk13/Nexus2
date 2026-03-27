"""
Studio routes - AI generation, video, images, text-to-video
"""
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
import uuid
import logging

from .dependencies import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Studio"])

class AIGenerateRequest(BaseModel):
    type: str  # image, video, text
    prompt: str
    model: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = {}
    provider: Optional[str] = None  # sora, runway, fal, etc.

class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = None

def get_studio_router(
    db: AsyncIOMotorDatabase,
    agent_system,
    text_to_video_service,
    runway_video_service,
    fal_ai_service,
    elevenlabs_service
):
    """Create studio router with dependencies"""
    
    @router.post("/ai/generate")
    async def generate_ai_content(request: AIGenerateRequest, current_user: dict = Depends(get_current_user)):
        """Generate AI content (images, videos, text)"""
        try:
            result = None
            
            if request.type == "image":
                # Fal.ai image generation
                if request.provider == "fal" or not request.provider:
                    result = await fal_ai_service.generate_image(
                        prompt=request.prompt,
                        model=request.model or "fal-ai/flux/schnell"
                    )
                else:
                    # Fallback to agent system
                    result = await agent_system.generate_image(request.prompt)
            
            elif request.type == "video":
                provider = request.provider or "sora"
                
                if provider == "sora":
                    # Sora 2 video generation
                    result = await text_to_video_service.generate_video(
                        prompt=request.prompt,
                        model=request.model or "sora-2-latest"
                    )
                
                elif provider == "runway":
                    # Runway ML video generation
                    result = await runway_video_service.generate_video(
                        prompt=request.prompt,
                        model=request.model or "gen3a_turbo",
                        duration=request.parameters.get("duration", 5)
                    )
                
                else:
                    raise HTTPException(status_code=400, detail=f"Unknown video provider: {provider}")
            
            elif request.type == "text":
                result = await agent_system.generate_text(request.prompt, request.model)
            
            elif request.type == "audio":
                # ElevenLabs TTS
                result = await elevenlabs_service.text_to_speech(
                    text=request.prompt,
                    voice=request.parameters.get("voice", "default")
                )
            
            else:
                raise HTTPException(status_code=400, detail=f"Unknown generation type: {request.type}")
            
            # Save generation to history
            generation = {
                "id": str(uuid.uuid4()),
                "user_id": current_user["id"],
                "type": request.type,
                "prompt": request.prompt,
                "provider": request.provider,
                "result": result,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            await db.generations.insert_one(generation)
            
            return {k: v for k, v in generation.items() if k != "_id"}
        
        except Exception as e:
            logger.error(f"Generation failed: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.post("/ai/chat")
    async def ai_chat_support(message: ChatMessage, current_user: dict = Depends(get_current_user)):
        """AI chat support"""
        try:
            response = await agent_system.chat(message.message, current_user["id"], message.session_id)
            return {
                "response": response,
                "session_id": message.session_id or str(uuid.uuid4())
            }
        except Exception as e:
            logger.error(f"Chat failed: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/runway/status/{task_id}")
    async def get_runway_status(task_id: str):
        """Get Runway video generation status"""
        try:
            status = await runway_video_service.check_status(task_id)
            return status
        except Exception as e:
            logger.error(f"Failed to get Runway status: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/studio/generations")
    async def get_my_generations(
        current_user: dict = Depends(get_current_user),
        type: Optional[str] = None,
        limit: int = 50
    ):
        """Get user's generation history"""
        query = {"user_id": current_user["id"]}
        if type:
            query["type"] = type
        
        generations = await db.generations.find(
            query,
            {"_id": 0}
        ).sort("created_at", -1).limit(limit).to_list(limit)
        
        return generations
    
    return router
