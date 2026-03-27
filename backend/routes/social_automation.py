"""
Hybrid Social Automation Routes - Apaya-inspired features
"""
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import logging

from services.hybrid_social_automation import hybrid_social_automation
from .dependencies import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Hybrid Social Automation"])

class GenerateContentRequest(BaseModel):
    topic: str
    platform: str = "all"

class ScheduleRequest(BaseModel):
    days_ahead: int = 30

class EngageRequest(BaseModel):
    response_text: str

def get_social_automation_router():
    """Create hybrid social automation router"""
    
    @router.get("/social-automation/status")
    async def get_status(current_user: dict = Depends(get_current_user)):
        """Get social automation service status"""
        return hybrid_social_automation.get_status()
    
    @router.get("/social-automation/brand-profile")
    async def get_brand_profile(current_user: dict = Depends(get_current_user)):
        """Get AI-analyzed brand profile"""
        try:
            profile = await hybrid_social_automation.analyze_brand_from_profile(current_user)
            return profile
        except Exception as e:
            logger.error(f"Failed to get brand profile: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.post("/social-automation/generate-content")
    async def generate_content(
        request: GenerateContentRequest,
        current_user: dict = Depends(get_current_user)
    ):
        """Generate AI-powered social media content"""
        try:
            content = await hybrid_social_automation.generate_content(
                request.topic,
                request.platform
            )
            return content
        except Exception as e:
            logger.error(f"Failed to generate content: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.post("/social-automation/schedule")
    async def schedule_posts(
        request: ScheduleRequest,
        background_tasks: BackgroundTasks,
        current_user: dict = Depends(get_current_user)
    ):
        """Schedule posts for next N days with AI-optimized times"""
        try:
            scheduled = await hybrid_social_automation.schedule_posts(request.days_ahead)
            return {
                "success": True,
                "scheduled_count": len(scheduled),
                "posts": scheduled
            }
        except Exception as e:
            logger.error(f"Failed to schedule posts: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/social-automation/scheduled-posts")
    async def get_scheduled_posts(current_user: dict = Depends(get_current_user)):
        """Get all scheduled posts"""
        return {
            "scheduled_posts": hybrid_social_automation.scheduled_posts,
            "count": len(hybrid_social_automation.scheduled_posts)
        }
    
    @router.post("/social-automation/publish/{post_id}")
    async def publish_post(
        post_id: str,
        current_user: dict = Depends(get_current_user)
    ):
        """Publish a post to all selected platforms"""
        try:
            result = await hybrid_social_automation.publish_post(post_id)
            return result
        except Exception as e:
            logger.error(f"Failed to publish post: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/social-automation/conversations")
    async def get_conversations(current_user: dict = Depends(get_current_user)):
        """Get monitored social conversations (social listening)"""
        try:
            conversations = await hybrid_social_automation.monitor_social_conversations()
            return {
                "conversations": conversations,
                "count": len(conversations)
            }
        except Exception as e:
            logger.error(f"Failed to get conversations: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.post("/social-automation/engage/{conversation_id}")
    async def engage_conversation(
        conversation_id: str,
        request: EngageRequest,
        current_user: dict = Depends(get_current_user)
    ):
        """Auto-engage in a relevant conversation"""
        try:
            result = await hybrid_social_automation.auto_engage(
                conversation_id,
                request.response_text
            )
            return result
        except Exception as e:
            logger.error(f"Failed to engage: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/social-automation/analytics")
    async def get_analytics(current_user: dict = Depends(get_current_user)):
        """Get social media performance analytics"""
        try:
            analytics = await hybrid_social_automation.analyze_performance()
            return analytics
        except Exception as e:
            logger.error(f"Failed to get analytics: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/social-automation/platforms")
    async def get_platforms(current_user: dict = Depends(get_current_user)):
        """Get supported platforms and their config"""
        return {
            "platforms": hybrid_social_automation.platforms,
            "active": [p for p, c in hybrid_social_automation.platforms.items() if c["enabled"]]
        }
    
    return router
