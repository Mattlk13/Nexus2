"""
OAuth Integration Routes - Easy platform connections
Handles OAuth flows for LinkedIn, Instagram, Facebook, X/Twitter
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import RedirectResponse
from typing import Dict, Any
import logging
import secrets
import os
from datetime import datetime, timezone

from .dependencies import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(tags=["OAuth"])

# OAuth configurations
OAUTH_CONFIGS = {
    "linkedin": {
        "client_id": os.getenv("LINKEDIN_CLIENT_ID"),
        "client_secret": os.getenv("LINKEDIN_CLIENT_SECRET"),
        "authorize_url": "https://www.linkedin.com/oauth/v2/authorization",
        "token_url": "https://www.linkedin.com/oauth/v2/accessToken",
        "scope": "w_member_social r_liteprofile"
    },
    "instagram": {
        "client_id": os.getenv("INSTAGRAM_CLIENT_ID"),
        "client_secret": os.getenv("INSTAGRAM_CLIENT_SECRET"),
        "authorize_url": "https://api.instagram.com/oauth/authorize",
        "token_url": "https://api.instagram.com/oauth/access_token",
        "scope": "user_profile,user_media"
    },
    "facebook": {
        "client_id": os.getenv("FACEBOOK_CLIENT_ID"),
        "client_secret": os.getenv("FACEBOOK_CLIENT_SECRET"),
        "authorize_url": "https://www.facebook.com/v18.0/dialog/oauth",
        "token_url": "https://graph.facebook.com/v18.0/oauth/access_token",
        "scope": "pages_manage_posts,pages_read_engagement"
    },
    "x_twitter": {
        "client_id": os.getenv("X_CLIENT_ID"),
        "client_secret": os.getenv("X_CLIENT_SECRET"),
        "authorize_url": "https://twitter.com/i/oauth2/authorize",
        "token_url": "https://api.twitter.com/2/oauth2/token",
        "scope": "tweet.read tweet.write users.read offline.access"
    }
}

# Store state tokens (in production, use Redis)
oauth_states = {}

def get_oauth_router(db):
    """Create OAuth router"""
    
    @router.get("/oauth/{platform}/connect")
    async def start_oauth_flow(
        platform: str,
        current_user: dict = Depends(get_current_user)
    ):
        """Start OAuth flow for a platform"""
        if platform not in OAUTH_CONFIGS:
            raise HTTPException(status_code=400, detail="Unsupported platform")
        
        config = OAUTH_CONFIGS[platform]
        
        # Generate state token for CSRF protection
        state = secrets.token_urlsafe(32)
        oauth_states[state] = {
            "user_id": current_user["id"],
            "platform": platform
        }
        
        # Build redirect URI
        redirect_uri = f"{os.getenv('APP_URL', 'http://localhost:3000')}/oauth/{platform}/callback"
        
        # Build authorization URL
        auth_url = f"{config['authorize_url']}?" + \
                   f"client_id={config['client_id']}&" + \
                   f"redirect_uri={redirect_uri}&" + \
                   f"scope={config['scope']}&" + \
                   f"response_type=code&" + \
                   f"state={state}"
        
        logger.info(f"Starting OAuth flow for {platform}")
        
        return {"authorization_url": auth_url}
    
    @router.get("/oauth/{platform}/callback")
    async def oauth_callback(
        platform: str,
        code: str = Query(...),
        state: str = Query(...)
    ):
        """Handle OAuth callback"""
        # Verify state
        if state not in oauth_states:
            raise HTTPException(status_code=400, detail="Invalid state")
        
        state_data = oauth_states.pop(state)
        user_id = state_data["user_id"]
        
        # Exchange code for access token (simulated)
        access_token = f"mock_token_{platform}_{user_id}"
        
        # Store token in database
        await db.users.update_one(
            {"id": user_id},
            {"$set": {
                f"oauth_tokens.{platform}": {
                    "access_token": access_token,
                    "platform": platform,
                    "connected_at": datetime.now(timezone.utc).isoformat()
                }
            }}
        )
        
        logger.info(f"OAuth completed for {platform} - user {user_id}")
        
        # Redirect back to app with success
        return RedirectResponse(
            url=f"/social-automation?connected={platform}",
            status_code=302
        )
    
    @router.get("/oauth/connections")
    async def get_connections(current_user: dict = Depends(get_current_user)):
        """Get user's connected platforms"""
        user = await db.users.find_one({"id": current_user["id"]}, {"_id": 0})
        
        connections = user.get("oauth_tokens", {})
        
        return {
            "connected_platforms": list(connections.keys()),
            "connections": {
                platform: {
                    "connected": True,
                    "connected_at": data.get("connected_at")
                }
                for platform, data in connections.items()
            }
        }
    
    @router.delete("/oauth/{platform}/disconnect")
    async def disconnect_platform(
        platform: str,
        current_user: dict = Depends(get_current_user)
    ):
        """Disconnect a platform"""
        await db.users.update_one(
            {"id": current_user["id"]},
            {"$unset": {f"oauth_tokens.{platform}": ""}}
        )
        
        logger.info(f"Disconnected {platform} for user {current_user['id']}")
        
        return {"success": True, "message": f"{platform} disconnected"}
    
    return router
