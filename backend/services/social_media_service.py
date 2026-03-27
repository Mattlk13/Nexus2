"""
Social Media Integration Service
Supports multiple platforms: Buffer, SocialBee, Later, and direct posting
"""
import logging
import os
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import httpx
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class SocialMediaService:
    """Unified service for managing social media posts across multiple platforms"""
    
    def __init__(self):
        # API Keys
        self.buffer_token = os.environ.get('BUFFER_ACCESS_TOKEN', '')
        self.socialbee_token = os.environ.get('SOCIALBEE_API_KEY', '')
        self.later_token = os.environ.get('LATER_API_KEY', '')
        
        # Base URLs
        self.buffer_url = "https://api.bufferapp.com/1"
        self.socialbee_url = "https://api.socialbee.com/v1"
        self.later_url = "https://api.later.com/v1"
        
        self.supported_platforms = {
            "buffer": {
                "name": "Buffer",
                "active": bool(self.buffer_token),
                "features": ["scheduling", "analytics", "multi-account"]
            },
            "socialbee": {
                "name": "SocialBee",
                "active": bool(self.socialbee_token),
                "features": ["scheduling", "ai_generation", "categories", "dall_e_3"]
            },
            "later": {
                "name": "Later",
                "active": bool(self.later_token),
                "features": ["visual_planning", "instagram_focus", "link_in_bio"]
            }
        }
    
    async def get_platform_status(self) -> Dict[str, Any]:
        """Get status of all integrated social media platforms"""
        return {
            "platforms": self.supported_platforms,
            "active_count": sum(1 for p in self.supported_platforms.values() if p["active"]),
            "total_count": len(self.supported_platforms)
        }
    
    # ==================== BUFFER INTEGRATION ====================
    
    async def buffer_get_profiles(self) -> Dict[str, Any]:
        """Get all connected Buffer profiles (Facebook, Twitter, LinkedIn, etc.)"""
        if not self.buffer_token:
            return {"success": False, "error": "Buffer not configured"}
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.buffer_url}/profiles.json",
                    params={"access_token": self.buffer_token}
                )
                
                if response.status_code == 200:
                    profiles = response.json()
                    return {
                        "success": True,
                        "profiles": profiles,
                        "count": len(profiles)
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Buffer API error: {response.status_code}"
                    }
        except Exception as e:
            logger.error(f"Buffer profiles error: {e}")
            return {"success": False, "error": str(e)}
    
    async def buffer_create_post(
        self,
        profile_ids: List[str],
        text: str,
        media_url: Optional[str] = None,
        scheduled_at: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Create a post on Buffer
        
        Args:
            profile_ids: List of Buffer profile IDs to post to
            text: Post content
            media_url: Optional image/video URL
            scheduled_at: Optional schedule time (UTC)
        """
        if not self.buffer_token:
            return {"success": False, "error": "Buffer not configured"}
        
        try:
            results = []
            
            for profile_id in profile_ids:
                payload = {
                    "access_token": self.buffer_token,
                    "profile_ids[]": profile_id,
                    "text": text,
                    "now": scheduled_at is None
                }
                
                if media_url:
                    payload["media[photo]"] = media_url
                
                if scheduled_at:
                    payload["scheduled_at"] = int(scheduled_at.timestamp())
                
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"{self.buffer_url}/updates/create.json",
                        data=payload
                    )
                    
                    if response.status_code == 200:
                        results.append({
                            "profile_id": profile_id,
                            "success": True,
                            "data": response.json()
                        })
                    else:
                        results.append({
                            "profile_id": profile_id,
                            "success": False,
                            "error": response.text
                        })
            
            return {
                "success": True,
                "results": results,
                "posted_count": sum(1 for r in results if r["success"])
            }
            
        except Exception as e:
            logger.error(f"Buffer post error: {e}")
            return {"success": False, "error": str(e)}
    
    # ==================== SOCIALBEE INTEGRATION ====================
    
    async def socialbee_get_profiles(self) -> Dict[str, Any]:
        """Get all connected SocialBee profiles"""
        if not self.socialbee_token:
            return {"success": False, "error": "SocialBee not configured"}
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.socialbee_url}/profiles",
                    headers={"Authorization": f"Bearer {self.socialbee_token}"}
                )
                
                if response.status_code == 200:
                    profiles = response.json()
                    return {
                        "success": True,
                        "profiles": profiles,
                        "count": len(profiles.get("data", []))
                    }
                else:
                    return {
                        "success": False,
                        "error": f"SocialBee API error: {response.status_code}"
                    }
        except Exception as e:
            logger.error(f"SocialBee profiles error: {e}")
            return {"success": False, "error": str(e)}
    
    async def socialbee_create_post(
        self,
        profile_ids: List[str],
        text: str,
        category: str = "general",
        media_urls: Optional[List[str]] = None,
        scheduled_at: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Create a post on SocialBee
        
        Args:
            profile_ids: List of SocialBee profile IDs
            text: Post content
            category: Post category
            media_urls: Optional list of image URLs
            scheduled_at: Optional schedule time
        """
        if not self.socialbee_token:
            return {"success": False, "error": "SocialBee not configured"}
        
        try:
            payload = {
                "profiles": profile_ids,
                "text": text,
                "category": category
            }
            
            if media_urls:
                payload["media"] = media_urls
            
            if scheduled_at:
                payload["post_at"] = scheduled_at.isoformat()
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.socialbee_url}/posts",
                    headers={"Authorization": f"Bearer {self.socialbee_token}"},
                    json=payload
                )
                
                if response.status_code in [200, 201]:
                    return {
                        "success": True,
                        "data": response.json()
                    }
                else:
                    return {
                        "success": False,
                        "error": f"SocialBee API error: {response.text}"
                    }
                    
        except Exception as e:
            logger.error(f"SocialBee post error: {e}")
            return {"success": False, "error": str(e)}
    
    # ==================== LATER INTEGRATION ====================
    
    async def later_get_profiles(self) -> Dict[str, Any]:
        """Get all connected Later profiles"""
        if not self.later_token:
            return {"success": False, "error": "Later not configured"}
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.later_url}/social_profiles",
                    headers={"Authorization": f"Bearer {self.later_token}"}
                )
                
                if response.status_code == 200:
                    profiles = response.json()
                    return {
                        "success": True,
                        "profiles": profiles,
                        "count": len(profiles.get("social_profiles", []))
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Later API error: {response.status_code}"
                    }
        except Exception as e:
            logger.error(f"Later profiles error: {e}")
            return {"success": False, "error": str(e)}
    
    async def later_schedule_post(
        self,
        profile_id: str,
        text: str,
        media_url: str,
        scheduled_at: datetime
    ) -> Dict[str, Any]:
        """Schedule a post on Later (primarily for Instagram)"""
        if not self.later_token:
            return {"success": False, "error": "Later not configured"}
        
        try:
            payload = {
                "social_profile_id": profile_id,
                "caption": text,
                "media_url": media_url,
                "scheduled_at": scheduled_at.isoformat()
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.later_url}/posts",
                    headers={"Authorization": f"Bearer {self.later_token}"},
                    json=payload
                )
                
                if response.status_code in [200, 201]:
                    return {
                        "success": True,
                        "data": response.json()
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Later API error: {response.text}"
                    }
                    
        except Exception as e:
            logger.error(f"Later post error: {e}")
            return {"success": False, "error": str(e)}
    
    # ==================== UNIFIED POSTING ====================
    
    async def post_to_all_platforms(
        self,
        text: str,
        media_url: Optional[str] = None,
        platforms: Optional[List[str]] = None,
        scheduled_at: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Post to multiple social media platforms at once
        
        Args:
            text: Post content
            media_url: Optional media URL
            platforms: List of platforms to post to (defaults to all active)
            scheduled_at: Optional schedule time
        """
        if platforms is None:
            platforms = [p for p, data in self.supported_platforms.items() if data["active"]]
        
        results = {}
        
        # Buffer
        if "buffer" in platforms and self.buffer_token:
            profiles_res = await self.buffer_get_profiles()
            if profiles_res["success"] and profiles_res.get("profiles"):
                profile_ids = [p["id"] for p in profiles_res["profiles"]]
                results["buffer"] = await self.buffer_create_post(
                    profile_ids, text, media_url, scheduled_at
                )
        
        # SocialBee
        if "socialbee" in platforms and self.socialbee_token:
            profiles_res = await self.socialbee_get_profiles()
            if profiles_res["success"] and profiles_res.get("profiles"):
                profile_ids = [p["id"] for p in profiles_res["profiles"].get("data", [])]
                results["socialbee"] = await self.socialbee_create_post(
                    profile_ids, text, "general", [media_url] if media_url else None, scheduled_at
                )
        
        # Later (Instagram-focused)
        if "later" in platforms and self.later_token and media_url:
            profiles_res = await self.later_get_profiles()
            if profiles_res["success"] and profiles_res.get("profiles"):
                for profile in profiles_res["profiles"].get("social_profiles", []):
                    if scheduled_at:  # Later requires scheduling
                        results["later"] = await self.later_schedule_post(
                            profile["id"], text, media_url, scheduled_at
                        )
                        break  # Post to first profile only
        
        return {
            "success": True,
            "results": results,
            "platforms_posted": len(results)
        }

# Create singleton instance
social_media_service = SocialMediaService()
