"""
NEXUS Social Network API Routes
RESTful API endpoints for social features
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from typing import List, Optional
from pydantic import BaseModel
import os
import logging

logger = logging.getLogger(__name__)

# Request/Response Models
class UserCreateRequest(BaseModel):
    email: str
    username: str
    full_name: str
    password: str
    bio: Optional[str] = ""

class UserUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    bio: Optional[str] = None
    profile_picture: Optional[str] = None
    cover_photo: Optional[str] = None

class PostCreateRequest(BaseModel):
    content: str
    media: List[str] = []
    visibility: str = "public"

class CommentCreateRequest(BaseModel):
    post_id: str
    content: str

class MessageSendRequest(BaseModel):
    to_user_id: str
    content: str
    media: List[str] = []

def create_social_routes(db, get_current_user):
    """Create social network API routes"""
    router = APIRouter(prefix="/api/social", tags=["Social Network"])
    
    # Import service
    from services.social_network_service import create_social_network_service
    social_service = create_social_network_service(db)
    
    # ==================== USER ROUTES ====================
    
    @router.post("/users/register")
    async def register_user(request: UserCreateRequest):
        """Register a new user"""
        from services.social_network_service import UserProfile
        user = UserProfile(
            email=request.email,
            username=request.username,
            full_name=request.full_name
        )
        return await social_service.create_user(user)
    
    @router.get("/users/{user_id}")
    async def get_user_profile(user_id: str):
        """Get user profile"""
        return await social_service.get_user(user_id)
    
    @router.put("/users/{user_id}")
    async def update_user_profile(user_id: str, request: UserUpdateRequest, current_user: dict = Depends(get_current_user)):
        """Update user profile"""
        # TODO: Add auth check (user can only update own profile)
        updates = request.dict(exclude_unset=True)
        return await social_service.update_user(user_id, updates)
    
    @router.get("/users/search/{query}")
    async def search_users(query: str, limit: int = 20):
        """Search users"""
        return await social_service.search_users(query, limit)
    
    # ==================== POST ROUTES ====================
    
    @router.post("/posts")
    async def create_post(request: PostCreateRequest, current_user: dict = Depends(get_current_user)):
        """Create a new post"""
        from services.social_network_service import Post
        post = Post(
            user_id=current_user["id"],
            content=request.content,
            media=request.media,
            visibility=request.visibility
        )
        return await social_service.create_post(post)
    
    @router.get("/feed")
    async def get_news_feed(skip: int = 0, limit: int = 20, current_user: dict = Depends(get_current_user)):
        """Get personalized news feed"""
        return await social_service.get_news_feed(current_user["id"], skip, limit)
    
    @router.post("/posts/{post_id}/like")
    async def like_post(post_id: str, current_user: dict = Depends(get_current_user)):
        """Like/unlike a post"""
        return await social_service.like_post(post_id, current_user["id"])
    
    @router.post("/posts/{post_id}/comment")
    async def add_comment(post_id: str, request: CommentCreateRequest, current_user: dict = Depends(get_current_user)):
        """Add comment to post"""
        from services.social_network_service import Comment
        comment = Comment(
            user_id=current_user["id"],
            post_id=post_id,
            content=request.content
        )
        return await social_service.add_comment(comment)
    
    # ==================== FRIENDS ROUTES ====================
    
    @router.post("/friends/request/{to_user_id}")
    async def send_friend_request(to_user_id: str, current_user: dict = Depends(get_current_user)):
        """Send friend request"""
        return await social_service.send_friend_request(current_user["id"], to_user_id)
    
    @router.post("/friends/accept/{request_id}")
    async def accept_friend_request(request_id: str, current_user: dict = Depends(get_current_user)):
        """Accept friend request"""
        return await social_service.accept_friend_request(request_id)
    
    @router.delete("/friends/{friend_id}")
    async def remove_friend(friend_id: str, current_user: dict = Depends(get_current_user)):
        """Remove friend"""
        return await social_service.remove_friend(current_user["id"], friend_id)
    
    @router.get("/friends")
    async def get_friends(current_user: dict = Depends(get_current_user)):
        """Get friends list"""
        return await social_service.get_friends(current_user["id"])
    
    # ==================== MESSAGING ROUTES ====================
    
    @router.post("/messages")
    async def send_message(request: MessageSendRequest, current_user: dict = Depends(get_current_user)):
        """Send direct message"""
        from services.social_network_service import Message
        message = Message(
            from_user_id=current_user["id"],
            to_user_id=request.to_user_id,
            content=request.content,
            media=request.media
        )
        return await social_service.send_message(message)
    
    @router.get("/messages/{other_user_id}")
    async def get_conversation(other_user_id: str, limit: int = 50, current_user: dict = Depends(get_current_user)):
        """Get conversation with user"""
        return await social_service.get_conversation(current_user["id"], other_user_id, limit)
    
    @router.post("/messages/{from_user_id}/read")
    async def mark_messages_read(from_user_id: str, current_user: dict = Depends(get_current_user)):
        """Mark messages as read"""
        return await social_service.mark_messages_read(current_user["id"], from_user_id)
    
    # ==================== NOTIFICATIONS ROUTES ====================
    
    @router.get("/notifications")
    async def get_notifications(unread_only: bool = False, limit: int = 50, current_user: dict = Depends(get_current_user)):
        """Get notifications"""
        return await social_service.get_notifications(current_user["id"], unread_only, limit)
    
    @router.post("/notifications/{notification_id}/read")
    async def mark_notification_read(notification_id: str):
        """Mark notification as read"""
        return await social_service.mark_notification_read(notification_id)
    
    # ==================== FILE UPLOAD ====================
    
    @router.post("/upload")
    async def upload_file(file: UploadFile = File(...), current_user: dict = Depends(get_current_user)):
        """Upload photo/video to Cloudflare R2"""
        try:
            from services.cloudflare_service_enhanced import cloudflare_service
            
            # Read file
            content = await file.read()
            filename = f"{current_user['id']}_{file.filename}"
            
            # Upload to R2
            result = await cloudflare_service.upload_to_r2(
                file_content=content,
                filename=filename,
                content_type=file.content_type
            )
            
            return result
        except Exception as e:
            logger.error(f"Upload error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    return router
