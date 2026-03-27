"""
User routes - Profiles, follows, vendor analytics
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional
from datetime import datetime, timezone

from .dependencies import get_current_user, require_vendor

router = APIRouter(tags=["Users"])

class UserProfileUpdate(BaseModel):
    username: Optional[str] = None
    bio: Optional[str] = None
    avatar: Optional[str] = None
    location: Optional[str] = None
    website: Optional[str] = None

def get_users_router(db: AsyncIOMotorDatabase, create_notification_func):
    """Create users router with dependencies"""
    
    @router.get("/users/{user_id}")
    async def get_user_profile(user_id: str):
        """Get user profile"""
        user = await db.users.find_one({"id": user_id}, {"_id": 0, "password": 0})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user["followers_count"] = len(user.get("followers", []))
        user["following_count"] = len(user.get("following", []))
        
        return user
    
    @router.put("/users/profile")
    async def update_profile(update: UserProfileUpdate, current_user: dict = Depends(get_current_user)):
        """Update user profile"""
        update_data = {k: v for k, v in update.model_dump().items() if v is not None}
        
        if update_data:
            await db.users.update_one(
                {"id": current_user["id"]},
                {"$set": update_data}
            )
        
        updated_user = await db.users.find_one({"id": current_user["id"]}, {"_id": 0, "password": 0})
        return updated_user
    
    @router.post("/users/{user_id}/follow")
    async def follow_user(user_id: str, current_user: dict = Depends(get_current_user)):
        """Follow/unfollow a user"""
        if user_id == current_user["id"]:
            raise HTTPException(status_code=400, detail="Cannot follow yourself")
        
        target_user = await db.users.find_one({"id": user_id}, {"_id": 0})
        if not target_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        is_following = current_user["id"] in target_user.get("followers", [])
        
        if is_following:
            await db.users.update_one({"id": user_id}, {"$pull": {"followers": current_user["id"]}})
            await db.users.update_one({"id": current_user["id"]}, {"$pull": {"following": user_id}})
            return {"following": False}
        else:
            await db.users.update_one({"id": user_id}, {"$addToSet": {"followers": current_user["id"]}})
            await db.users.update_one({"id": current_user["id"]}, {"$addToSet": {"following": user_id}})
            
            await create_notification_func(
                user_id, "follow", "New Follower",
                f"{current_user['username']} started following you",
                {"follower_id": current_user["id"]}
            )
            return {"following": True}
    
    @router.get("/users/{user_id}/bids")
    async def get_user_bids(user_id: str, limit: int = 20, current_user: dict = Depends(get_current_user)):
        """Get user's bid history"""
        if user_id != current_user["id"]:
            raise HTTPException(status_code=403, detail="Can only view own bids")
        
        bids = await db.bids.find(
            {"user_id": user_id},
            {"_id": 0}
        ).sort("placed_at", -1).limit(limit).to_list(limit)
        
        for bid in bids:
            product = await db.products.find_one({"id": bid["product_id"]}, {"_id": 0})
            bid["product"] = product
        
        return bids
    
    @router.get("/vendor/analytics")
    async def get_vendor_analytics(current_user: dict = Depends(require_vendor)):
        """Get vendor analytics"""
        products = await db.products.find({"vendor_id": current_user["id"]}, {"_id": 0}).to_list(100)
        purchases = await db.purchases.find({"vendor_id": current_user["id"]}, {"_id": 0}).to_list(1000)
        
        total_sales = len(purchases)
        total_revenue = sum(p.get("amount", 0) for p in purchases)
        total_views = sum(p.get("views", 0) for p in products)
        
        return {
            "total_products": len(products),
            "total_sales": total_sales,
            "total_revenue": total_revenue,
            "total_views": total_views,
            "products": products
        }
    
    @router.get("/vendor/products")
    async def get_vendor_products(current_user: dict = Depends(require_vendor)):
        """Get vendor's products"""
        products = await db.products.find({"vendor_id": current_user["id"]}, {"_id": 0}).to_list(100)
        return products
    
    return router
