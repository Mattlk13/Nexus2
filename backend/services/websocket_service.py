"""
NEXUS WebSocket Service
Real-time communication for chat, notifications, and live updates
"""
from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List, Set
import json
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

class ConnectionManager:
    """Manage WebSocket connections"""
    
    def __init__(self):
        # user_id -> Set of WebSocket connections
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        # room_id -> Set of user_ids
        self.rooms: Dict[str, Set[str]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str):
        """Connect a user"""
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        self.active_connections[user_id].add(websocket)
        logger.info(f"User {user_id} connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket, user_id: str):
        """Disconnect a user"""
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        logger.info(f"User {user_id} disconnected")
    
    async def send_personal_message(self, message: dict, user_id: str):
        """Send message to specific user"""
        if user_id in self.active_connections:
            disconnected = set()
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(message)
                except:
                    disconnected.add(connection)
            
            # Clean up disconnected websockets
            for conn in disconnected:
                self.active_connections[user_id].discard(conn)
    
    async def broadcast_to_room(self, message: dict, room_id: str):
        """Broadcast message to all users in a room"""
        if room_id in self.rooms:
            for user_id in self.rooms[room_id]:
                await self.send_personal_message(message, user_id)
    
    async def broadcast_to_friends(self, message: dict, user_id: str, friend_ids: List[str]):
        """Broadcast message to user's friends"""
        for friend_id in friend_ids:
            await self.send_personal_message(message, friend_id)
    
    def join_room(self, room_id: str, user_id: str):
        """Add user to a room"""
        if room_id not in self.rooms:
            self.rooms[room_id] = set()
        self.rooms[room_id].add(user_id)
    
    def leave_room(self, room_id: str, user_id: str):
        """Remove user from a room"""
        if room_id in self.rooms:
            self.rooms[room_id].discard(user_id)
            if not self.rooms[room_id]:
                del self.rooms[room_id]

# Global connection manager
manager = ConnectionManager()

async def handle_websocket_message(websocket: WebSocket, user_id: str, db):
    """Handle incoming WebSocket messages"""
    from services.social_network_service import create_social_network_service, Message
    social_service = create_social_network_service(db)
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_json()
            message_type = data.get("type")
            
            if message_type == "ping":
                # Keep-alive ping
                await websocket.send_json({"type": "pong"})
            
            elif message_type == "chat_message":
                # Direct message
                to_user_id = data.get("to_user_id")
                content = data.get("content")
                media = data.get("media", [])
                
                # Save to database
                message = Message(
                    from_user_id=user_id,
                    to_user_id=to_user_id,
                    content=content,
                    media=media
                )
                result = await social_service.send_message(message)
                
                # Send to recipient in real-time
                await manager.send_personal_message({
                    "type": "new_message",
                    "message": result["message"]
                }, to_user_id)
                
                # Confirm to sender
                await websocket.send_json({
                    "type": "message_sent",
                    "message": result["message"]
                })
            
            elif message_type == "typing":
                # Typing indicator
                to_user_id = data.get("to_user_id")
                await manager.send_personal_message({
                    "type": "user_typing",
                    "user_id": user_id
                }, to_user_id)
            
            elif message_type == "read_receipt":
                # Mark messages as read
                from_user_id = data.get("from_user_id")
                await social_service.mark_messages_read(user_id, from_user_id)
                
                # Notify sender
                await manager.send_personal_message({
                    "type": "messages_read",
                    "user_id": user_id
                }, from_user_id)
            
            elif message_type == "join_room":
                # Join a chat room (for group chats, future feature)
                room_id = data.get("room_id")
                manager.join_room(room_id, user_id)
                await websocket.send_json({
                    "type": "room_joined",
                    "room_id": room_id
                })
            
            elif message_type == "leave_room":
                # Leave a chat room
                room_id = data.get("room_id")
                manager.leave_room(room_id, user_id)
                await websocket.send_json({
                    "type": "room_left",
                    "room_id": room_id
                })
            
            else:
                logger.warning(f"Unknown message type: {message_type}")
    
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket, user_id)

async def broadcast_post_update(post: dict, db):
    """Broadcast new post to user's friends"""
    # Get user's friends
    user = await db.users.find_one({"id": post["user_id"]}, {"_id": 0, "friends": 1})
    if user and user.get("friends"):
        await manager.broadcast_to_friends(
            {
                "type": "new_post",
                "post": post
            },
            post["user_id"],
            user["friends"]
        )

async def broadcast_notification(notification: dict):
    """Broadcast notification to user"""
    await manager.send_personal_message({
        "type": "notification",
        "notification": notification
    }, notification["user_id"])
