"""
Notification routes
"""
from fastapi import APIRouter, HTTPException, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from .dependencies import get_current_user

router = APIRouter(tags=["Notifications"])

def get_notifications_router(db: AsyncIOMotorDatabase):
    """Create notifications router with dependencies"""
    
    @router.get("/notifications")
    async def get_notifications(current_user: dict = Depends(get_current_user), limit: int = 50):
        """Get user notifications"""
        notifications = await db.notifications.find(
            {"user_id": current_user["id"]},
            {"_id": 0}
        ).sort("created_at", -1).limit(limit).to_list(limit)
        return notifications
    
    @router.put("/notifications/{notification_id}/read")
    async def mark_notification_read(notification_id: str, current_user: dict = Depends(get_current_user)):
        """Mark notification as read"""
        await db.notifications.update_one(
            {"id": notification_id, "user_id": current_user["id"]},
            {"$set": {"read": True}}
        )
        return {"success": True}
    
    @router.put("/notifications/read-all")
    async def mark_all_notifications_read(current_user: dict = Depends(get_current_user)):
        """Mark all notifications as read"""
        await db.notifications.update_many(
            {"user_id": current_user["id"], "read": False},
            {"$set": {"read": True}}
        )
        return {"success": True}
    
    return router
