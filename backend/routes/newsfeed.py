"""
Newsfeed Routes - Social feed with posts, likes, comments (MongoDB persistence)
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
import logging
from datetime import datetime, timezone
from uuid import uuid4

from .dependencies import get_current_user, get_optional_user

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Newsfeed"])

class CreatePostRequest(BaseModel):
    content: str
    media_urls: Optional[List[str]] = []
    post_type: Optional[str] = "text"  # text, image, video

class CreateCommentRequest(BaseModel):
    content: str

def get_newsfeed_router(db):
    """Create newsfeed router with MongoDB persistence"""
    
    @router.get("/newsfeed/posts")
    async def get_posts(
        limit: int = 50,
        current_user: dict = Depends(get_optional_user)
    ):
        """Get all posts with like status"""
        try:
            posts = await db.newsfeed_posts.find(
                {},
                {"_id": 0}
            ).sort("created_at", -1).limit(limit).to_list(limit)
            
            # If user is logged in, check which posts they've liked
            if current_user:
                for post in posts:
                    like = await db.newsfeed_likes.find_one({
                        "post_id": post["id"],
                        "user_id": current_user["id"]
                    })
                    post["liked_by_user"] = like is not None
            
            return {"posts": posts}
        except Exception as e:
            logger.error(f"Failed to get posts: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.post("/newsfeed/posts")
    async def create_post(
        request: CreatePostRequest,
        current_user: dict = Depends(get_current_user)
    ):
        """Create a new post"""
        try:
            post_id = str(uuid4())
            post = {
                "id": post_id,
                "content": request.content,
                "media_urls": request.media_urls or [],
                "post_type": request.post_type or "text",
                "author_id": current_user["id"],
                "author_name": current_user.get("username", "User"),
                "author_avatar": current_user.get("avatar"),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "likes": 0,
                "comments": 0
            }
            
            await db.newsfeed_posts.insert_one(post)
            logger.info(f"Created post {post_id} by user {current_user['id']}")
            
            return {k: v for k, v in post.items() if k != "_id"}
        except Exception as e:
            logger.error(f"Failed to create post: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.post("/newsfeed/posts/{post_id}/like")
    async def like_post(
        post_id: str,
        current_user: dict = Depends(get_current_user)
    ):
        """Like or unlike a post"""
        try:
            # Check if post exists
            post = await db.newsfeed_posts.find_one({"id": post_id}, {"_id": 0})
            if not post:
                raise HTTPException(status_code=404, detail="Post not found")
            
            # Check if already liked
            existing_like = await db.newsfeed_likes.find_one({
                "post_id": post_id,
                "user_id": current_user["id"]
            })
            
            if existing_like:
                # Unlike
                await db.newsfeed_likes.delete_one({
                    "post_id": post_id,
                    "user_id": current_user["id"]
                })
                await db.newsfeed_posts.update_one(
                    {"id": post_id},
                    {"$inc": {"likes": -1}}
                )
                new_likes = max(0, post.get("likes", 0) - 1)
                logger.info(f"User {current_user['id']} unliked post {post_id}")
                return {"success": True, "liked": False, "likes": new_likes}
            else:
                # Like
                await db.newsfeed_likes.insert_one({
                    "id": str(uuid4()),
                    "post_id": post_id,
                    "user_id": current_user["id"],
                    "created_at": datetime.now(timezone.utc).isoformat()
                })
                await db.newsfeed_posts.update_one(
                    {"id": post_id},
                    {"$inc": {"likes": 1}}
                )
                new_likes = post.get("likes", 0) + 1
                logger.info(f"User {current_user['id']} liked post {post_id}")
                
                # Notify post author if not self-like
                if post["author_id"] != current_user["id"]:
                    await db.notifications.insert_one({
                        "id": str(uuid4()),
                        "user_id": post["author_id"],
                        "type": "like",
                        "title": "New Like",
                        "message": f"{current_user['username']} liked your post",
                        "data": {"post_id": post_id},
                        "read": False,
                        "created_at": datetime.now(timezone.utc).isoformat()
                    })
                
                return {"success": True, "liked": True, "likes": new_likes}
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to like post: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/newsfeed/posts/{post_id}/comments")
    async def get_comments(post_id: str, limit: int = 50):
        """Get comments for a post"""
        try:
            comments = await db.newsfeed_comments.find(
                {"post_id": post_id},
                {"_id": 0}
            ).sort("created_at", -1).limit(limit).to_list(limit)
            
            return {"comments": comments}
        except Exception as e:
            logger.error(f"Failed to get comments: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.post("/newsfeed/posts/{post_id}/comment")
    async def add_comment(
        post_id: str,
        request: CreateCommentRequest,
        current_user: dict = Depends(get_current_user)
    ):
        """Add a comment to a post"""
        try:
            # Check if post exists
            post = await db.newsfeed_posts.find_one({"id": post_id}, {"_id": 0})
            if not post:
                raise HTTPException(status_code=404, detail="Post not found")
            
            comment_id = str(uuid4())
            comment = {
                "id": comment_id,
                "post_id": post_id,
                "content": request.content,
                "author_id": current_user["id"],
                "author_name": current_user.get("username", "User"),
                "author_avatar": current_user.get("avatar"),
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            
            await db.newsfeed_comments.insert_one(comment)
            await db.newsfeed_posts.update_one(
                {"id": post_id},
                {"$inc": {"comments": 1}}
            )
            
            # Notify post author if not self-comment
            if post["author_id"] != current_user["id"]:
                await db.notifications.insert_one({
                    "id": str(uuid4()),
                    "user_id": post["author_id"],
                    "type": "comment",
                    "title": "New Comment",
                    "message": f"{current_user['username']} commented on your post",
                    "data": {"post_id": post_id, "comment_id": comment_id},
                    "read": False,
                    "created_at": datetime.now(timezone.utc).isoformat()
                })
            
            logger.info(f"User {current_user['id']} commented on post {post_id}")
            return {k: v for k, v in comment.items() if k != "_id"}
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to add comment: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/messenger/online-friends")
    async def get_online_friends(current_user: dict = Depends(get_current_user)):
        """Get online friends list"""
        try:
            # Get users who the current user follows
            follows = await db.follows.find(
                {"follower_id": current_user["id"]},
                {"_id": 0}
            ).to_list(100)
            
            following_ids = [f["following_id"] for f in follows]
            
            # Get user info for followed users
            friends = await db.users.find(
                {"id": {"$in": following_ids}},
                {"_id": 0, "id": 1, "username": 1, "avatar": 1}
            ).to_list(100)
            
            # Add online status (would be tracked via Socket.IO in real implementation)
            for friend in friends:
                friend["online"] = False  # Placeholder - implement real online tracking
            
            return {"online_friends": friends}
        except Exception as e:
            logger.error(f"Failed to get online friends: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    return router
