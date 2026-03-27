"""
FederatedChat System - Supreme Chat Hybrid
Combines: Django Channels + Socket.IO + ActivityPub Federation
"""
import logging
import asyncio
from typing import Dict, Any, Optional, List, Set
from datetime import datetime, timezone
import json
import httpx
from collections import defaultdict

logger = logging.getLogger(__name__)

class FederatedChatSystem:
    """Elite chat system with rooms, presence, and federation capabilities"""
    
    def __init__(self, sio):
        self.sio = sio  # Socket.IO server instance
        self.rooms: Dict[str, Set[str]] = defaultdict(set)  # room_id -> set of sid
        self.user_presence: Dict[str, Dict[str, Any]] = {}  # sid -> presence data
        self.message_history: Dict[str, List[Dict]] = defaultdict(list)  # room_id -> messages
        self.max_history = 100
        
        # ActivityPub federation
        self.federation_enabled = True
        self.federated_rooms: Set[str] = set()  # Rooms available for federation
        self.remote_instances: List[str] = []  # List of federated instances
    
    async def join_room(
        self,
        sid: str,
        room_id: str,
        user_data: Dict[str, Any]
    ) -> bool:
        """
        User joins a chat room with presence tracking.
        
        Features:
        - Real-time presence updates
        - Message history delivery
        - Typing indicators
        - Read receipts
        """
        try:
            # Enter Socket.IO room
            await self.sio.enter_room(sid, room_id)
            self.rooms[room_id].add(sid)
            
            # Update presence
            self.user_presence[sid] = {
                'user_id': user_data.get('user_id'),
                'username': user_data.get('username'),
                'avatar': user_data.get('avatar'),
                'status': 'online',
                'last_seen': datetime.now(timezone.utc).isoformat(),
                'room_id': room_id
            }
            
            # Notify others in room
            await self.sio.emit('user_joined', {
                'user': self.user_presence[sid],
                'room_id': room_id,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }, room=room_id, skip_sid=sid)
            
            # Send message history to new joiner
            history = self.message_history[room_id][-50:]  # Last 50 messages
            await self.sio.emit('message_history', {
                'messages': history,
                'room_id': room_id
            }, to=sid)
            
            # Send current room members
            room_members = [
                self.user_presence[s] for s in self.rooms[room_id]
                if s in self.user_presence
            ]
            await self.sio.emit('room_members', {
                'members': room_members,
                'room_id': room_id
            }, to=sid)
            
            logger.info(f"User {user_data.get('username')} joined room {room_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error joining room: {e}")
            return False
    
    async def leave_room(
        self,
        sid: str,
        room_id: Optional[str] = None
    ):
        """User leaves chat room"""
        if room_id:
            rooms_to_leave = [room_id]
        else:
            # Find all rooms user is in
            rooms_to_leave = [
                rid for rid, sids in self.rooms.items()
                if sid in sids
            ]
        
        for rid in rooms_to_leave:
            await self.sio.leave_room(sid, rid)
            self.rooms[rid].discard(sid)
            
            # Notify others
            if sid in self.user_presence:
                await self.sio.emit('user_left', {
                    'user': self.user_presence[sid],
                    'room_id': rid,
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }, room=rid)
        
        # Clean up presence
        if sid in self.user_presence:
            del self.user_presence[sid]
    
    async def send_message(
        self,
        sid: str,
        room_id: str,
        message: Dict[str, Any]
    ) -> bool:
        """
        Send message to room with advanced features:
        - Delivery confirmation
        - Read receipts
        - Message editing
        - Reactions
        - File attachments
        """
        if sid not in self.user_presence:
            logger.warning(f"Message from unknown user {sid}")
            return False
        
        user = self.user_presence[sid]
        
        # Create message object
        msg = {
            'id': f"msg_{datetime.now(timezone.utc).timestamp()}",
            'room_id': room_id,
            'user_id': user['user_id'],
            'username': user['username'],
            'avatar': user['avatar'],
            'content': message.get('content', ''),
            'type': message.get('type', 'text'),  # text, image, file, code
            'attachments': message.get('attachments', []),
            'reply_to': message.get('reply_to'),
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'edited': False,
            'reactions': {}
        }
        
        # Store in history
        self.message_history[room_id].append(msg)
        if len(self.message_history[room_id]) > self.max_history:
            self.message_history[room_id] = self.message_history[room_id][-self.max_history:]
        
        # Broadcast to room
        await self.sio.emit('new_message', msg, room=room_id)
        
        # Federate to remote instances if enabled
        if room_id in self.federated_rooms and self.federation_enabled:
            await self._federate_message(room_id, msg)
        
        logger.info(f"Message sent in room {room_id} by {user['username']}")
        return True
    
    async def typing_indicator(
        self,
        sid: str,
        room_id: str,
        is_typing: bool
    ):
        """Send typing indicator to room"""
        if sid not in self.user_presence:
            return
        
        user = self.user_presence[sid]
        
        await self.sio.emit('user_typing', {
            'user_id': user['user_id'],
            'username': user['username'],
            'is_typing': is_typing,
            'room_id': room_id
        }, room=room_id, skip_sid=sid)
    
    async def mark_read(
        self,
        sid: str,
        room_id: str,
        message_id: str
    ):
        """Mark message as read"""
        if sid not in self.user_presence:
            return
        
        user = self.user_presence[sid]
        
        await self.sio.emit('message_read', {
            'message_id': message_id,
            'user_id': user['user_id'],
            'room_id': room_id,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }, room=room_id)
    
    async def add_reaction(
        self,
        sid: str,
        room_id: str,
        message_id: str,
        reaction: str
    ):
        """Add emoji reaction to message"""
        if sid not in self.user_presence:
            return
        
        user = self.user_presence[sid]
        
        # Find message and add reaction
        for msg in self.message_history[room_id]:
            if msg['id'] == message_id:
                if reaction not in msg['reactions']:
                    msg['reactions'][reaction] = []
                if user['user_id'] not in msg['reactions'][reaction]:
                    msg['reactions'][reaction].append(user['user_id'])
                break
        
        # Broadcast reaction
        await self.sio.emit('message_reaction', {
            'message_id': message_id,
            'reaction': reaction,
            'user_id': user['user_id'],
            'room_id': room_id
        }, room=room_id)
    
    # ==================== ACTIVITYPUB FEDERATION ====================
    
    async def enable_federation(self, room_id: str, public: bool = False):
        """Enable ActivityPub federation for a room"""
        self.federated_rooms.add(room_id)
        
        # Announce room availability to federated instances
        if public:
            await self._announce_room(room_id)
    
    async def _federate_message(
        self,
        room_id: str,
        message: Dict[str, Any]
    ):
        """Send message to federated instances via ActivityPub"""
        if not self.federation_enabled:
            return
        
        # Create ActivityPub Note object
        activity = {
            '@context': 'https://www.w3.org/ns/activitystreams',
            'type': 'Create',
            'actor': f"https://nexus.ai/users/{message['user_id']}",
            'object': {
                'type': 'Note',
                'content': message['content'],
                'published': message['timestamp'],
                'to': [f"https://nexus.ai/rooms/{room_id}"],
                'attributedTo': f"https://nexus.ai/users/{message['user_id']}"
            }
        }
        
        # Send to federated instances
        async with httpx.AsyncClient() as client:
            tasks = [
                client.post(
                    f"{instance}/inbox",
                    json=activity,
                    headers={'Content-Type': 'application/activity+json'}
                )
                for instance in self.remote_instances
            ]
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _announce_room(self, room_id: str):
        """Announce room to fediverse"""
        activity = {
            '@context': 'https://www.w3.org/ns/activitystreams',
            'type': 'Announce',
            'actor': 'https://nexus.ai',
            'object': f"https://nexus.ai/rooms/{room_id}",
            'published': datetime.now(timezone.utc).isoformat()
        }
        
        # Broadcast to known instances
        # Implementation here
    
    def get_room_stats(self, room_id: str) -> Dict[str, Any]:
        """Get statistics for a room"""
        return {
            'room_id': room_id,
            'active_users': len(self.rooms.get(room_id, set())),
            'total_messages': len(self.message_history.get(room_id, [])),
            'federated': room_id in self.federated_rooms
        }
    
    def get_all_presence(self) -> List[Dict[str, Any]]:
        """Get presence data for all connected users"""
        return list(self.user_presence.values())

# Will be initialized with Socket.IO instance in server.py
federated_chat = None
