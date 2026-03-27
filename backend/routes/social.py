"""
Social routes - Posts, comments, likes
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timezone
import uuid

from .dependencies import get_current_user

router = APIRouter(tags=["Social"])

class PostCreate(BaseModel):
    content: str
    media: list = []

class CommentCreate(BaseModel):
    content: str

def get_social_router(db: AsyncIOMotorDatabase, agent_system, broadcast_func, create_notification_func):
    """Create social router with dependencies"""
    
    @router.get("/posts")
    async def get_posts(limit: int = 50):
        """Get all posts"""
        posts = await db.posts.find({}, {"_id": 0}).sort("created_at", -1).limit(limit).to_list(limit)
        return posts
    
    @router.post("/posts")
    async def create_post(post: PostCreate, current_user: dict = Depends(get_current_user)):
        """Create a new post"""
        moderation = await agent_system.moderate_content(post.content, "post")
        if not moderation.get("approved", True):
            raise HTTPException(status_code=400, detail=f"Content rejected: {moderation.get('reason')}")
        
        post_id = str(uuid.uuid4())
        post_doc = {
            "id": post_id,
            **post.model_dump(),
            "author_id": current_user["id"],
            "author_name": current_user["username"],
            "author_avatar": current_user.get("avatar"),
            "likes": 0,
            "comments_count": 0,
            "shares": 0,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.posts.insert_one(post_doc)
        
        await broadcast_func("feed", {"type": "new_post", "post": {k: v for k, v in post_doc.items() if k != "_id"}})
        
        return {k: v for k, v in post_doc.items() if k != "_id"}
    
    @router.post("/posts/{post_id}/like")
    async def like_post(post_id: str, current_user: dict = Depends(get_current_user)):
        """Like/unlike a post"""
        existing = await db.post_likes.find_one({"post_id": post_id, "user_id": current_user["id"]}, {"_id": 0})
        post = await db.posts.find_one({"id": post_id}, {"_id": 0})
        
        if existing:
            await db.post_likes.delete_one({"post_id": post_id, "user_id": current_user["id"]})
            await db.posts.update_one({"id": post_id}, {"$inc": {"likes": -1}})
            return {"liked": False}
        else:
            await db.post_likes.insert_one({
                "id": str(uuid.uuid4()),
                "post_id": post_id,
                "user_id": current_user["id"],
                "created_at": datetime.now(timezone.utc).isoformat()
            })
            await db.posts.update_one({"id": post_id}, {"$inc": {"likes": 1}})
            
            if post and post.get("author_id") != current_user["id"]:
                await create_notification_func(
                    post["author_id"], "like", "Post Liked",
                    f"{current_user['username']} liked your post",
                    {"post_id": post_id}
                )
            return {"liked": True}
    
    @router.post("/posts/{post_id}/comment")
    async def comment_post(post_id: str, comment: CommentCreate, current_user: dict = Depends(get_current_user)):
        """Add comment to post"""
        comment_id = str(uuid.uuid4())
        comment_doc = {
            "id": comment_id,
            "post_id": post_id,
            "content": comment.content,
            "author_id": current_user["id"],
            "author_name": current_user["username"],
            "author_avatar": current_user.get("avatar"),
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.comments.insert_one(comment_doc)
        await db.posts.update_one({"id": post_id}, {"$inc": {"comments_count": 1}})
        
        post = await db.posts.find_one({"id": post_id}, {"_id": 0})
        if post and post.get("author_id") != current_user["id"]:
            await create_notification_func(
                post["author_id"], "comment", "New Comment",
                f"{current_user['username']} commented on your post",
                {"post_id": post_id, "comment_id": comment_id}
            )
        
        return {k: v for k, v in comment_doc.items() if k != "_id"}
    
    @router.get("/posts/{post_id}/comments")
    async def get_comments(post_id: str):
        """Get all comments for a post"""
        comments = await db.comments.find({"post_id": post_id}, {"_id": 0}).sort("created_at", -1).to_list(100)
        return comments
    
    return router
