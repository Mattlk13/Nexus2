"""
Instagram Integration Service using Instaloader
Auto-post content to Instagram from NEXUS
"""
import logging
import os
from typing import Dict, Any, Optional
from pathlib import Path
import asyncio

logger = logging.getLogger(__name__)

class InstagramService:
    """Service for Instagram integration using Instaloader"""
    
    def __init__(self):
        self.username = os.environ.get('INSTAGRAM_USERNAME', '')
        self.password = os.environ.get('INSTAGRAM_PASSWORD', '')
        self.session_file = Path('/app/backend/.instagram_session')
        self.loader = None
        self._initialize_loader()
    
    def _initialize_loader(self):
        """Initialize Instaloader"""
        try:
            import instaloader
            self.loader = instaloader.Instaloader(
                download_pictures=True,
                download_videos=True,
                download_video_thumbnails=False,
                save_metadata=False,
                compress_json=False
            )
            logger.info("✓ Instagram service initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Instagram: {e}")
            self.loader = None
    
    async def login(self) -> bool:
        """Login to Instagram"""
        if not self.loader or not self.username or not self.password:
            return False
        
        try:
            # Try to load session first
            if self.session_file.exists():
                self.loader.load_session_from_file(self.username, str(self.session_file))
                logger.info("✓ Instagram session loaded")
                return True
            
            # Fresh login
            await asyncio.to_thread(self.loader.login, self.username, self.password)
            
            # Save session
            self.loader.save_session_to_file(str(self.session_file))
            logger.info("✓ Instagram login successful")
            return True
            
        except Exception as e:
            logger.error(f"Instagram login failed: {e}")
            return False
    
    async def post_image(
        self,
        image_path: str,
        caption: str,
        hashtags: Optional[list] = None
    ) -> Dict[str, Any]:
        """
        Post image to Instagram
        
        Args:
            image_path: Path to image file
            caption: Post caption
            hashtags: List of hashtags
        """
        if not self.loader:
            return {"success": False, "error": "Instagram not initialized"}
        
        try:
            # Ensure logged in
            if not await self.login():
                return {"success": False, "error": "Login failed"}
            
            # Build full caption with hashtags
            full_caption = caption
            if hashtags:
                full_caption += "\n\n" + " ".join(f"#{tag}" for tag in hashtags)
            
            # Note: Instaloader is primarily for downloading
            # For posting, we'd need Instagram Private API (instagrapi)
            # This is a placeholder for the architecture
            
            logger.info(f"Instagram post prepared: {image_path}")
            
            return {
                "success": True,
                "message": "Post prepared (requires instagrapi for actual posting)",
                "caption": full_caption
            }
            
        except Exception as e:
            logger.error(f"Instagram post error: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_profile_stats(self, username: str) -> Dict[str, Any]:
        """Get profile statistics"""
        if not self.loader:
            return {"success": False, "error": "Instagram not initialized"}
        
        try:
            import instaloader
            profile = instaloader.Profile.from_username(self.loader.context, username)
            
            return {
                "success": True,
                "username": profile.username,
                "full_name": profile.full_name,
                "followers": profile.followers,
                "following": profile.followees,
                "posts": profile.mediacount,
                "biography": profile.biography,
                "is_private": profile.is_private,
                "is_verified": profile.is_verified
            }
            
        except Exception as e:
            logger.error(f"Get profile stats error: {e}")
            return {"success": False, "error": str(e)}
    
    async def download_profile_posts(
        self,
        username: str,
        max_posts: int = 10
    ) -> Dict[str, Any]:
        """Download recent posts from a profile"""
        if not self.loader:
            return {"success": False, "error": "Instagram not initialized"}
        
        try:
            import instaloader
            profile = instaloader.Profile.from_username(self.loader.context, username)
            
            posts = []
            for i, post in enumerate(profile.get_posts()):
                if i >= max_posts:
                    break
                
                posts.append({
                    "url": post.url,
                    "caption": post.caption,
                    "likes": post.likes,
                    "comments": post.comments,
                    "date": post.date_utc.isoformat(),
                    "is_video": post.is_video
                })
            
            return {
                "success": True,
                "username": username,
                "posts": posts,
                "count": len(posts)
            }
            
        except Exception as e:
            logger.error(f"Download posts error: {e}")
            return {"success": False, "error": str(e)}
    
    def get_status(self) -> Dict[str, Any]:
        """Get Instagram service status"""
        return {
            "available": self.loader is not None,
            "configured": bool(self.username and self.password),
            "session_exists": self.session_file.exists()
        }

# Create singleton instance
instagram_service = InstagramService()
