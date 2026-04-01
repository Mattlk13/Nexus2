"""
NEXUS Social Network Service
Facebook-like social features: profiles, posts, friends, chat
"""
from fastapi import HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict
from datetime import datetime, timezone
from uuid import uuid4
import logging

logger = logging.getLogger(__name__)

# Pydantic Models
class UserProfile(BaseModel):
    id: Optional[str] = None
    email: EmailStr
    username: str
    full_name: str
    bio: Optional[str] = ""
    profile_picture: Optional[str] = None
    cover_photo: Optional[str] = None
    is_vendor: bool = False
    friends: List[str] = []
    friend_requests: List[str] = []
    created_at: Optional[datetime] = None
    last_active: Optional[datetime] = None
    settings: Dict = {}

class Post(BaseModel):
    id: Optional[str] = None
    user_id: str
    content: str
    media: List[str] = []
    likes: List[str] = []
    comments: List[Dict] = []
    shares: int = 0
    visibility: str = "public"  # public, friends, private
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class Comment(BaseModel):
    id: Optional[str] = None
    user_id: str
    post_id: str
    content: str
    likes: List[str] = []
    created_at: Optional[datetime] = None

class FriendRequest(BaseModel):
    id: Optional[str] = None
    from_user_id: str
    to_user_id: str
    status: str = "pending"  # pending, accepted, rejected
    created_at: Optional[datetime] = None

class Message(BaseModel):
    id: Optional[str] = None
    from_user_id: str
    to_user_id: str
    content: str
    media: List[str] = []
    read: bool = False
    created_at: Optional[datetime] = None

class Notification(BaseModel):
    id: Optional[str] = None
    user_id: str
    type: str  # friend_request, post_like, comment, message
    from_user_id: str
    content: str
    link: Optional[str] = None
    read: bool = False
    created_at: Optional[datetime] = None

class SocialNetworkService:
    def __init__(self, db):
        self.db = db
        self.users = db.users
        self.posts = db.posts
        self.comments = db.comments
        self.friend_requests = db.friend_requests
        self.messages = db.messages
        self.notifications = db.notifications
    
    # ==================== USER MANAGEMENT ====================
    
    async def create_user(self, user: UserProfile) -> Dict:
        """Create a new user profile"""
        try:
            # Check if username/email exists
            existing = await self.users.find_one(
                {"$or": [{"email": user.email}, {"username": user.username}]},
                {"_id": 0}
            )
            if existing:
                raise HTTPException(status_code=400, detail="Username or email already exists")
            
            user_dict = user.dict()
            user_dict["id"] = str(uuid4())
            user_dict["created_at"] = datetime.now(timezone.utc)
            user_dict["last_active"] = datetime.now(timezone.utc)
            
            await self.users.insert_one(user_dict)
            return {"success": True, "user": user_dict}
        except Exception as e:
            logger.error(f"Create user error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def get_user(self, user_id: str) -> Dict:
        """Get user profile"""
        user = await self.users.find_one({"id": user_id}, {"_id": 0})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    
    async def update_user(self, user_id: str, updates: Dict) -> Dict:
        """Update user profile"""
        await self.users.update_one(
            {"id": user_id},
            {"$set": updates}
        )
        return {"success": True, "user_id": user_id}
    
    async def search_users(self, query: str, limit: int = 20) -> List[Dict]:
        """Search users by username or full name"""
        users = await self.users.find(
            {
                "$or": [
                    {"username": {"$regex": query, "$options": "i"}},
                    {"full_name": {"$regex": query, "$options": "i"}}
                ]
            },
            {"_id": 0}
        ).limit(limit).to_list(limit)
        return users
    
    # ==================== POSTS & FEED ====================
    
    async def create_post(self, post: Post) -> Dict:
        """Create a new post"""
        try:
            post_dict = post.dict()
            post_dict["id"] = str(uuid4())
            post_dict["created_at"] = datetime.now(timezone.utc)
            post_dict["updated_at"] = datetime.now(timezone.utc)
            
            await self.posts.insert_one(post_dict)
            return {"success": True, "post": post_dict}
        except Exception as e:
            logger.error(f"Create post error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def get_news_feed(self, user_id: str, skip: int = 0, limit: int = 20) -> List[Dict]:
        """Get news feed for user (own posts + friends' posts)"""
        user = await self.get_user(user_id)
        friend_ids = user.get("friends", [])
        
        # Get posts from user and friends
        posts = await self.posts.find(
            {
                "$or": [
                    {"user_id": user_id},
                    {"user_id": {"$in": friend_ids}, "visibility": {"$in": ["public", "friends"]}}
                ]
            },
            {"_id": 0}
        ).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
        
        # Enrich with user data
        for post in posts:
            post_user = await self.users.find_one({"id": post["user_id"]}, {"_id": 0, "username": 1, "full_name": 1, "profile_picture": 1})
            post["user"] = post_user
        
        return posts
    
    async def like_post(self, post_id: str, user_id: str) -> Dict:
        """Like/unlike a post"""
        post = await self.posts.find_one({"id": post_id}, {"_id": 0})
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        likes = post.get("likes", [])
        if user_id in likes:
            # Unlike
            await self.posts.update_one(
                {"id": post_id},
                {"$pull": {"likes": user_id}}
            )
            return {"success": True, "action": "unliked"}
        else:
            # Like
            await self.posts.update_one(
                {"id": post_id},
                {"$push": {"likes": user_id}}
            )
            
            # Create notification
            await self.create_notification(
                user_id=post["user_id"],
                type="post_like",
                from_user_id=user_id,
                content="liked your post",
                link=f"/post/{post_id}"
            )
            return {"success": True, "action": "liked"}
    
    async def add_comment(self, comment: Comment) -> Dict:
        """Add comment to post"""
        comment_dict = comment.dict()
        comment_dict["id"] = str(uuid4())
        comment_dict["created_at"] = datetime.now(timezone.utc)
        
        await self.comments.insert_one(comment_dict)
        
        # Add to post's comments array
        await self.posts.update_one(
            {"id": comment.post_id},
            {"$push": {"comments": comment_dict}}
        )
        
        # Create notification
        post = await self.posts.find_one({"id": comment.post_id}, {"_id": 0})
        if post and post["user_id"] != comment.user_id:
            await self.create_notification(
                user_id=post["user_id"],
                type="comment",
                from_user_id=comment.user_id,
                content="commented on your post",
                link=f"/post/{comment.post_id}"
            )
        
        return {"success": True, "comment": comment_dict}
    
    # ==================== FRIENDS SYSTEM ====================
    
    async def send_friend_request(self, from_user_id: str, to_user_id: str) -> Dict:
        """Send friend request"""
        # Check if already friends
        user = await self.get_user(from_user_id)
        if to_user_id in user.get("friends", []):
            return {"success": False, "message": "Already friends"}
        
        # Check if request already exists
        existing = await self.friend_requests.find_one(
            {"from_user_id": from_user_id, "to_user_id": to_user_id, "status": "pending"},
            {"_id": 0}
        )
        if existing:
            return {"success": False, "message": "Request already sent"}
        
        request = FriendRequest(
            from_user_id=from_user_id,
            to_user_id=to_user_id
        )
        request_dict = request.dict()
        request_dict["id"] = str(uuid4())
        request_dict["created_at"] = datetime.now(timezone.utc)
        
        await self.friend_requests.insert_one(request_dict)
        
        # Add to user's friend_requests array
        await self.users.update_one(
            {"id": to_user_id},
            {"$push": {"friend_requests": from_user_id}}
        )
        
        # Create notification
        await self.create_notification(
            user_id=to_user_id,
            type="friend_request",
            from_user_id=from_user_id,
            content="sent you a friend request",
            link=f"/profile/{from_user_id}"
        )
        
        return {"success": True, "request": request_dict}
    
    async def accept_friend_request(self, request_id: str) -> Dict:
        """Accept friend request"""
        request = await self.friend_requests.find_one({"id": request_id}, {"_id": 0})
        if not request:
            raise HTTPException(status_code=404, detail="Request not found")
        
        # Update request status
        await self.friend_requests.update_one(
            {"id": request_id},
            {"$set": {"status": "accepted"}}
        )
        
        # Add to friends lists (both users)
        await self.users.update_one(
            {"id": request["from_user_id"]},
            {"$push": {"friends": request["to_user_id"]}}
        )
        await self.users.update_one(
            {"id": request["to_user_id"]},
            {"$push": {"friends": request["from_user_id"]},
             "$pull": {"friend_requests": request["from_user_id"]}}
        )
        
        # Create notification
        await self.create_notification(
            user_id=request["from_user_id"],
            type="friend_request",
            from_user_id=request["to_user_id"],
            content="accepted your friend request",
            link=f"/profile/{request['to_user_id']}"
        )
        
        return {"success": True, "message": "Friend request accepted"}
    
    async def remove_friend(self, user_id: str, friend_id: str) -> Dict:
        """Remove friend"""
        await self.users.update_one(
            {"id": user_id},
            {"$pull": {"friends": friend_id}}
        )
        await self.users.update_one(
            {"id": friend_id},
            {"$pull": {"friends": user_id}}
        )
        return {"success": True, "message": "Friend removed"}
    
    async def get_friends(self, user_id: str) -> List[Dict]:
        """Get user's friends list"""
        user = await self.get_user(user_id)
        friend_ids = user.get("friends", [])
        
        friends = await self.users.find(
            {"id": {"$in": friend_ids}},
            {"_id": 0, "id": 1, "username": 1, "full_name": 1, "profile_picture": 1}
        ).to_list(1000)
        
        return friends
    
    # ==================== MESSAGING ====================
    
    async def send_message(self, message: Message) -> Dict:
        """Send direct message"""
        message_dict = message.dict()
        message_dict["id"] = str(uuid4())
        message_dict["created_at"] = datetime.now(timezone.utc)
        
        await self.messages.insert_one(message_dict)
        
        # Create notification
        await self.create_notification(
            user_id=message.to_user_id,
            type="message",
            from_user_id=message.from_user_id,
            content="sent you a message",
            link=f"/messages/{message.from_user_id}"
        )
        
        return {"success": True, "message": message_dict}
    
    async def get_conversation(self, user1_id: str, user2_id: str, limit: int = 50) -> List[Dict]:
        """Get conversation between two users"""
        messages = await self.messages.find(
            {
                "$or": [
                    {"from_user_id": user1_id, "to_user_id": user2_id},
                    {"from_user_id": user2_id, "to_user_id": user1_id}
                ]
            },
            {"_id": 0}
        ).sort("created_at", 1).limit(limit).to_list(limit)
        
        return messages
    
    async def mark_messages_read(self, user_id: str, from_user_id: str) -> Dict:
        """Mark all messages from a user as read"""
        await self.messages.update_many(
            {"from_user_id": from_user_id, "to_user_id": user_id, "read": False},
            {"$set": {"read": True}}
        )
        return {"success": True}
    
    # ==================== NOTIFICATIONS ====================
    
    async def create_notification(self, user_id: str, type: str, from_user_id: str, content: str, link: Optional[str] = None) -> Dict:
        """Create notification"""
        notification = Notification(
            user_id=user_id,
            type=type,
            from_user_id=from_user_id,
            content=content,
            link=link
        )
        notification_dict = notification.dict()
        notification_dict["id"] = str(uuid4())
        notification_dict["created_at"] = datetime.now(timezone.utc)
        
        await self.notifications.insert_one(notification_dict)
        return {"success": True, "notification": notification_dict}
    
    async def get_notifications(self, user_id: str, unread_only: bool = False, limit: int = 50) -> List[Dict]:
        """Get user notifications"""
        query = {"user_id": user_id}
        if unread_only:
            query["read"] = False
        
        notifications = await self.notifications.find(
            query,
            {"_id": 0}
        ).sort("created_at", -1).limit(limit).to_list(limit)
        
        # Enrich with user data
        for notif in notifications:
            user = await self.users.find_one(
                {"id": notif["from_user_id"]},
                {"_id": 0, "username": 1, "full_name": 1, "profile_picture": 1}
            )
            notif["from_user"] = user
        
        return notifications
    
    async def mark_notification_read(self, notification_id: str) -> Dict:
        """Mark notification as read"""
        await self.notifications.update_one(
            {"id": notification_id},
            {"$set": {"read": True}}
        )
        return {"success": True}

def create_social_network_service(db):
    return SocialNetworkService(db)
