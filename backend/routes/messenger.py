"""
HyperMessenger Router - Elite IM Integration
"""
from fastapi import APIRouter, HTTPException, Depends, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

from .dependencies import get_current_user, require_admin

logger = logging.getLogger(__name__)
router = APIRouter(tags=["HyperMessenger"])

# Will be set by server.py
_hyper_messenger = None

def set_hyper_messenger(messenger):
    """Set the hyper messenger instance"""
    global _hyper_messenger
    _hyper_messenger = messenger

# ==================== MODELS ====================

class DirectMessageRequest(BaseModel):
    recipient_id: str
    content: str
    message_type: str = "text"
    attachments: List[Dict[str, Any]] = []

class GroupChatCreate(BaseModel):
    name: str
    description: str = ""
    members: List[str]

class GroupMessageRequest(BaseModel):
    group_id: str
    content: str
    message_type: str = "text"

class CallRequest(BaseModel):
    callee_id: str
    call_type: str = "voice"  # voice or video

class StatusUpdate(BaseModel):
    status_text: str
    emoji: Optional[str] = None

def get_messenger_router(db):
    """Create messenger router with database dependency"""
    
    # ==================== SIMPLE ROOM API ====================
    
    @router.get("/messenger/rooms")
    async def get_rooms(current_user: dict = Depends(get_current_user)):
        """Get all accessible rooms"""
        if not _hyper_messenger:
            raise HTTPException(status_code=503, detail="Messenger not initialized")
        
        rooms = await _hyper_messenger.get_user_rooms(current_user["id"])
        return {"rooms": rooms}
    
    @router.post("/messenger/rooms")
    async def create_room(
        name: str,
        private: bool = False,
        current_user: dict = Depends(get_current_user)
    ):
        """Create a new chat room"""
        if not _hyper_messenger:
            raise HTTPException(status_code=503, detail="Messenger not initialized")
        
        room = await _hyper_messenger.create_room(
            name,
            current_user["id"],
            private=private
        )
        return room
    
    @router.get("/messenger/rooms/{room_id}/messages")
    async def get_room_messages(
        room_id: str,
        limit: int = 50,
        current_user: dict = Depends(get_current_user)
    ):
        """Get messages from a room"""
        if not _hyper_messenger:
            raise HTTPException(status_code=503, detail="Messenger not initialized")
        
        messages = await _hyper_messenger.get_messages(room_id, limit)
        return {"messages": messages}
    
    @router.post("/messenger/rooms/{room_id}/messages")
    async def send_room_message(
        room_id: str,
        content: str,
        current_user: dict = Depends(get_current_user)
    ):
        """Send a message to a room"""
        if not _hyper_messenger:
            raise HTTPException(status_code=503, detail="Messenger not initialized")
        
        message = await _hyper_messenger.send_message(
            room_id,
            current_user["id"],
            content
        )
        return message
    
    # ==================== FRIENDS & PRESENCE ====================
    
    @router.get("/messenger/online-friends")
    async def get_online_friends(current_user: dict = Depends(get_current_user)):
        """Get list of online friends from NEXUS social platform"""
        if not _hyper_messenger:
            raise HTTPException(status_code=503, detail="Messenger not initialized")
        
        # Get user's friends from database
        user = await db.users.find_one({"id": current_user["id"]}, {"_id": 0})
        friend_ids = user.get("following", [])  # Using following as friends
        
        online_friends = await _hyper_messenger.get_online_friends(
            user_id=current_user["id"],
            friend_ids=friend_ids,
            db=db
        )
        
        return {
            "online_friends": online_friends,
            "count": len(online_friends)
        }
    
    @router.post("/messenger/status")
    async def update_status(
        status: StatusUpdate,
        current_user: dict = Depends(get_current_user)
    ):
        """Update custom status"""
        if not _hyper_messenger:
            raise HTTPException(status_code=503, detail="Messenger not initialized")
        
        await _hyper_messenger.update_custom_status(
            user_id=current_user["id"],
            status_text=status.status_text,
            emoji=status.emoji
        )
        
        return {"success": True, "status": status.status_text}
    
    # ==================== DIRECT MESSAGES ====================
    
    @router.post("/messenger/send-dm")
    async def send_direct_message(
        message: DirectMessageRequest,
        current_user: dict = Depends(get_current_user)
    ):
        """Send direct message to another user"""
        if not _hyper_messenger:
            raise HTTPException(status_code=503, detail="Messenger not initialized")
        
        result = await _hyper_messenger.send_direct_message(
            sender_id=current_user["id"],
            recipient_id=message.recipient_id,
            content=message.content,
            message_type=message.message_type,
            attachments=message.attachments
        )
        
        return result
    
    @router.get("/messenger/conversations/{user_id}")
    async def get_conversation(
        user_id: str,
        limit: int = 50,
        current_user: dict = Depends(get_current_user)
    ):
        """Get conversation history with a user"""
        if not _hyper_messenger:
            raise HTTPException(status_code=503, detail="Messenger not initialized")
        
        conversation_id = _hyper_messenger._get_conversation_id(
            current_user["id"],
            user_id
        )
        
        messages = await _hyper_messenger.get_conversation_history(
            conversation_id=conversation_id,
            limit=limit
        )
        
        return {
            "conversation_id": conversation_id,
            "messages": messages,
            "count": len(messages)
        }
    
    # ==================== GROUP CHATS ====================
    
    @router.post("/messenger/create-group")
    async def create_group(
        group: GroupChatCreate,
        current_user: dict = Depends(get_current_user)
    ):
        """Create a group chat"""
        if not _hyper_messenger:
            raise HTTPException(status_code=503, detail="Messenger not initialized")
        
        result = await _hyper_messenger.create_group_chat(
            creator_id=current_user["id"],
            name=group.name,
            members=group.members,
            description=group.description
        )
        
        return result
    
    @router.post("/messenger/send-group-message")
    async def send_group_message(
        message: GroupMessageRequest,
        current_user: dict = Depends(get_current_user)
    ):
        """Send message to group chat"""
        if not _hyper_messenger:
            raise HTTPException(status_code=503, detail="Messenger not initialized")
        
        result = await _hyper_messenger.send_group_message(
            sender_id=current_user["id"],
            group_id=message.group_id,
            content=message.content,
            message_type=message.message_type
        )
        
        return result
    
    @router.get("/messenger/groups")
    async def get_my_groups(current_user: dict = Depends(get_current_user)):
        """Get user's group chats"""
        if not _hyper_messenger:
            raise HTTPException(status_code=503, detail="Messenger not initialized")
        
        user_groups = [
            group for group in _hyper_messenger.group_chats.values()
            if current_user["id"] in group["members"]
        ]
        
        return {
            "groups": user_groups,
            "count": len(user_groups)
        }
    
    # ==================== VOICE/VIDEO CALLS ====================
    
    @router.post("/messenger/initiate-call")
    async def initiate_call(
        call: CallRequest,
        current_user: dict = Depends(get_current_user)
    ):
        """Initiate voice or video call"""
        if not _hyper_messenger:
            raise HTTPException(status_code=503, detail="Messenger not initialized")
        
        result = await _hyper_messenger.initiate_call(
            caller_id=current_user["id"],
            callee_id=call.callee_id,
            call_type=call.call_type
        )
        
        return result
    
    # ==================== STATISTICS ====================
    
    @router.get("/messenger/stats")
    async def get_messenger_stats(current_user: dict = Depends(require_admin)):
        """Get messenger statistics"""
        if not _hyper_messenger:
            raise HTTPException(status_code=503, detail="Messenger not initialized")
        
        stats = _hyper_messenger.get_stats()
        return stats
    
    return router
