"""
ULTRA Services Router - All Hybrid Integration Endpoints
"""
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import logging
import base64

from services.ultra_image_video_generator import ultra_generator
from services.ultra_voice_service import ultra_voice
from services.ultra_llm_service import ultra_llm
from services import ultra_video_conferencing
from .dependencies import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(tags=["ULTRA Services"])

# ==================== MODELS ====================

class ImageGenerationRequest(BaseModel):
    prompt: str
    negative_prompt: Optional[str] = None
    width: int = 1024
    height: int = 1024
    steps: int = 30
    guidance_scale: float = 7.5
    model: str = "sd_xl"

class VoiceGenerationRequest(BaseModel):
    text: str
    voice: str = "default_female"
    language: str = "en"
    speed: float = 1.0

class VoiceCloneRequest(BaseModel):
    audio_sample_base64: str
    voice_name: str

class LLMChatRequest(BaseModel):
    messages: List[Dict[str, str]]
    model: str = "llama-3.1-70b"
    temperature: float = 0.7
    max_tokens: int = 2000
    stream: bool = False

class VideoRoomCreate(BaseModel):
    room_name: str
    max_participants: int = 10
    enable_recording: bool = False

def get_ultra_services_router():
    """Create ULTRA services router"""
    
    # ==================== IMAGE/VIDEO GENERATION ====================
    
    @router.post("/ultra/image/generate")
    async def generate_image(
        request: ImageGenerationRequest,
        current_user: dict = Depends(get_current_user)
    ):
        """
        Generate image using ULTRA hybrid generator.
        
        Tries local backends first (ComfyUI, AUTOMATIC1111, InvokeAI),
        falls back to fal.ai if needed.
        """
        result = await ultra_generator.generate_image(
            prompt=request.prompt,
            negative_prompt=request.negative_prompt,
            width=request.width,
            height=request.height,
            steps=request.steps,
            guidance_scale=request.guidance_scale,
            model=request.model
        )
        
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error"))
        
        return result
    
    @router.get("/ultra/image/status")
    async def get_image_generator_status(current_user: dict = Depends(get_current_user)):
        """Get ULTRA image generator status"""
        return ultra_generator.get_status()
    
    # ==================== VOICE/TTS ====================
    
    @router.post("/ultra/voice/generate")
    async def generate_speech(
        request: VoiceGenerationRequest,
        current_user: dict = Depends(get_current_user)
    ):
        """
        Generate speech using ULTRA hybrid TTS.
        
        Tries local backends first (XTTS, Piper, Kokoro),
        falls back to ElevenLabs if needed.
        """
        result = await ultra_voice.generate_speech(
            text=request.text,
            voice=request.voice,
            language=request.language,
            speed=request.speed
        )
        
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error"))
        
        return result
    
    @router.post("/ultra/voice/clone")
    async def clone_voice(
        request: VoiceCloneRequest,
        current_user: dict = Depends(get_current_user)
    ):
        """
        Clone voice from audio sample (requires XTTS-v2).
        
        Only 6 seconds of audio needed for cloning.
        """
        result = await ultra_voice.clone_voice(
            audio_sample_base64=request.audio_sample_base64,
            voice_name=request.voice_name
        )
        
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error"))
        
        return result
    
    @router.get("/ultra/voice/status")
    async def get_voice_service_status(current_user: dict = Depends(get_current_user)):
        """Get ULTRA voice service status"""
        return ultra_voice.get_status()
    
    # ==================== LLM INFERENCE ====================
    
    @router.post("/ultra/llm/chat")
    async def chat_completion(
        request: LLMChatRequest,
        current_user: dict = Depends(get_current_user)
    ):
        """
        Chat completion using ULTRA hybrid LLM service.
        
        Tries local backends first (vLLM, Ollama),
        falls back to cloud (Emergent Universal Key) if needed.
        """
        result = await ultra_llm.chat_completion(
            messages=request.messages,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            stream=request.stream
        )
        
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error"))
        
        return result
    
    @router.get("/ultra/llm/status")
    async def get_llm_service_status(current_user: dict = Depends(get_current_user)):
        """Get ULTRA LLM service status"""
        return ultra_llm.get_status()
    
    # ==================== VIDEO CONFERENCING ====================
    
    @router.post("/ultra/video/create-room")
    async def create_video_room(
        request: VideoRoomCreate,
        current_user: dict = Depends(get_current_user)
    ):
        """
        Create video conference room.
        
        Uses LiveKit for large rooms, Jitsi for medium,
        P2P WebRTC for 1:1 calls.
        """
        if not ultra_video_conferencing.ultra_video:
            raise HTTPException(status_code=503, detail="Video conferencing not initialized")
        
        result = await ultra_video_conferencing.ultra_video.create_room(
            room_name=request.room_name,
            creator_id=current_user["id"],
            max_participants=request.max_participants,
            enable_recording=request.enable_recording
        )
        
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error"))
        
        return result
    
    @router.post("/ultra/video/join-room/{room_name}")
    async def join_video_room(
        room_name: str,
        current_user: dict = Depends(get_current_user)
    ):
        """Join existing video room"""
        if not ultra_video_conferencing.ultra_video:
            raise HTTPException(status_code=503, detail="Video conferencing not initialized")
        
        result = await ultra_video_conferencing.ultra_video.join_room(room_name, current_user["id"])
        
        if not result.get("success"):
            raise HTTPException(status_code=404, detail=result.get("error"))
        
        return result
    
    @router.delete("/ultra/video/leave-room/{room_name}")
    async def leave_video_room(
        room_name: str,
        current_user: dict = Depends(get_current_user)
    ):
        """Leave video room"""
        if not ultra_video_conferencing.ultra_video:
            raise HTTPException(status_code=503, detail="Video conferencing not initialized")
        
        await ultra_video_conferencing.ultra_video.leave_room(room_name, current_user["id"])
        
        return {"success": True, "message": "Left room"}
    
    @router.get("/ultra/video/rooms")
    async def get_active_video_rooms(current_user: dict = Depends(get_current_user)):
        """Get list of active video rooms"""
        if not ultra_video_conferencing.ultra_video:
            raise HTTPException(status_code=503, detail="Video conferencing not initialized")
        
        rooms = ultra_video_conferencing.ultra_video.get_active_rooms()
        
        return {
            "rooms": rooms,
            "count": len(rooms)
        }
    
    @router.get("/ultra/video/status")
    async def get_video_conferencing_status(current_user: dict = Depends(get_current_user)):
        """Get ULTRA video conferencing status"""
        if not ultra_video_conferencing.ultra_video:
            raise HTTPException(status_code=503, detail="Video conferencing not initialized")
        
        return ultra_video_conferencing.ultra_video.get_status()
    
    # ==================== COMBINED STATUS ====================
    
    @router.get("/ultra/status")
    async def get_all_ultra_services_status(current_user: dict = Depends(get_current_user)):
        """Get status of all ULTRA hybrid services"""
        video_status = ultra_video_conferencing.ultra_video.get_status() if ultra_video_conferencing.ultra_video else {"error": "Not initialized", "backend_count": 0}
        return {
            "image_video_generator": ultra_generator.get_status(),
            "voice_service": ultra_voice.get_status(),
            "llm_service": ultra_llm.get_status(),
            "video_conferencing": video_status,
            "total_services": 4,
            "philosophy": "Combine best open-source + commercial tools for superior hybrid integrations"
        }
    
    return router
