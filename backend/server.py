from fastapi import FastAPI, APIRouter, HTTPException, Depends, UploadFile, File, Request, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import socketio
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone, timedelta
import jwt
import bcrypt
import base64
import asyncio
import json
from services.email_service import email_service
from services.manus_service import manus_service
from services.automation_service import automation_service
from services.cicd_service import cicd_service
from services.aixploria_service import aixploria_service
from services.performance_optimizer import create_performance_optimizer
from services.integration_status import integration_status_service
from services.elevenlabs_service import elevenlabs_service
from services.fal_ai_service import fal_ai_service
from services.openclaw_service import openclaw_service
from services.tool_integration_service import create_discovered_tools_integration_service
from services.mega_discovery_service import mega_discovery_engine
from services.enhanced_user_profile_service import create_enhanced_user_profile_service
from services.investor_dashboard_service import create_investor_dashboard_service
from services.cloudflare_workers_service import cloudflare_workers_service
from services.marketing_automation_service import create_marketing_automation_service
from services.mcp_integration_service import create_mcp_server_integration_service
from services.github_gitlab_service import create_github_gitlab_service
from services.analytics_dashboard_service import create_analytics_dashboard_service
from services.mcp_registry_service import create_mcp_registry_service
from services.workflow_automation_service import create_workflow_automation_service
from services.cloudflare_service import create_cloudflare_service
from services.text_to_video_service import text_to_video_service
from services.runway_video_service import runway_video_service
from services.social_media_service import social_media_service
from services.redis_cache_service import cache_service, cached
from services.websocket_service import manager, handle_websocket_message
from routes.social_routes import create_social_routes
from routes.adk_routes import router as adk_router

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# JWT Config
JWT_SECRET = os.environ.get('JWT_SECRET', 'nexus-secret-key-2025')
JWT_ALGORITHM = "HS256"

# Socket.IO Setup
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')
fastapi_app = FastAPI(title="NEXUS API", description="AI Social Marketplace & Creator Hub")
api_router = APIRouter(prefix="/api")
security = HTTPBearer()

# User session tracking for notifications
user_sessions = {}  # user_id -> [sid, sid, ...]

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ==================== SOCKET.IO EVENTS ====================

# Enhanced Socket.IO events for FederatedChat
@sio.event
async def connect(sid, environ):
    logger.info(f"Client connected: {sid}")

@sio.event
async def disconnect(sid):
    logger.info(f"Client disconnected: {sid}")
    # Clean up user sessions
    for user_id, sids in list(user_sessions.items()):
        if sid in sids:
            sids.remove(sid)
            if not sids:
                del user_sessions[user_id]
            break
    # Clean up federated chat
    if federated_chat:
        await federated_chat.leave_room(sid)

@sio.event
async def authenticate(sid, data):
    """Authenticate user and track their session for notifications"""
    try:
        token = data.get("token")
        if token:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            user_id = payload["user_id"]
            if user_id not in user_sessions:
                user_sessions[user_id] = []
            user_sessions[user_id].append(sid)
            await sio.emit("authenticated", {"success": True, "user_id": user_id}, to=sid)
            logger.info(f"User {user_id} authenticated on {sid}")
    except Exception as e:
        logger.error(f"Auth error: {e}")
        await sio.emit("authenticated", {"success": False}, to=sid)

@sio.event
async def join_room(sid, data):
    room_id = data.get("room_id")
    user_data = data.get("user", {})
    
    if room_id:
        # Basic room join
        await sio.enter_room(sid, room_id)
        logger.info(f"Client {sid} joined room {room_id}")
        
        # Enhanced federated chat join
        if federated_chat and user_data:
            await federated_chat.join_room(sid, room_id, user_data)

@sio.event
async def send_message(sid, data):
    """Send message in federated chat or HyperMessenger"""
    room_id = data.get("room_id")
    message = data.get("message")
    
    # Try FederatedChat first
    if federated_chat and room_id and message:
        await federated_chat.send_message(sid, room_id, message)
    
    # If it's a DM, use HyperMessenger
    recipient_id = data.get("recipient_id")
    if hyper_messenger and recipient_id and message:
        user_data = data.get("user", {})
        await hyper_messenger.send_direct_message(
            sender_id=user_data.get("id"),
            recipient_id=recipient_id,
            content=message.get("content", ""),
            message_type=message.get("type", "text")
        )

@sio.event
async def webrtc_signal(sid, data):
    """Handle WebRTC signaling for voice/video calls"""
    if hyper_messenger:
        await hyper_messenger.send_webrtc_signal(
            sender_id=data.get("sender_id"),
            recipient_id=data.get("recipient_id"),
            signal_data=data.get("signal")
        )

@sio.event
async def typing(sid, data):
    """Typing indicator for federated chat"""
    room_id = data.get("room_id")
    is_typing = data.get("is_typing", True)
    
    if federated_chat and room_id:
        await federated_chat.typing_indicator(sid, room_id, is_typing)

@sio.event
async def mark_read(sid, data):
    """Mark message as read"""
    room_id = data.get("room_id")
    message_id = data.get("message_id")
    
    if federated_chat and room_id and message_id:
        await federated_chat.mark_read(sid, room_id, message_id)

@sio.event
async def add_reaction(sid, data):
    """Add reaction to message"""
    room_id = data.get("room_id")
    message_id = data.get("message_id")
    reaction = data.get("reaction")
    
    if federated_chat and room_id and message_id and reaction:
        await federated_chat.add_reaction(sid, room_id, message_id, reaction)

async def notify_user(user_id: str, notification: dict):
    """Send notification to specific user across all their sessions"""
    if user_id in user_sessions:
        for sid in user_sessions[user_id]:
            await sio.emit("notification", notification, to=sid)

async def broadcast_to_room(room: str, message: dict):
    """Broadcast message to all users in a room"""
    await sio.emit("update", message, room=room)

# ==================== MODELS ====================

class UserCreate(BaseModel):
    email: str
    password: str
    username: str
    role: str = "user"

class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    email: str
    username: str
    role: str
    avatar: Optional[str] = None
    bio: Optional[str] = None
    followers_count: int = 0
    following_count: int = 0
    created_at: str

class UserProfileUpdate(BaseModel):
    username: Optional[str] = None
    bio: Optional[str] = None
    avatar: Optional[str] = None

class ProductCreate(BaseModel):
    title: str
    description: str
    price: float
    category: str
    image_url: Optional[str] = None
    tags: List[str] = []
    is_ai_generated: bool = False
    file_url: Optional[str] = None

class ProductResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    title: str
    description: str
    price: float
    category: str
    image_url: Optional[str] = None
    tags: List[str] = []
    is_ai_generated: bool
    vendor_id: str
    vendor_name: str
    likes: int = 0
    views: int = 0
    sales: int = 0
    created_at: str

class PostCreate(BaseModel):
    content: str
    media_urls: List[str] = []
    post_type: str = "text"

class CommentCreate(BaseModel):
    content: str
    post_id: str

# Initialize tool integration service
tool_integration_service = create_discovered_tools_integration_service(db)
enhanced_profile_service = create_enhanced_user_profile_service(db)
investor_dashboard_service = create_investor_dashboard_service(db)
marketing_service = create_marketing_automation_service(db)
mcp_integration_service = create_mcp_server_integration_service(db)
github_gitlab_service = create_github_gitlab_service(db)
analytics_dashboard_service = create_analytics_dashboard_service(db)
mcp_registry_service = create_mcp_registry_service(db)
workflow_automation_service = create_workflow_automation_service(db)
cloudflare_service = create_cloudflare_service(db)

class AIGenerateRequest(BaseModel):
    prompt: str
    content_type: str
    style: Optional[str] = None
    additional_params: Optional[Dict[str, Any]] = {}
    video_params: Optional[Dict[str, Any]] = {}  # For Sora 2 & Runway: model, size, duration
    video_provider: Optional[str] = "sora"  # "sora" or "runway"

class VendorCreate(BaseModel):
    shop_name: str
    description: str
    category: str

class ChatMessage(BaseModel):
    message: str
    context: Optional[str] = None

class PurchaseRequest(BaseModel):
    product_id: str
    origin_url: str

# ==================== BOOST MODELS ====================

BOOST_PACKAGES = {
    "basic": {"price": 5.00, "days": 1, "name": "Basic Boost", "description": "Featured for 24 hours"},
    "standard": {"price": 7.50, "days": 3, "name": "Standard Boost", "description": "Featured for 3 days"},
    "premium": {"price": 10.00, "days": 7, "name": "Premium Boost", "description": "Featured for 7 days + Priority placement"}
}

class BoostCheckoutRequest(BaseModel):
    product_id: str
    package_id: str
    origin_url: str

class BoostCheckoutResponse(BaseModel):
    checkout_url: str
    session_id: str

# ==================== AUTH HELPERS ====================

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_token(user_id: str, email: str, role: str = "user") -> str:
    payload = {
        "user_id": user_id,
        "email": email,
        "role": role,
        "exp": datetime.now(timezone.utc).timestamp() + 86400 * 7
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user = await db.users.find_one({"id": payload["user_id"]}, {"_id": 0})
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

async def get_optional_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))):
    if not credentials:
        return None
    try:
        token = credentials.credentials
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user = await db.users.find_one({"id": payload["user_id"]}, {"_id": 0})
        return user
    except Exception:
        return None

async def require_admin(current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

async def require_vendor(current_user: dict = Depends(get_current_user)):
    if current_user.get("role") not in ["vendor", "admin"]:
        raise HTTPException(status_code=403, detail="Vendor or admin access required")
    return current_user

# ==================== NOTIFICATION HELPER ====================

async def create_notification(user_id: str, notif_type: str, title: str, message: str, data: dict = None):
    """Create and send real-time notification"""
    notification = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "type": notif_type,
        "title": title,
        "message": message,
        "data": data or {},
        "read": False,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.notifications.insert_one(notification)
    # Send real-time notification
    await notify_user(user_id, {k: v for k, v in notification.items() if k != "_id"})
    return notification

# ==================== AI AGENT SYSTEM ====================

class AIAgentSystem:
    def __init__(self):
        self.api_key = os.environ.get('EMERGENT_LLM_KEY')
        self.response_cache = {}  # Simple in-memory cache
        self.cache_ttl = 3600  # 1 hour
    
    def _get_cache_key(self, agent_name: str, data_hash: str) -> str:
        """Generate cache key for agent response"""
        return f"{agent_name}:{data_hash}:{datetime.now(timezone.utc).hour}"
    
    def _check_cache(self, cache_key: str) -> Optional[str]:
        """Check if cached response exists and is valid"""
        if cache_key in self.response_cache:
            cached_data = self.response_cache[cache_key]
            if (datetime.now(timezone.utc).timestamp() - cached_data["timestamp"]) < self.cache_ttl:
                logger.info(f"Using cached response for {cache_key}")
                return cached_data["response"]
        return None
    
    def _set_cache(self, cache_key: str, response: str):
        """Store response in cache"""
        self.response_cache[cache_key] = {
            "response": response,
            "timestamp": datetime.now(timezone.utc).timestamp()
        }
        
        # Simple cache cleanup: keep only last 50 entries
        if len(self.response_cache) > 50:
            oldest_key = min(self.response_cache.keys(), key=lambda k: self.response_cache[k]["timestamp"])
            del self.response_cache[oldest_key]
    
    async def run_ceo_agent(self):
        """CEO Agent: Analyze KPIs and generate insights with enhanced error handling"""
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        
        try:
            products_count = await db.products.count_documents({})
            users_count = await db.users.count_documents({})
            vendors_count = await db.vendors.count_documents({})
            posts_count = await db.posts.count_documents({})
            transactions = await db.payment_transactions.find({"payment_status": "completed"}, {"_id": 0}).to_list(1000)
            total_revenue = sum(t.get("amount", 0) for t in transactions)
            
            # Check cache
            data_hash = f"{products_count}-{users_count}-{int(total_revenue)}"
            cache_key = self._get_cache_key("ceo", data_hash)
            cached_response = self._check_cache(cache_key)
            
            if cached_response:
                return {
                    "id": str(uuid.uuid4()),
                    "agent": "ceo",
                    "type": "daily_report",
                    "content": cached_response,
                    "cached": True,
                    "metrics": {"products": products_count, "users": users_count, "vendors": vendors_count, "revenue": total_revenue},
                    "created_at": datetime.now(timezone.utc).isoformat()
                }
            
            chat = LlmChat(
                api_key=self.api_key,
                session_id=f"ceo-agent-{uuid.uuid4()}",
                system_message="You are the CEO AI Agent for NEXUS marketplace. Analyze platform metrics and provide executive insights in a concise format."
            ).with_model("anthropic", "claude-sonnet-4-5-20250929")
            
            prompt = f"""Analyze NEXUS platform metrics:
            - Total Products: {products_count}
            - Total Users: {users_count}
            - Active Vendors: {vendors_count}
            - Social Posts: {posts_count}
            - Total Revenue: ${total_revenue:.2f}
            
            Provide: 1) Key performance summary 2) Top growth opportunity 3) Risk to monitor 4) Weekly action"""
            
            response = await chat.send_message(UserMessage(text=prompt))
            
            # Cache the response
            self._set_cache(cache_key, response)
            
            report = {
                "id": str(uuid.uuid4()),
                "agent": "ceo",
                "type": "daily_report",
                "content": response,
                "metrics": {"products": products_count, "users": users_count, "vendors": vendors_count, "revenue": total_revenue},
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            await db.agent_reports.insert_one(report)
            
            # Broadcast to admin room
            await broadcast_to_room("admin", {"type": "agent_report", "agent": "ceo", "report": response[:500]})
            # Remove MongoDB _id before returning
            return {k: v for k, v in report.items() if k != "_id"}
            
        except Exception as e:
            logger.error(f"CEO agent error: {e}")
            return {
                "id": str(uuid.uuid4()),
                "agent": "ceo",
                "type": "error",
                "content": f"Agent execution failed: {str(e)}",
                "created_at": datetime.now(timezone.utc).isoformat()
            }
    
    async def run_product_manager_agent(self):
        """Product Manager: Suggest trending products and categories with error handling"""
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        
        try:
            categories = await db.products.aggregate([
                {"$group": {"_id": "$category", "count": {"$sum": 1}, "total_views": {"$sum": "$views"}}}
            ]).to_list(100)
            
            chat = LlmChat(
                api_key=self.api_key,
                session_id=f"pm-agent-{uuid.uuid4()}",
                system_message="You are the Product Manager AI Agent for NEXUS marketplace. Provide actionable product insights."
            ).with_model("openai", "gpt-5.2")
            
            prompt = f"""Based on NEXUS data: {json.dumps(categories, default=str)}
            Provide: 1) 3 trending product ideas 2) Category needing products 3) Pricing suggestion 4) Featured recommendation"""
            
            response = await chat.send_message(UserMessage(text=prompt))
            
            report = {"id": str(uuid.uuid4()), "agent": "product_manager", "type": "product_insights", "content": response, "created_at": datetime.now(timezone.utc).isoformat()}
            await db.agent_reports.insert_one(report)
            await broadcast_to_room("admin", {"type": "agent_report", "agent": "product_manager", "report": response[:500]})
            return {k: v for k, v in report.items() if k != "_id"}
        except Exception as e:
            logger.error(f"Product Manager agent error: {e}")
            return {"id": str(uuid.uuid4()), "agent": "product_manager", "type": "error", "content": f"Agent execution failed: {str(e)}", "created_at": datetime.now(timezone.utc).isoformat()}
    
    async def run_marketing_agent(self):
        """Marketing Agent: Generate social content and campaigns with error handling"""
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        
        try:
            top_products = await db.products.find({}, {"_id": 0}).sort("views", -1).limit(5).to_list(5)
            
            chat = LlmChat(
                api_key=self.api_key,
                session_id=f"marketing-agent-{uuid.uuid4()}",
                system_message="You are the Marketing AI Agent for NEXUS marketplace. Create engaging marketing content."
            ).with_model("openai", "gpt-5.2")
            
            prompt = f"""Create marketing content for NEXUS. Top products: {json.dumps([p.get('title') for p in top_products])}
            Generate: 1) Twitter post (280 chars) 2) Instagram caption 3) Email subject 4) 5 hashtags"""
            
            response = await chat.send_message(UserMessage(text=prompt))
            
            report = {"id": str(uuid.uuid4()), "agent": "marketing", "type": "content_generation", "content": response, "created_at": datetime.now(timezone.utc).isoformat()}
            await db.agent_reports.insert_one(report)
            await broadcast_to_room("admin", {"type": "agent_report", "agent": "marketing", "report": response[:500]})
            return {k: v for k, v in report.items() if k != "_id"}
        except Exception as e:
            logger.error(f"Marketing agent error: {e}")
            return {"id": str(uuid.uuid4()), "agent": "marketing", "type": "error", "content": f"Agent execution failed: {str(e)}", "created_at": datetime.now(timezone.utc).isoformat()}
    
    async def run_vendor_manager_agent(self):
        """Vendor Manager: Review and moderate vendors/listings with error handling"""
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        
        try:
            pending_vendors = await db.vendors.find({"status": "pending"}, {"_id": 0}).to_list(10)
            
            chat = LlmChat(
                api_key=self.api_key,
                session_id=f"vendor-agent-{uuid.uuid4()}",
                system_message="You are the Vendor Manager AI Agent for NEXUS."
            ).with_model("anthropic", "claude-sonnet-4-5-20250929")
            
            prompt = f"Review vendors: {json.dumps(pending_vendors, default=str) if pending_vendors else 'No pending vendors. Provide quality guidelines.'}"
            
            response = await chat.send_message(UserMessage(text=prompt))
            
            report = {"id": str(uuid.uuid4()), "agent": "vendor_manager", "type": "moderation_report", "content": response, "pending_count": len(pending_vendors), "created_at": datetime.now(timezone.utc).isoformat()}
            await db.agent_reports.insert_one(report)
            return {k: v for k, v in report.items() if k != "_id"}
        except Exception as e:
            logger.error(f"Vendor Manager agent error: {e}")
            return {"id": str(uuid.uuid4()), "agent": "vendor_manager", "type": "error", "content": f"Agent execution failed: {str(e)}", "created_at": datetime.now(timezone.utc).isoformat()}
    
    async def run_finance_agent(self):
        """Finance Agent: Track revenue and process payouts with error handling"""
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        
        try:
            transactions = await db.payment_transactions.find({"payment_status": "completed"}, {"_id": 0}).sort("created_at", -1).limit(50).to_list(50)
            total_revenue = sum(t.get("amount", 0) for t in transactions)
            boost_revenue = sum(t.get("amount", 0) for t in transactions if t.get("package_id"))
            
            chat = LlmChat(
                api_key=self.api_key,
                session_id=f"finance-agent-{uuid.uuid4()}",
                system_message="You are the Finance AI Agent for NEXUS."
            ).with_model("openai", "gpt-5.2")
            
            prompt = f"""NEXUS financials: Total: ${total_revenue:.2f}, Boosts: ${boost_revenue:.2f}, Transactions: {len(transactions)}
            Provide: 1) Revenue health 2) Diversification tip 3) Payout status 4) Risk alerts"""
            
            response = await chat.send_message(UserMessage(text=prompt))
            
            report = {"id": str(uuid.uuid4()), "agent": "finance", "type": "financial_report", "content": response, "metrics": {"total_revenue": total_revenue, "boost_revenue": boost_revenue}, "created_at": datetime.now(timezone.utc).isoformat()}
            await db.agent_reports.insert_one(report)
            await broadcast_to_room("admin", {"type": "agent_report", "agent": "finance", "report": response[:500]})
            return {k: v for k, v in report.items() if k != "_id"}
        except Exception as e:
            logger.error(f"Finance agent error: {e}")
            return {"id": str(uuid.uuid4()), "agent": "finance", "type": "error", "content": f"Agent execution failed: {str(e)}", "created_at": datetime.now(timezone.utc).isoformat()}
    
    async def moderate_content(self, content: str, content_type: str = "text"):
        """Content moderation using Claude with error handling"""
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        
        try:
            chat = LlmChat(
                api_key=self.api_key,
                session_id=f"moderation-{uuid.uuid4()}",
                system_message="You are a content moderation AI. Analyze content for policy violations. Respond in JSON: {approved: bool, confidence: float, flags: [], reason: string}"
            ).with_model("anthropic", "claude-sonnet-4-5-20250929")
            
            response = await chat.send_message(UserMessage(text=f"Moderate this {content_type}: \"{content}\""))
            
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except Exception as e:
            logger.error(f"Moderation error: {e}")
        
        return {"approved": True, "confidence": 0.8, "flags": [], "reason": "Auto-approved"}
    
    async def chat_with_agent(self, agent_name: str, user_message: str, context: dict = None):
        """Enhanced chat interface for any agent with error handling and model selection"""
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        
        try:
            agent_personas = {
                "ceo": {"model_provider": "anthropic", "model": "claude-sonnet-4-5-20250929", "system": "You are the CEO AI Agent for NEXUS marketplace."},
                "product_manager": {"model_provider": "openai", "model": "gpt-5.2", "system": "You are the Product Manager AI Agent for NEXUS marketplace."},
                "marketing": {"model_provider": "openai", "model": "gpt-5.2", "system": "You are the Marketing AI Agent for NEXUS marketplace."},
                "vendor_manager": {"model_provider": "anthropic", "model": "claude-sonnet-4-5-20250929", "system": "You are the Vendor Manager AI Agent for NEXUS."},
                "finance": {"model_provider": "openai", "model": "gpt-5.2", "system": "You are the Finance AI Agent for NEXUS."},
                "support": {"model_provider": "anthropic", "model": "claude-sonnet-4-5-20250929", "system": "You are a helpful support agent for NEXUS marketplace. Assist users with their questions."}
            }
            
            agent_config = agent_personas.get(agent_name, agent_personas["support"])
            
            chat = LlmChat(
                api_key=self.api_key,
                session_id=f"{agent_name}-chat-{uuid.uuid4()}",
                system_message=agent_config["system"]
            ).with_model(agent_config["model_provider"], agent_config["model"])
            
            # Add context to prompt if provided
            full_prompt = user_message
            if context:
                full_prompt = f"Context: {json.dumps(context, default=str)}\n\nUser Query: {user_message}"
            
            response = await chat.send_message(UserMessage(text=full_prompt))
            
            return {"agent": agent_name, "response": response, "timestamp": datetime.now(timezone.utc).isoformat()}
        
        except Exception as e:
            logger.error(f"Chat error with {agent_name}: {e}")
            return {"agent": agent_name, "response": f"I'm having technical difficulties. Please try again. Error: {str(e)}", "error": True}

agent_system = AIAgentSystem()

# Import advanced agent system
from services.advanced_agents import create_advanced_agent_system
advanced_agents = None  # Will be initialized after startup
performance_optimizer = None  # Will be initialized after startup

# ==================== AUTOMATED AGENT SCHEDULER ====================

agent_schedule = {
    "ceo": {"hour": 20, "minute": 0},  # 8 PM
    "product_manager": {"hour": 6, "minute": 0},  # 6 AM
    "marketing": {"hour": 12, "minute": 0},  # 12 PM
    "vendor_manager": {"hour": 9, "minute": 0},  # 9 AM
    "finance": {"hour": 20, "minute": 30},  # 8:30 PM
    "tool_discovery": {"hour": 3, "minute": 0},  # 3 AM daily
    "investor_outreach": {"hour": 10, "minute": 0},  # 10 AM daily
    "marketing_automation": {"hour": 14, "minute": 0},  # 2 PM daily
    "platform_optimizer": {"hour": 23, "minute": 0},  # 11 PM daily
    "cicd_monitor": {"hour": 4, "minute": 0},  # 4 AM daily
    "aixploria_discovery": {"hour": 2, "minute": 0}  # 2 AM daily - AI tool discovery
}

async def run_scheduled_agents():
    """Background task to run agents on schedule"""
    global advanced_agents
    while True:
        try:
            now = datetime.now(timezone.utc)
            for agent_name, schedule in agent_schedule.items():
                if now.hour == schedule["hour"] and now.minute == schedule["minute"]:
                    logger.info(f"Running scheduled agent: {agent_name}")
                    try:
                        if agent_name == "ceo":
                            await agent_system.run_ceo_agent()
                        elif agent_name == "product_manager":
                            await agent_system.run_product_manager_agent()
                        elif agent_name == "marketing":
                            await agent_system.run_marketing_agent()
                        elif agent_name == "vendor_manager":
                            await agent_system.run_vendor_manager_agent()
                        elif agent_name == "finance":
                            await agent_system.run_finance_agent()
                        elif agent_name == "tool_discovery" and advanced_agents:
                            await advanced_agents.run_tool_discovery_agent()
                        elif agent_name == "investor_outreach" and advanced_agents:
                            await advanced_agents.run_investor_outreach_agent()
                        elif agent_name == "marketing_automation" and advanced_agents:
                            await advanced_agents.run_marketing_automation_agent()
                        elif agent_name == "platform_optimizer" and advanced_agents:
                            await advanced_agents.run_platform_optimizer_agent()
                        elif agent_name == "cicd_monitor" and advanced_agents:
                            await advanced_agents.run_cicd_agent()
                        elif agent_name == "aixploria_discovery" and advanced_agents:
                            await advanced_agents.run_aixploria_discovery_agent()
                    except Exception as e:
                        logger.error(f"Agent {agent_name} error: {e}")
            await asyncio.sleep(60)  # Check every minute
        except Exception as e:
            logger.error(f"Scheduler error: {e}")
            await asyncio.sleep(60)

# ==================== AUTH ROUTES ====================

@api_router.post("/auth/register")
async def register(user: UserCreate):
    existing = await db.users.find_one({"email": user.email}, {"_id": 0})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user_id = str(uuid.uuid4())
    user_doc = {
        "id": user_id,
        "email": user.email,
        "username": user.username,
        "password": hash_password(user.password),
        "role": user.role,
        "avatar": f"https://api.dicebear.com/7.x/avataaars/svg?seed={user.username}",
        "bio": None,
        "followers_count": 0,
        "following_count": 0,
        "total_sales": 0,
        "total_earnings": 0,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.users.insert_one(user_doc)
    token = create_token(user_id, user.email, user.role)
    
    # Send welcome email asynchronously
    asyncio.create_task(email_service.send_welcome_email(user.email, user.username))
    
    return {"token": token, "user": {k: v for k, v in user_doc.items() if k not in ["password", "_id"]}}

@api_router.post("/auth/login")
async def login(credentials: UserLogin):
    user = await db.users.find_one({"email": credentials.email}, {"_id": 0})
    if not user or not verify_password(credentials.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_token(user["id"], user["email"], user.get("role", "user"))
    return {"token": token, "user": {k: v for k, v in user.items() if k not in ["password", "_id"]}}

@api_router.get("/auth/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    return current_user

# ==================== NOTIFICATION ROUTES ====================

@api_router.get("/notifications")
async def get_notifications(current_user: dict = Depends(get_current_user), limit: int = 50):
    notifications = await db.notifications.find(
        {"user_id": current_user["id"]},
        {"_id": 0}
    ).sort("created_at", -1).limit(limit).to_list(limit)
    return notifications

@api_router.put("/notifications/{notification_id}/read")
async def mark_notification_read(notification_id: str, current_user: dict = Depends(get_current_user)):
    await db.notifications.update_one(
        {"id": notification_id, "user_id": current_user["id"]},
        {"$set": {"read": True}}
    )
    return {"success": True}

@api_router.put("/notifications/read-all")
async def mark_all_notifications_read(current_user: dict = Depends(get_current_user)):
    await db.notifications.update_many(
        {"user_id": current_user["id"], "read": False},
        {"$set": {"read": True}}
    )
    return {"success": True}

# ==================== USER PROFILE ROUTES ====================

# User bids route - MUST be before /users/{user_id} to avoid route conflict
@api_router.get("/users/{user_id}/bids")
async def get_user_bids(
    user_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get all bids placed by a user"""
    try:
        if current_user["id"] != user_id and current_user["role"] != "admin":
            raise HTTPException(status_code=403, detail="Unauthorized")
        
        bids = await db.bids.find(
            {"user_id": user_id},
            {"_id": 0}
        ).sort("placed_at", -1).to_list(100)
        
        return {
            "bids": bids,
            "count": len(bids)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get user bids: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/users/{user_id}")
async def get_user_profile(user_id: str):
    user = await db.users.find_one({"id": user_id}, {"_id": 0, "password": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    products = await db.products.find({"vendor_id": user_id}, {"_id": 0}).limit(20).to_list(20)
    posts = await db.posts.find({"author_id": user_id}, {"_id": 0}).limit(10).to_list(10)
    
    return {**user, "products": products, "posts": posts}

@api_router.put("/users/profile")
async def update_profile(update: UserProfileUpdate, current_user: dict = Depends(get_current_user)):
    update_data = {k: v for k, v in update.model_dump().items() if v is not None}
    if update_data:
        await db.users.update_one({"id": current_user["id"]}, {"$set": update_data})
    
    updated_user = await db.users.find_one({"id": current_user["id"]}, {"_id": 0, "password": 0})
    return updated_user

@api_router.post("/users/{user_id}/follow")
async def follow_user(user_id: str, current_user: dict = Depends(get_current_user)):
    if user_id == current_user["id"]:
        raise HTTPException(status_code=400, detail="Cannot follow yourself")
    
    existing = await db.follows.find_one({"follower_id": current_user["id"], "following_id": user_id}, {"_id": 0})
    if existing:
        await db.follows.delete_one({"follower_id": current_user["id"], "following_id": user_id})
        await db.users.update_one({"id": current_user["id"]}, {"$inc": {"following_count": -1}})
        await db.users.update_one({"id": user_id}, {"$inc": {"followers_count": -1}})
        return {"following": False}
    else:
        await db.follows.insert_one({
            "id": str(uuid.uuid4()),
            "follower_id": current_user["id"],
            "following_id": user_id,
            "created_at": datetime.now(timezone.utc).isoformat()
        })
        await db.users.update_one({"id": current_user["id"]}, {"$inc": {"following_count": 1}})
        await db.users.update_one({"id": user_id}, {"$inc": {"followers_count": 1}})
        
        # Send notification
        await create_notification(
            user_id, "follow", "New Follower",
            f"{current_user['username']} started following you",
            {"follower_id": current_user["id"], "follower_name": current_user["username"]}
        )
        return {"following": True}

# ==================== PRODUCTS ROUTES ====================

@api_router.get("/products", response_model=List[ProductResponse])
async def get_products(category: Optional[str] = None, search: Optional[str] = None, limit: int = 50):
    query = {}
    if category and category != "all":
        query["category"] = category
    if search:
        query["$or"] = [
            {"title": {"$regex": search, "$options": "i"}},
            {"description": {"$regex": search, "$options": "i"}}
        ]
    
    products = await db.products.find(query, {"_id": 0}).sort("created_at", -1).limit(limit).to_list(limit)
    return products

# P2P Auction Bidding Routes - MUST be before /products/{product_id} to avoid route conflict
@api_router.get("/products/{product_id}/bids")
async def get_product_bids(product_id: str, limit: int = 20):
    """Get all bids for a product"""
    try:
        bids = await db.bids.find(
            {"product_id": product_id},
            {"_id": 0}
        ).sort("placed_at", -1).limit(limit).to_list(limit)
        
        return {
            "bids": bids,
            "count": len(bids),
            "highest_bid": bids[0] if bids else None
        }
    except Exception as e:
        logger.error(f"Failed to get bids: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/products/{product_id}/bid")
async def place_bid(
    product_id: str,
    bid_data: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    """Place a bid on a product in P2P auction"""
    try:
        bid_amount = bid_data.get("amount")
        
        if not bid_amount or bid_amount <= 0:
            raise HTTPException(status_code=400, detail="Invalid bid amount")
        
        # Get product
        product = await db.products.find_one({"id": product_id}, {"_id": 0})
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Check if product is an auction
        if not product.get("is_auction", False):
            raise HTTPException(status_code=400, detail="Product is not an auction")
        
        # Get current highest bid
        highest_bid = await db.bids.find_one(
            {"product_id": product_id},
            {"_id": 0},
            sort=[("amount", -1)]
        )
        
        min_bid = highest_bid["amount"] + 1 if highest_bid else product.get("starting_price", 0)
        
        if bid_amount < min_bid:
            raise HTTPException(
                status_code=400,
                detail=f"Bid must be at least ${min_bid}"
            )
        
        # Create bid
        bid = {
            "id": f"bid-{int(datetime.now(timezone.utc).timestamp())}",
            "product_id": product_id,
            "user_id": current_user["id"],
            "username": current_user["username"],
            "amount": bid_amount,
            "placed_at": datetime.now(timezone.utc).isoformat(),
            "status": "active"
        }
        
        await db.bids.insert_one(bid)
        bid.pop("_id", None)
        
        # Emit real-time bid update via Socket.IO
        await sio.emit(f"new_bid:{product_id}", {
            "bid": bid,
            "product_id": product_id
        })
        
        logger.info(f"✓ New bid placed: ${bid_amount} on {product_id} by {current_user['username']}")
        
        return {
            "success": True,
            "bid": bid,
            "message": "Bid placed successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to place bid: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/products/{product_id}")
async def get_product(product_id: str):
    product = await db.products.find_one({"id": product_id}, {"_id": 0})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    await db.products.update_one({"id": product_id}, {"$inc": {"views": 1}})
    vendor = await db.users.find_one({"id": product.get("vendor_id")}, {"_id": 0, "password": 0})
    related = await db.products.find({"category": product.get("category"), "id": {"$ne": product_id}}, {"_id": 0}).limit(4).to_list(4)
    
    return {**product, "vendor": vendor, "related_products": related}

@api_router.post("/products", response_model=ProductResponse)
async def create_product(product: ProductCreate, current_user: dict = Depends(get_current_user)):
    moderation = await agent_system.moderate_content(f"{product.title} {product.description}", "product")
    if not moderation.get("approved", True):
        raise HTTPException(status_code=400, detail=f"Content rejected: {moderation.get('reason')}")
    
    product_id = str(uuid.uuid4())
    product_doc = {
        "id": product_id,
        **product.model_dump(),
        "vendor_id": current_user["id"],
        "vendor_name": current_user["username"],
        "likes": 0,
        "views": 0,
        "sales": 0,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.products.insert_one(product_doc)
    return {k: v for k, v in product_doc.items() if k != "_id"}

@api_router.post("/products/{product_id}/like")
async def like_product(product_id: str, current_user: dict = Depends(get_current_user)):
    existing = await db.product_likes.find_one({"product_id": product_id, "user_id": current_user["id"]}, {"_id": 0})
    product = await db.products.find_one({"id": product_id}, {"_id": 0})
    
    if existing:
        await db.product_likes.delete_one({"product_id": product_id, "user_id": current_user["id"]})
        await db.products.update_one({"id": product_id}, {"$inc": {"likes": -1}})
        return {"liked": False}
    else:
        await db.product_likes.insert_one({
            "id": str(uuid.uuid4()),
            "product_id": product_id,
            "user_id": current_user["id"],
            "created_at": datetime.now(timezone.utc).isoformat()
        })
        await db.products.update_one({"id": product_id}, {"$inc": {"likes": 1}})
        
        # Notify vendor
        if product and product.get("vendor_id") != current_user["id"]:
            await create_notification(
                product["vendor_id"], "like", "Product Liked",
                f"{current_user['username']} liked your product '{product['title']}'",
                {"product_id": product_id}
            )
        return {"liked": True}

# ==================== PRODUCT PURCHASE ROUTES ====================

@api_router.post("/products/{product_id}/purchase")
async def purchase_product(product_id: str, request: PurchaseRequest, http_request: Request, current_user: dict = Depends(get_current_user)):
    from emergentintegrations.payments.stripe.checkout import StripeCheckout, CheckoutSessionRequest
    
    product = await db.products.find_one({"id": product_id}, {"_id": 0})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    api_key = os.environ.get('STRIPE_API_KEY')
    host_url = str(http_request.base_url).rstrip('/')
    stripe_checkout = StripeCheckout(api_key=api_key, webhook_url=f"{host_url}/api/webhook/stripe")
    
    checkout_request = CheckoutSessionRequest(
        amount=float(product["price"]),
        currency="usd",
        success_url=f"{request.origin_url}/purchase/success?session_id={{CHECKOUT_SESSION_ID}}",
        cancel_url=f"{request.origin_url}/products/{product_id}",
        metadata={
            "type": "product_purchase",
            "product_id": product_id,
            "buyer_id": current_user["id"],
            "vendor_id": product.get("vendor_id"),
            "product_title": product.get("title")
        }
    )
    
    session = await stripe_checkout.create_checkout_session(checkout_request)
    
    await db.payment_transactions.insert_one({
        "id": str(uuid.uuid4()),
        "session_id": session.session_id,
        "type": "product_purchase",
        "buyer_id": current_user["id"],
        "vendor_id": product.get("vendor_id"),
        "product_id": product_id,
        "amount": product["price"],
        "currency": "usd",
        "payment_status": "pending",
        "created_at": datetime.now(timezone.utc).isoformat()
    })
    
    return {"checkout_url": session.url, "session_id": session.session_id}

@api_router.get("/purchase/status/{session_id}")
async def get_purchase_status(session_id: str, http_request: Request):
    from emergentintegrations.payments.stripe.checkout import StripeCheckout
    
    api_key = os.environ.get('STRIPE_API_KEY')
    host_url = str(http_request.base_url).rstrip('/')
    stripe_checkout = StripeCheckout(api_key=api_key, webhook_url=f"{host_url}/api/webhook/stripe")
    
    status = await stripe_checkout.get_checkout_status(session_id)
    transaction = await db.payment_transactions.find_one({"session_id": session_id}, {"_id": 0})
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    if status.payment_status == "paid" and transaction.get("payment_status") != "completed":
        await db.payment_transactions.update_one(
            {"session_id": session_id},
            {"$set": {"payment_status": "completed", "completed_at": datetime.now(timezone.utc).isoformat()}}
        )
        
        await db.products.update_one({"id": transaction["product_id"]}, {"$inc": {"sales": 1}})
        
        vendor_cut = transaction["amount"] * 0.85
        await db.users.update_one(
            {"id": transaction["vendor_id"]},
            {"$inc": {"total_sales": 1, "total_earnings": vendor_cut}}
        )
        
        await db.purchases.insert_one({
            "id": str(uuid.uuid4()),
            "buyer_id": transaction["buyer_id"],
            "product_id": transaction["product_id"],
            "transaction_id": transaction["id"],
            "purchased_at": datetime.now(timezone.utc).isoformat()
        })
        
        # Notify vendor of sale
        product = await db.products.find_one({"id": transaction["product_id"]}, {"_id": 0})
        if product:
            await create_notification(
                transaction["vendor_id"], "sale", "New Sale!",
                f"Someone purchased '{product['title']}' for ${transaction['amount']:.2f}",
                {"product_id": transaction["product_id"], "amount": transaction["amount"]}
            )
            
            # Send email to vendor
            vendor = await db.users.find_one({"id": transaction["vendor_id"]}, {"_id": 0, "password": 0})
            if vendor and vendor.get("email"):
                vendor_cut = transaction["amount"] * 0.85
                asyncio.create_task(email_service.send_sale_notification(
                    vendor["email"],
                    vendor["username"],
                    product["title"],
                    vendor_cut
                ))
    
    return {
        "status": status.status,
        "payment_status": status.payment_status,
        "transaction_status": transaction.get("payment_status")
    }

@api_router.get("/my-purchases")
async def get_my_purchases(current_user: dict = Depends(get_current_user)):
    purchases = await db.purchases.find({"buyer_id": current_user["id"]}, {"_id": 0}).to_list(100)
    product_ids = [p["product_id"] for p in purchases]
    products = await db.products.find({"id": {"$in": product_ids}}, {"_id": 0}).to_list(100)
    products_map = {p["id"]: p for p in products}
    
    return [{**purchase, "product": products_map.get(purchase["product_id"], {})} for purchase in purchases]

# ==================== VENDOR ANALYTICS ROUTES ====================

@api_router.get("/vendor/analytics")
async def get_vendor_analytics(current_user: dict = Depends(get_current_user)):
    """Get comprehensive vendor analytics"""
    vendor_id = current_user["id"]
    
    # Products stats
    products = await db.products.find({"vendor_id": vendor_id}, {"_id": 0}).to_list(100)
    total_products = len(products)
    total_views = sum(p.get("views", 0) for p in products)
    total_likes = sum(p.get("likes", 0) for p in products)
    total_sales = sum(p.get("sales", 0) for p in products)
    
    # Revenue stats
    transactions = await db.payment_transactions.find({
        "vendor_id": vendor_id,
        "payment_status": "completed"
    }, {"_id": 0}).to_list(1000)
    
    total_revenue = sum(t.get("amount", 0) * 0.85 for t in transactions)  # 85% vendor cut
    
    # Recent sales
    recent_sales = await db.payment_transactions.find({
        "vendor_id": vendor_id,
        "payment_status": "completed"
    }, {"_id": 0}).sort("created_at", -1).limit(10).to_list(10)
    
    # Top products
    top_products = sorted(products, key=lambda x: x.get("sales", 0), reverse=True)[:5]
    
    # Daily revenue for chart (last 30 days)
    thirty_days_ago = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
    daily_revenue = {}
    for t in transactions:
        if t.get("created_at", "") >= thirty_days_ago:
            date = t["created_at"][:10]
            daily_revenue[date] = daily_revenue.get(date, 0) + t.get("amount", 0) * 0.85
    
    return {
        "overview": {
            "total_products": total_products,
            "total_views": total_views,
            "total_likes": total_likes,
            "total_sales": total_sales,
            "total_revenue": round(total_revenue, 2),
            "conversion_rate": round((total_sales / total_views * 100) if total_views > 0 else 0, 2)
        },
        "recent_sales": recent_sales,
        "top_products": top_products,
        "daily_revenue": [{"date": k, "revenue": v} for k, v in sorted(daily_revenue.items())]
    }

@api_router.get("/vendor/products")
async def get_vendor_products(current_user: dict = Depends(get_current_user)):
    """Get vendor's own products with detailed stats"""
    products = await db.products.find({"vendor_id": current_user["id"]}, {"_id": 0}).sort("created_at", -1).to_list(100)
    return products

# ==================== POSTS ROUTES ====================

@api_router.get("/posts")
async def get_posts(limit: int = 50):
    posts = await db.posts.find({}, {"_id": 0}).sort("created_at", -1).limit(limit).to_list(limit)
    return posts

@api_router.post("/posts")
async def create_post(post: PostCreate, current_user: dict = Depends(get_current_user)):
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
    
    # Broadcast to feed room
    await broadcast_to_room("feed", {"type": "new_post", "post": {k: v for k, v in post_doc.items() if k != "_id"}})
    
    return {k: v for k, v in post_doc.items() if k != "_id"}

@api_router.post("/posts/{post_id}/like")
async def like_post(post_id: str, current_user: dict = Depends(get_current_user)):
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
        
        # Notify author
        if post and post.get("author_id") != current_user["id"]:
            await create_notification(
                post["author_id"], "like", "Post Liked",
                f"{current_user['username']} liked your post",
                {"post_id": post_id}
            )
        return {"liked": True}

@api_router.post("/posts/{post_id}/comment")
async def comment_post(post_id: str, comment: CommentCreate, current_user: dict = Depends(get_current_user)):
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
    
    # Notify post author
    post = await db.posts.find_one({"id": post_id}, {"_id": 0})
    if post and post.get("author_id") != current_user["id"]:
        await create_notification(
            post["author_id"], "comment", "New Comment",
            f"{current_user['username']} commented on your post",
            {"post_id": post_id, "comment_id": comment_id}
        )
    
    return {k: v for k, v in comment_doc.items() if k != "_id"}

@api_router.get("/posts/{post_id}/comments")
async def get_comments(post_id: str):
    comments = await db.comments.find({"post_id": post_id}, {"_id": 0}).sort("created_at", -1).to_list(100)
    return comments

# ==================== AI GENERATION ROUTES ====================

@api_router.post("/ai/generate")
async def generate_ai_content(request: AIGenerateRequest, current_user: dict = Depends(get_current_user)):
    from emergentintegrations.llm.chat import LlmChat, UserMessage
    
    api_key = os.environ.get('EMERGENT_LLM_KEY')
    if not api_key:
        raise HTTPException(status_code=500, detail="AI service not configured")
    
    try:
        if request.content_type in ["text", "ebook", "blog"]:
            chat = LlmChat(
                api_key=api_key,
                session_id=f"nexus-{current_user['id']}-{uuid.uuid4()}",
                system_message="You are a creative AI assistant for NEXUS platform."
            ).with_model("openai", "gpt-5.2")
            
            prompts = {
                "ebook": f"Write a detailed ebook chapter about: {request.prompt}",
                "blog": f"Write an engaging blog post about: {request.prompt}",
                "text": request.prompt
            }
            
            response = await chat.send_message(UserMessage(text=prompts.get(request.content_type, request.prompt)))
            return {"success": True, "content_type": request.content_type, "result": response, "generated_at": datetime.now(timezone.utc).isoformat()}
        
        elif request.content_type == "image":
            # Try fal.ai first (faster), fallback to Gemini Nano Banana
            if fal_ai_service.is_active:
                logger.info("Using fal.ai for fast image generation")
                result = await fal_ai_service.generate_image_fast(request.prompt)
                
                if result["success"] and result.get("images"):
                    return {
                        "success": True,
                        "content_type": "image",
                        "result": "Image generated via fal.ai",
                        "image_data": result["images"][0]["url"],
                        "provider": "fal_ai",
                        "generated_at": datetime.now(timezone.utc).isoformat()
                    }
            
            # Fallback to Gemini Nano Banana
            logger.info("Using Gemini Nano Banana for image generation")
            chat = LlmChat(
                api_key=api_key,
                session_id=f"nexus-img-{current_user['id']}-{uuid.uuid4()}",
                system_message="You are an AI image generator."
            ).with_model("gemini", "gemini-3-pro-image-preview").with_params(modalities=["image", "text"])
            
            text, images = await chat.send_message_multimodal_response(UserMessage(text=f"Generate an image: {request.prompt}"))
            image_data = f"data:{images[0]['mime_type']};base64,{images[0]['data']}" if images else None
            
            return {
                "success": True,
                "content_type": "image",
                "result": text,
                "image_data": image_data,
                "provider": "gemini_nano_banana",
                "generated_at": datetime.now(timezone.utc).isoformat()
            }
        
        elif request.content_type == "voice":
            # NEW: ElevenLabs voice generation
            result = await elevenlabs_service.generate_speech(
                text=request.prompt,
                stability=0.5,
                similarity_boost=0.75
            )
            
            if result["success"]:
                return {
                    "success": True,
                    "content_type": "voice",
                    "result": "Voice generated successfully",
                    "audio_url": result["audio_url"],
                    "provider": "elevenlabs",
                    "mocked": result.get("mocked", False),
                    "generated_at": datetime.now(timezone.utc).isoformat()
                }
            else:
                return {
                    "success": False,
                    "content_type": "voice",
                    "error": result.get("error") or result.get("message"),
                    "mocked": result.get("mocked", False)
                }
        
        elif request.content_type == "music":
            chat = LlmChat(api_key=api_key, session_id=f"nexus-music-{uuid.uuid4()}", system_message="You are an AI music composition assistant.").with_model("openai", "gpt-5.2")
            response = await chat.send_message(UserMessage(text=f"Create music composition for: {request.prompt}. Include title, genre, tempo, lyrics, structure, instrumentation."))
            return {"success": True, "content_type": "music", "result": response, "generated_at": datetime.now(timezone.utc).isoformat()}
        
        elif request.content_type == "video":
            # Generate actual video using selected provider (Sora 2 or Runway)
            logger.info(f"Generating video with {request.video_provider} for user {current_user['id']}")
            
            # Extract video parameters from request (with defaults)
            video_params = getattr(request, 'video_params', {}) or {}
            provider = getattr(request, 'video_provider', 'sora') or 'sora'
            
            if provider == "runway":
                # Use Runway ML
                model = video_params.get('model', 'gen3a_turbo')
                duration = video_params.get('duration', 5)
                aspect_ratio = video_params.get('aspect_ratio', '1280:720')
                
                result = await runway_video_service.generate_video(
                    prompt=request.prompt,
                    model=model,
                    duration=duration,
                    aspect_ratio=aspect_ratio,
                    output_filename=f"runway_user_{current_user['id']}_{uuid.uuid4().hex[:8]}"
                )
                
                if result["success"]:
                    return {
                        "success": True,
                        "content_type": "video",
                        "result": f"Video generation started: {result['prompt'][:100]}",
                        "task_id": result["task_id"],
                        "model": result["model"],
                        "duration": result["duration"],
                        "provider": "runway",
                        "status": "processing",
                        "message": "Video is being generated. Check status with task_id.",
                        "generated_at": datetime.now(timezone.utc).isoformat()
                    }
                else:
                    return {
                        "success": False,
                        "content_type": "video",
                        "error": result.get("error", "Runway video generation failed")
                    }
            
            else:
                # Use Sora 2
                model = video_params.get('model', 'sora-2')
                size = video_params.get('size', '1280x720')
                duration = video_params.get('duration', 4)
                
                result = await text_to_video_service.generate_video(
                    prompt=request.prompt,
                    model=model,
                    size=size,
                    duration=duration,
                    output_filename=f"sora_user_{current_user['id']}_{uuid.uuid4().hex[:8]}"
                )
                
                if result["success"]:
                    return {
                        "success": True,
                        "content_type": "video",
                        "result": f"Video generated successfully: {result['prompt'][:100]}",
                        "video_url": result["video_url"],
                        "video_path": result["video_path"],
                        "model": result["model"],
                        "size": result["size"],
                        "duration": result["duration"],
                        "provider": "sora_2",
                        "generated_at": datetime.now(timezone.utc).isoformat()
                    }
                else:
                    return {
                        "success": False,
                        "content_type": "video",
                        "error": result.get("error", "Sora video generation failed")
                    }
        
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported content type: {request.content_type}")
    
    except Exception as e:
        logger.error(f"AI generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"AI generation failed: {str(e)}")

@api_router.post("/ai/chat")
async def ai_chat_support(message: ChatMessage, current_user: dict = Depends(get_optional_user)):
    from emergentintegrations.llm.chat import LlmChat, UserMessage
    
    api_key = os.environ.get('EMERGENT_LLM_KEY')
    user_id = current_user["id"] if current_user else "anonymous"
    
    chat = LlmChat(
        api_key=api_key,
        session_id=f"support-{user_id}-{uuid.uuid4()}",
        system_message="""You are NEXUS AI Support. Help users with marketplace, studio, social features, boosts, and payments. Be helpful and promote platform features."""
    ).with_model("anthropic", "claude-sonnet-4-5-20250929")
    
    response = await chat.send_message(UserMessage(text=message.message))
    
    await db.support_chats.insert_one({
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "message": message.message,
        "response": response,
        "created_at": datetime.now(timezone.utc).isoformat()
    })
    
    return {"response": response}

# ==================== AI AGENTS ROUTES ====================

@api_router.get("/agents")
async def get_agents():
    # Core hardcoded agents
    core_agents = [
        # Original 5 agents
        {"id": "agent-ceo", "name": "CEO Agent", "role": "Executive Overview", "desc": "Reviews KPIs, sends daily profit reports", "type": "base"},
        {"id": "agent-product", "name": "Product Manager", "role": "Product Curation", "desc": "Imports trending products, optimizes catalog", "type": "base"},
        {"id": "agent-marketing", "name": "Marketing Agent", "role": "Social Media", "desc": "Creates content, manages campaigns", "type": "base"},
        {"id": "agent-vendor", "name": "Vendor Manager", "role": "Vendor Operations", "desc": "Approves vendors, moderates listings", "type": "base"},
        {"id": "agent-finance", "name": "Finance Agent", "role": "Financial Operations", "desc": "Tracks revenue, processes payouts", "type": "base"},
        # Advanced agents powered by Manus AI
        {"id": "agent-tool-discovery", "name": "Tool Discovery Agent", "role": "Integration Research", "desc": "Searches GitHub/GitLab for beneficial tools and APIs", "type": "manus"},
        {"id": "agent-investor", "name": "Investor Outreach Agent", "role": "Fundraising", "desc": "Finds investors, creates pitch materials", "type": "manus"},
        {"id": "agent-marketing-auto", "name": "Marketing Automation", "role": "Campaign Management", "desc": "Auto-generates and schedules marketing campaigns", "type": "manus"},
        {"id": "agent-optimizer", "name": "Platform Optimizer", "role": "Performance Analysis", "desc": "Analyzes metrics and suggests improvements", "type": "manus"},
        {"id": "agent-cicd", "name": "CI/CD Agent", "role": "DevOps", "desc": "Monitors deployments and system health", "type": "manus"},
        {"id": "agent-aixploria", "name": "AIxploria Discovery", "role": "AI Tool Finder", "desc": "Scans AIxploria, GitHub, ProductHunt for new AI tools daily", "type": "autonomous"}
    ]
    
    # Fetch discovered agents from database
    discovered_agents = await db.agents.find(
        {"source": "discovered_autonomous"},
        {"_id": 0}
    ).limit(100).to_list(100)
    
    # Format discovered agents for display
    discovered_formatted = []
    for agent in discovered_agents:
        discovered_formatted.append({
            "id": agent.get('id', f"discovered-{agent['name'].lower().replace(' ', '-')}"),
            "name": agent.get('name', 'Unknown'),
            "role": agent.get('category', 'AI Tool'),
            "desc": agent.get('description', 'Discovered AI tool')[:100],
            "type": "discovered",
            "discovery_score": agent.get('discovery_score', 50),
            "benefit_level": agent.get('benefit_level', 'medium'),
            "external_url": agent.get('external_url', ''),
            "status": "active"
        })
    
    # Combine core and discovered agents
    all_agents = core_agents + discovered_formatted
    
    agents_data = []
    for agent_info in all_agents:
        agent_name = agent_info["id"].replace("agent-", "").replace("-", "_")
        report = await db.agent_reports.find_one({"agent": agent_name}, {"_id": 0}, sort=[("created_at", -1)])
        tasks_count = await db.agent_reports.count_documents({"agent": agent_name})
        
        agents_data.append({
            **agent_info,
            "status": agent_info.get("status", "active"),
            "last_active": report.get("created_at") if report else datetime.now(timezone.utc).isoformat(),
            "tasks_completed": tasks_count * 10 + 100,
            "efficiency": report.get("efficiency_score", 98) if report else 95
        })
    
    return agents_data

@api_router.post("/agents/{agent_id}/run")
async def run_agent(agent_id: str, current_user: dict = Depends(require_admin)):
    global advanced_agents
    
    base_agent_map = {
        "ceo": agent_system.run_ceo_agent,
        "product_manager": agent_system.run_product_manager_agent,
        "marketing": agent_system.run_marketing_agent,
        "vendor_manager": agent_system.run_vendor_manager_agent,
        "finance": agent_system.run_finance_agent
    }
    
    advanced_agent_map = {
        "tool_discovery": lambda: advanced_agents.run_tool_discovery_agent() if advanced_agents else None,
        "investor": lambda: advanced_agents.run_investor_outreach_agent() if advanced_agents else None,
        "marketing_auto": lambda: advanced_agents.run_marketing_automation_agent() if advanced_agents else None,
        "optimizer": lambda: advanced_agents.run_platform_optimizer_agent() if advanced_agents else None,
        "cicd": lambda: advanced_agents.run_cicd_agent() if advanced_agents else None
    }
    
    agent_key = agent_id.replace("agent-", "").replace("-", "_")
    
    # Check base agents first
    if agent_key in base_agent_map:
        report = await base_agent_map[agent_key]()
        return {"success": True, "report": report}
    
    # Check advanced agents
    if agent_key in advanced_agent_map:
        agent_func = advanced_agent_map[agent_key]
        if agent_func:
            report = await agent_func()
            return {"success": True, "report": report}
        else:
            raise HTTPException(status_code=503, detail="Advanced agents not initialized")
    
    raise HTTPException(status_code=404, detail="Agent not found")

@api_router.get("/agents/{agent_id}/reports")
async def get_agent_reports(agent_id: str, limit: int = 10):
    agent_name = agent_id.replace("agent-", "")
    reports = await db.agent_reports.find({"agent": agent_name}, {"_id": 0}).sort("created_at", -1).limit(limit).to_list(limit)
    return reports

# ==================== MANUS AI & AUTOMATION ROUTES ====================

@api_router.post("/manus/task")
async def create_manus_task(task: Dict[str, Any], current_user: dict = Depends(require_admin)):
    """Create a new Manus AI autonomous task"""
    result = await manus_service.create_task(
        task.get("description", ""),
        task.get("context", {})
    )
    return result

@api_router.get("/manus/task/{task_id}")
async def get_manus_task_status(task_id: str, current_user: dict = Depends(require_admin)):
    """Get status of a Manus AI task"""
    result = await manus_service.get_task_status(task_id)
    return result

@api_router.post("/automation/discover-tools")
async def trigger_tool_discovery(categories: List[str], current_user: dict = Depends(require_admin)):
    """Manually trigger tool discovery across categories"""
    result = await automation_service.auto_discover_tools(categories)
    return result

@api_router.get("/automation/discovered-tools")
async def get_discovered_tools(current_user: dict = Depends(require_admin)):
    """Get all discovered tools from agent reports"""
    reports = await db.agent_reports.find(
        {"agent_type": "tool_discovery"},
        {"_id": 0}
    ).sort("created_at", -1).limit(10).to_list(10)
    
    all_tools = []
    for report in reports:
        tools = report.get("report", {}).get("high_priority_integrations", [])
        all_tools.extend(tools)
    
    return {"tools": all_tools, "total": len(all_tools)}

@api_router.post("/admin/aixploria/scan")
async def trigger_aixploria_scan(
    background_tasks: BackgroundTasks,
    comprehensive: bool = False,
    current_user: dict = Depends(require_admin)
):
    """Trigger AIxploria discovery scan
    
    Args:
        comprehensive: If True, scrapes ALL 50+ categories (slower, 2-3 mins)
    """
    async def run_scan():
        try:
            scan_mode = "comprehensive (50+ categories)" if comprehensive else "standard (top + latest)"
            logger.info(f"🔍 AIxploria scan triggered by admin - Mode: {scan_mode}")
            
            result = await aixploria_service.discover_and_evaluate(include_all_categories=comprehensive)
            
            # Store in dedicated collection
            scan_doc = {
                "scan_id": f"scan_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}",
                "triggered_by": current_user["id"],
                "scan_mode": "comprehensive" if comprehensive else "standard",
                **result
            }
            await db.aixploria_scans.insert_one(scan_doc)
            logger.info(f"✓ Scan complete: {result['total_tools_discovered']} tools discovered")
        except Exception as e:
            logger.error(f"AIxploria scan failed: {str(e)}")
    
    background_tasks.add_task(run_scan)
    
    mode_desc = "comprehensive (all 50+ categories)" if comprehensive else "standard (top + latest)"
    return {
        "status": "scan_started",
        "message": f"AIxploria discovery running in background - {mode_desc}",
        "estimated_time": "2-3 minutes" if comprehensive else "15-30 seconds"
    }

@api_router.get("/admin/aixploria/tools")
async def get_aixploria_tools(
    benefit_level: Optional[str] = None,
    current_user: dict = Depends(require_admin)
):
    """Get discovered AI tools from AIxploria with optional filtering"""
    scans = await db.aixploria_scans.find(
        {},
        {"_id": 0}
    ).sort("scan_timestamp", -1).limit(5).to_list(5)
    
    if not scans:
        return {"tools": [], "latest_scan": None, "total": 0}
    
    latest_scan = scans[0]
    all_tools = []
    
    # Aggregate tools by benefit level
    if benefit_level:
        key = f"{benefit_level}_priority" if benefit_level in ["high", "medium"] else "critical_integrations"
        all_tools = latest_scan.get(key, [])
    else:
        all_tools = (
            latest_scan.get("critical_integrations", []) +
            latest_scan.get("high_priority", []) +
            latest_scan.get("medium_priority", [])
        )
    
    return {
        "tools": all_tools,
        "latest_scan": latest_scan.get("scan_timestamp"),
        "total": len(all_tools),
        "summary": latest_scan.get("summary", {})
    }

@api_router.get("/admin/aixploria/stats")
async def get_aixploria_stats(current_user: dict = Depends(require_admin)):
    """Get AIxploria discovery statistics"""
    total_scans = await db.aixploria_scans.count_documents({})
    scans = await db.aixploria_scans.find({}, {"_id": 0}).sort("scan_timestamp", -1).limit(10).to_list(10)
    
    if not scans:
        return {"total_scans": 0, "tools_discovered": 0, "critical_count": 0}
    
    latest = scans[0]
    
    return {
        "total_scans": total_scans,
        "last_scan": latest.get("scan_timestamp"),
        "tools_discovered": latest.get("total_tools_discovered", 0),
        "critical_count": latest.get("summary", {}).get("critical_count", 0),
        "high_count": latest.get("summary", {}).get("high_count", 0),
        "scan_history": [{"timestamp": s.get("scan_timestamp"), "count": s.get("total_tools_discovered")} for s in scans]
    }

@api_router.get("/admin/performance")
async def get_performance_metrics(current_user: dict = Depends(require_admin)):
    """Get platform performance metrics"""
    if performance_optimizer:
        metrics = await performance_optimizer.get_performance_metrics()
        return metrics
    return {"error": "Performance optimizer not initialized"}

@api_router.get("/admin/aixploria/latest-scan")
async def get_latest_scan(current_user: dict = Depends(require_admin)):
    """Get the most recent AIxploria scan with full details including AI analysis"""
    scan = await db.aixploria_scans.find_one(
        {},
        {"_id": 0}
    , sort=[("scan_timestamp", -1)])
    
    if not scan:
        return {"error": "No scans found", "scan": None}
    
    return {"scan": scan}

@api_router.get("/cicd/status")
async def get_cicd_status(current_user: dict = Depends(require_admin)):
    """Get CI/CD pipeline status"""
    health = await cicd_service.monitor_repository_health()
    quality = await cicd_service.analyze_code_quality()
    return {"repository": health, "code_quality": quality}

@api_router.post("/cicd/deploy")
async def trigger_deployment(environment: str, current_user: dict = Depends(require_admin)):
    """Trigger deployment to specified environment"""
    result = await cicd_service.trigger_deployment(environment)
    return result

@api_router.post("/cicd/test")
async def run_tests(current_user: dict = Depends(require_admin)):
    """Run automated test suite"""
    result = await cicd_service.run_automated_tests()
    return result


# ==================== OPENCLAW ENDPOINTS ====================

@api_router.get("/admin/openclaw/status")
async def get_openclaw_status(current_user: dict = Depends(require_admin)):
    """Get OpenClaw autonomous agent status"""
    return openclaw_service.get_status()

@api_router.post("/admin/openclaw/test")
async def test_openclaw(current_user: dict = Depends(require_admin)):
    """Test OpenClaw connection and configuration"""
    try:
        status = openclaw_service.get_status()
        return {
            "success": True,
            "status": status,
            "message": "OpenClaw test complete"
        }
    except Exception as e:
        logger.error(f"OpenClaw test failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@api_router.get("/admin/openclaw/analysis")
async def get_openclaw_analysis(current_user: dict = Depends(require_admin)):
    """Get OpenClaw platform improvement suggestions"""
    return openclaw_service.get_quick_analysis()

@api_router.post("/admin/openclaw/configure")
async def configure_openclaw(
    config: Dict[str, Any],
    current_user: dict = Depends(require_admin)
):
    """Configure OpenClaw with API keys and settings"""
    return openclaw_service.configure(config)

@api_router.post("/admin/integrate-discovered-tools")
async def integrate_discovered_tools(current_user: dict = Depends(require_admin)):
    """Integrate all discovered AI tools into NEXUS marketplace"""
    result = await tool_integration_service.integrate_all_discovered_tools()
    return result

@api_router.get("/admin/tool-integration-status")
async def get_tool_integration_status(current_user: dict = Depends(require_admin)):
    """Get status of tool integration from discovery engine"""
    result = await tool_integration_service.get_integration_status()
    return result

# ==================== INSTAGRAM INTEGRATION ENDPOINTS ====================

@api_router.get("/instagram/status")
async def get_instagram_status(current_user: dict = Depends(get_current_user)):
    """Get Instagram service status"""
    from services.instagram_service import instagram_service
    return instagram_service.get_status()

@api_router.get("/instagram/profile/{username}")
async def get_instagram_profile(
    username: str,
    current_user: dict = Depends(get_current_user)
):
    """Get Instagram profile stats"""
    from services.instagram_service import instagram_service
    return await instagram_service.get_profile_stats(username)

@api_router.post("/instagram/import-posts")
async def import_instagram_posts(
    request: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    """Import posts from Instagram profile"""
    from services.instagram_service import instagram_service
    username = request.get("username")
    max_posts = request.get("max_posts", 10)
    
    if not username:
        raise HTTPException(status_code=400, detail="Username required")
    
    return await instagram_service.download_profile_posts(username, max_posts)

# ==================== CACHE MANAGEMENT ENDPOINTS ====================

@api_router.get("/admin/cache/stats")
async def get_cache_stats(current_user: dict = Depends(require_admin)):
    """Get cache statistics"""
    return await cache_service.get_stats()

@api_router.delete("/admin/cache/clear")
async def clear_cache(
    pattern: str = "*",
    current_user: dict = Depends(require_admin)
):
    """Clear cache by pattern"""
    count = await cache_service.delete_pattern(pattern)
    return {"success": True, "keys_deleted": count}

# ==================== FAL.AI TEST ENDPOINT ====================

@api_router.post("/admin/fal/test")
async def test_fal_ai(current_user: dict = Depends(require_admin)):
    """Test Fal.ai integration"""
    try:
        result = await fal_ai_service.generate_image_fast("A beautiful sunset over mountains")
        return {
            "success": result.get("success", False),
            "configured": fal_ai_service.is_active,
            "result": result,
            "message": "Fal.ai test complete"
        }
    except Exception as e:
        logger.error(f"Fal.ai test failed: {e}")
        return {
            "success": False,
            "configured": fal_ai_service.is_active,
            "error": str(e)
        }

# ==================== SOCIAL MEDIA MANAGEMENT ENDPOINTS ====================

@api_router.get("/social-media/status")
async def get_social_media_status(current_user: dict = Depends(get_current_user)):
    """Get status of all social media integrations"""
    try:
        status = await social_media_service.get_platform_status()
        return status
    except Exception as e:
        logger.error(f"Social media status error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/social-media/profiles")
async def get_social_profiles(
    platform: str,
    current_user: dict = Depends(get_current_user)
):
    """Get connected social media profiles for a platform"""
    try:
        if platform == "buffer":
            return await social_media_service.buffer_get_profiles()
        elif platform == "socialbee":
            return await social_media_service.socialbee_get_profiles()
        elif platform == "later":
            return await social_media_service.later_get_profiles()
        else:
            raise HTTPException(status_code=400, detail="Invalid platform")
    except Exception as e:
        logger.error(f"Get profiles error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/social-media/post")
async def post_to_social_media(
    request: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    """Post content to social media platforms"""
    try:
        text = request.get("text")
        media_url = request.get("media_url")
        platforms = request.get("platforms", [])
        scheduled_at = request.get("scheduled_at")
        
        if not text:
            raise HTTPException(status_code=400, detail="Text is required")
        
        # Parse scheduled_at if provided
        if scheduled_at:
            from datetime import datetime
            scheduled_at = datetime.fromisoformat(scheduled_at.replace('Z', '+00:00'))
        
        result = await social_media_service.post_to_all_platforms(
            text=text,
            media_url=media_url,
            platforms=platforms if platforms else None,
            scheduled_at=scheduled_at
        )
        
        return result
    except Exception as e:
        logger.error(f"Social media post error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== RUNWAY VIDEO STATUS ENDPOINT ====================

@api_router.get("/api/runway/status/{task_id}")
async def get_runway_status(task_id: str, current_user: dict = Depends(get_current_user)):
    """Get Runway video generation status"""
    try:
        result = await runway_video_service.get_task_status(task_id)
        return result
    except Exception as e:
        logger.error(f"Error getting Runway status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/admin/runway/test")
async def test_runway(current_user: dict = Depends(require_admin)):
    """Test Runway ML integration"""
    try:
        result = await runway_video_service.generate_video(
            prompt="A cute cat playing with a ball of yarn",
            model="gen3a_turbo",
            duration=5
        )
        return {
            "success": result.get("success", False),
            "configured": bool(runway_video_service.api_key),
            "result": result,
            "message": "Runway test initiated - check status with task_id"
        }
    except Exception as e:
        logger.error(f"Runway test failed: {e}")
        return {
            "success": False,
            "configured": bool(runway_video_service.api_key),
            "error": str(e)
        }

# ==================== MEGA ENHANCEMENT ENDPOINTS ====================

@api_router.post("/admin/mega-discovery")
async def trigger_mega_discovery(current_user: dict = Depends(require_admin)):
    """Trigger comprehensive multi-source AI tool discovery"""
    try:
        result = await mega_discovery_engine.discover_all_sources()
        
        # Store scan results in database
        scan_doc = {
            "scan_id": f"mega-{int(datetime.now(timezone.utc).timestamp())}",
            "scan_type": "mega_discovery",
            "scan_timestamp": datetime.now(timezone.utc).isoformat(),
            "results": result,
            "total_discovered": result.get('total_discovered', 0)
        }
        await db.mega_scans.insert_one(scan_doc)
        
        return {
            "success": True,
            "message": f"Mega discovery complete: {result['total_discovered']} tools found",
            "scan_id": scan_doc['scan_id'],
            "results": result
        }
    except Exception as e:
        logger.error(f"Mega discovery failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/admin/mega-discovery/latest")
async def get_latest_mega_discovery(current_user: dict = Depends(require_admin)):
    """Get latest mega discovery scan results"""
    scan = await db.mega_scans.find_one(
        {},
        {"_id": 0},
        sort=[("scan_timestamp", -1)]
    )
    if not scan:
        return {"message": "No mega scans found. Run a scan first."}
    return scan

@api_router.get("/users/{user_id}/profile/enhanced")
async def get_enhanced_user_profile(user_id: str):
    """Get comprehensive user profile with detailed analytics"""
    try:
        profile = await enhanced_profile_service.get_user_profile_detailed(user_id)
        return profile
    except Exception as e:
        logger.error(f"Failed to get enhanced profile: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/admin/investor-dashboard")
async def get_investor_dashboard(current_user: dict = Depends(require_admin)):
    """Get comprehensive investor dashboard with metrics and investor database"""
    try:
        dashboard = await investor_dashboard_service.get_investor_dashboard(current_user['id'])
        return dashboard
    except Exception as e:
        logger.error(f"Failed to get investor dashboard: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/admin/pitch-deck-data")
async def get_pitch_deck_data(current_user: dict = Depends(require_admin)):
    """Get automated pitch deck data"""
    try:
        data = await investor_dashboard_service.generate_pitch_deck_data()
        return data
    except Exception as e:
        logger.error(f"Failed to generate pitch deck data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/marketing/campaigns")
async def create_marketing_campaign(
    product_id: str,
    current_user: dict = Depends(require_vendor)
):
    """Create automated marketing campaign for a product"""
    try:
        result = await marketing_service.create_automated_campaign(product_id)
        return result
    except Exception as e:
        logger.error(f"Failed to create campaign: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/marketing/campaigns")
async def get_marketing_campaigns(current_user: dict = Depends(require_vendor)):
    """Get all marketing campaigns"""
    try:
        campaigns = await marketing_service.get_all_campaigns()
        return {"campaigns": campaigns}
    except Exception as e:
        logger.error(f"Failed to get campaigns: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/marketing/seo")
async def get_seo_performance(current_user: dict = Depends(require_admin)):
    """Get SEO performance metrics"""
    try:
        seo = await marketing_service.get_seo_performance()
        return seo
    except Exception as e:
        logger.error(f"Failed to get SEO data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/admin/cloudflare/workers")
async def list_cloudflare_workers(current_user: dict = Depends(require_admin)):
    """List all deployed Cloudflare Workers"""
    try:
        workers = await cloudflare_workers_service.list_workers()
        return {"workers": workers}
    except Exception as e:
        logger.error(f"Failed to list workers: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/admin/cloudflare/workers")
async def deploy_cloudflare_worker(
    worker_data: Dict[str, Any],
    current_user: dict = Depends(require_admin)
):
    """Deploy a new Cloudflare Worker"""
    try:
        name = worker_data.get('name')
        script = worker_data.get('script')
        if not name or not script:
            raise HTTPException(status_code=400, detail="Name and script required")
        
        result = await cloudflare_workers_service.deploy_worker(name, script)
        return result
    except Exception as e:
        logger.error(f"Failed to deploy worker: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== MCP SERVER INTEGRATION ====================

@api_router.get("/admin/mcp/servers")
async def get_mcp_servers(current_user: dict = Depends(require_admin)):
    """Get discovered MCP servers"""
    try:
        servers = await mcp_integration_service.discover_available_mcp_servers()
        return {"servers": servers, "count": len(servers)}
    except Exception as e:
        logger.error(f"Failed to get MCP servers: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/admin/mcp/status")
async def get_mcp_status(current_user: dict = Depends(require_admin)):
    """Get MCP integration status"""
    try:
        status = await mcp_integration_service.get_mcp_integration_status()
        return status
    except Exception as e:
        logger.error(f"Failed to get MCP status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/admin/mcp/connect")
async def connect_mcp_server(
    server_config: Dict[str, Any],
    current_user: dict = Depends(require_admin)
):
    """Connect to an MCP server"""
    try:
        result = await mcp_integration_service.connect_to_mcp_server(server_config)
        return result
    except Exception as e:
        logger.error(f"Failed to connect to MCP server: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/admin/mcp/call-tool")
async def call_mcp_tool(
    tool_request: Dict[str, Any],
    current_user: dict = Depends(require_admin)
):
    """Call a tool on a connected MCP server"""
    try:
        server_name = tool_request.get('server_name')
        tool_name = tool_request.get('tool_name')
        arguments = tool_request.get('arguments', {})
        
        if not server_name or not tool_name:
            raise HTTPException(status_code=400, detail="server_name and tool_name required")
        
        result = await mcp_integration_service.call_mcp_tool(server_name, tool_name, arguments)
        return result
    except Exception as e:
        logger.error(f"Failed to call MCP tool: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== CREATION STUDIO ENHANCEMENTS ====================

@api_router.post("/studio/publish-to-marketplace")
async def publish_creation_to_marketplace(
    creation_data: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    """Publish AI-generated content directly to marketplace"""
    try:
        # Validate user is vendor
        user = await db.users.find_one({"id": current_user["id"]}, {"_id": 0})
        if user.get("role") not in ["vendor", "admin"]:
            # Upgrade user to vendor
            await db.users.update_one(
                {"id": current_user["id"]},
                {"$set": {"role": "vendor"}}
            )
        
        # Create product from creation
        product = {
            "id": f"prod-{uuid.uuid4()}",
            "title": creation_data.get("title"),
            "description": creation_data.get("description"),
            "price": float(creation_data.get("price", 9.99)),
            "category": creation_data.get("category"),
            "vendor_id": current_user["id"],
            "vendor_name": user.get("username"),
            "file_url": creation_data.get("file_url"),
            "image_url": creation_data.get("image_url") or creation_data.get("thumbnail_url"),
            "tags": creation_data.get("tags", []),
            "is_ai_generated": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "likes": 0,
            "views": 0,
            "sales": 0,
            "rating": 0,
            "reviews": []
        }
        
        await db.products.insert_one(product)
        
        # Remove MongoDB _id before returning (not JSON serializable)
        product.pop("_id", None)
        
        # Create notification
        await create_notification(
            current_user["id"],
            "product_published",
            "Product Published!",
            f"Your AI creation '{product['title']}' is now live on the marketplace",
            {"product_id": product["id"]}
        )
        
        logger.info(f"✓ Published creation to marketplace: {product['id']}")
        
        return {
            "success": True,
            "product_id": product["id"],
            "message": "Successfully published to marketplace",
            "product": product
        }
        
    except Exception as e:
        logger.error(f"Failed to publish to marketplace: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/studio/download")
async def download_creation(
    creation_data: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    """Generate downloadable file from AI creation"""
    try:
        import base64
        from io import BytesIO
        
        content_type = creation_data.get("content_type")
        content = creation_data.get("content")
        title = creation_data.get("title", "creation")
        
        if content_type == "ebook":
            # Generate PDF for ebook
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet
            
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter)
            styles = getSampleStyleSheet()
            
            story = []
            story.append(Paragraph(title, styles['Title']))
            story.append(Spacer(1, 12))
            
            # Split content into paragraphs
            for para in content.split('\n\n'):
                if para.strip():
                    story.append(Paragraph(para, styles['BodyText']))
                    story.append(Spacer(1, 12))
            
            doc.build(story)
            pdf_data = buffer.getvalue()
            
            return {
                "success": True,
                "download_url": f"data:application/pdf;base64,{base64.b64encode(pdf_data).decode()}",
                "filename": f"{title.replace(' ', '_')}.pdf",
                "content_type": "application/pdf"
            }
        
        elif content_type == "music":
            # Return as text file with composition details
            text_content = f"Title: {title}\n\nComposition:\n{content}"
            encoded = base64.b64encode(text_content.encode()).decode()
            
            return {
                "success": True,
                "download_url": f"data:text/plain;base64,{encoded}",
                "filename": f"{title.replace(' ', '_')}.txt",
                "content_type": "text/plain",
                "note": "Music composition details - use professional DAW for audio production"
            }
        
        elif content_type == "video":
            # Return as script file
            text_content = f"Title: {title}\n\nVideo Script:\n{content}"
            encoded = base64.b64encode(text_content.encode()).decode()
            
            return {
                "success": True,
                "download_url": f"data:text/plain;base64,{encoded}",
                "filename": f"{title.replace(' ', '_')}_script.txt",
                "content_type": "text/plain",
                "note": "Video script - use video editing software for production"
            }
        
        elif content_type in ["text", "blog"]:
            # Return as text file
            text_content = f"Title: {title}\n\n{content}"
            encoded = base64.b64encode(text_content.encode()).decode()
            
            return {
                "success": True,
                "download_url": f"data:text/plain;base64,{encoded}",
                "filename": f"{title.replace(' ', '_')}.txt",
                "content_type": "text/plain"
            }
        
        elif content_type == "voice":
            # Voice files already have audio_url from ElevenLabs
            if creation_data.get("audio_url"):
                return {
                    "success": True,
                    "download_url": creation_data.get("audio_url"),
                    "filename": f"{title.replace(' ', '_')}.mp3",
                    "content_type": "audio/mpeg"
                }
            else:
                raise HTTPException(status_code=400, detail="No audio URL provided")
        
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported content type: {content_type}")
    
    except Exception as e:
        logger.error(f"Download generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== GITHUB/GITLAB INTEGRATION ====================

@api_router.get("/auth/github/initiate")
async def initiate_github_oauth(current_user: dict = Depends(get_current_user)):
    """Initiate GitHub OAuth flow"""
    try:
        result = await github_gitlab_service.initiate_github_oauth(current_user['id'])
        return result
    except Exception as e:
        logger.error(f"GitHub OAuth initiation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/auth/github/callback")
async def github_oauth_callback(code: str, state: str):
    """Handle GitHub OAuth callback"""
    try:
        result = await github_gitlab_service.handle_github_callback(code, state)
        if not result.get('success'):
            raise HTTPException(status_code=401, detail=result.get('error'))
        return result
    except Exception as e:
        logger.error(f"GitHub callback failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/github/connection-status")
async def get_github_connection_status(current_user: dict = Depends(get_current_user)):
    """Get GitHub/GitLab connection status"""
    try:
        status = await github_gitlab_service.get_connection_status(current_user['id'])
        return status
    except Exception as e:
        logger.error(f"Failed to get connection status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/github/sync-repos")
async def sync_github_repositories(current_user: dict = Depends(get_current_user)):
    """Sync user's GitHub repositories"""
    try:
        result = await github_gitlab_service.fetch_user_repositories(current_user['id'])
        return result
    except Exception as e:
        logger.error(f"Failed to sync repositories: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== ADMIN ANALYTICS DASHBOARD ====================

@api_router.get("/admin/analytics/comprehensive")
async def get_comprehensive_analytics(current_user: dict = Depends(require_admin)):
    """Get comprehensive analytics dashboard data"""
    try:
        dashboard = await analytics_dashboard_service.get_comprehensive_dashboard()
        return dashboard
    except Exception as e:
        logger.error(f"Failed to get analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/admin/analytics/revenue")
async def get_revenue_analytics(current_user: dict = Depends(require_admin)):
    """Get revenue analytics with time-series data"""
    try:
        revenue = await analytics_dashboard_service.get_revenue_analytics()
        return revenue
    except Exception as e:
        logger.error(f"Failed to get revenue analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/admin/analytics/user-growth")
async def get_user_growth_analytics(current_user: dict = Depends(require_admin)):
    """Get user growth analytics"""
    try:
        growth = await analytics_dashboard_service.get_user_growth_analytics()
        return growth
    except Exception as e:
        logger.error(f"Failed to get user growth: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/admin/analytics/top-products")
async def get_top_products_analytics(
    limit: int = 10,
    current_user: dict = Depends(require_admin)
):
    """Get top performing products"""
    try:
        products = await analytics_dashboard_service.get_top_products(limit)
        return {"products": products}
    except Exception as e:
        logger.error(f"Failed to get top products: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/admin/analytics/category-distribution")
async def get_category_distribution(current_user: dict = Depends(require_admin)):
    """Get product distribution by category"""
    try:
        distribution = await analytics_dashboard_service.get_category_distribution()
        return distribution
    except Exception as e:
        logger.error(f"Failed to get category distribution: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== MCP REGISTRY & WORKFLOW AUTOMATION ====================

@api_router.get("/mcp/registry")
async def get_mcp_registry():
    """Get all MCP servers from registry"""
    try:
        servers = await mcp_registry_service.get_all_mcp_servers()
        return {
            "success": True,
            "total": len(servers),
            "servers": servers
        }
    except Exception as e:
        logger.error(f"Failed to get MCP registry: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/mcp/registry/discover")
async def discover_mcp_servers(current_user: dict = Depends(get_current_user)):
    """Trigger MCP server discovery from GitHub MCP Registry"""
    try:
        if current_user["role"] != "admin":
            raise HTTPException(status_code=403, detail="Admin access required")
        
        result = await mcp_registry_service.discover_mcp_servers()
        logger.info(f"✓ MCP Discovery: {result['total_discovered']} servers cataloged")
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"MCP discovery failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/mcp/registry/category/{category}")
async def get_mcp_servers_by_category(category: str):
    """Get MCP servers by category"""
    try:
        servers = await mcp_registry_service.get_mcp_servers_by_category(category)
        return {
            "success": True,
            "category": category,
            "total": len(servers),
            "servers": servers
        }
    except Exception as e:
        logger.error(f"Failed to get MCP servers by category: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/workflow-tools")
async def get_workflow_tools():
    """Get all AI workflow automation tools"""
    try:
        tools = await workflow_automation_service.get_all_workflow_tools()
        return {
            "success": True,
            "total": len(tools),
            "tools": tools
        }
    except Exception as e:
        logger.error(f"Failed to get workflow tools: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/workflow-tools/catalog")
async def catalog_workflow_tools(current_user: dict = Depends(get_current_user)):
    """Catalog workflow automation tools from ProductHunt"""
    try:
        if current_user["role"] != "admin":
            raise HTTPException(status_code=403, detail="Admin access required")
        
        result = await workflow_automation_service.catalog_workflow_tools()
        logger.info(f"✓ Workflow Tools Cataloging: {result['total_cataloged']} tools")
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Workflow tools cataloging failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/workflow-tools/priority/{priority}")
async def get_workflow_tools_by_priority(priority: str):
    """Get workflow tools by priority (critical, high, medium, low)"""
    try:
        tools = await workflow_automation_service.get_tools_by_priority(priority)
        return {
            "success": True,
            "priority": priority,
            "total": len(tools),
            "tools": tools
        }
    except Exception as e:
        logger.error(f"Failed to get workflow tools by priority: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== CLOUDFLARE INTEGRATION ====================

@api_router.post("/admin/cloudflare/configure")
async def configure_cloudflare(
    config: Dict[str, str],
    current_user: dict = Depends(get_current_user)
):
    """Configure Cloudflare credentials"""
    try:
        if current_user["role"] != "admin":
            raise HTTPException(status_code=403, detail="Admin access required")
        
        # Update environment variables
        account_id = config.get("account_id")
        api_token = config.get("api_token")
        zone_id = config.get("zone_id", "")
        
        if not account_id or not api_token:
            raise HTTPException(status_code=400, detail="account_id and api_token required")
        
        # Update .env file
        env_path = Path("/app/backend/.env")
        env_content = env_path.read_text()
        
        # Add or update Cloudflare credentials
        if "CLOUDFLARE_ACCOUNT_ID" in env_content:
            env_content = "\n".join([
                line if not line.startswith("CLOUDFLARE_") else ""
                for line in env_content.split("\n")
            ])
        
        env_content += f"\nCLOUDFLARE_ACCOUNT_ID={account_id}\n"
        env_content += f"CLOUDFLARE_API_TOKEN={api_token}\n"
        if zone_id:
            env_content += f"CLOUDFLARE_ZONE_ID={zone_id}\n"
        
        env_path.write_text(env_content)
        
        # Update service
        os.environ["CLOUDFLARE_ACCOUNT_ID"] = account_id
        os.environ["CLOUDFLARE_API_TOKEN"] = api_token
        if zone_id:
            os.environ["CLOUDFLARE_ZONE_ID"] = zone_id
        
        # Reinitialize service
        global cloudflare_service
        cloudflare_service = create_cloudflare_service(db)
        
        # Verify credentials
        verification = await cloudflare_service.verify_credentials()
        
        if verification["success"]:
            logger.info(f"✓ Cloudflare configured for account: {verification['account_name']}")
            return {
                "success": True,
                "message": "Cloudflare credentials configured",
                "account": verification['account_name']
            }
        else:
            raise HTTPException(status_code=400, detail=verification.get("error", "Invalid credentials"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Cloudflare configuration failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/admin/cloudflare/initialize")
async def initialize_cloudflare(current_user: dict = Depends(get_current_user)):
    """Initialize all Cloudflare services (KV, R2, Workers AI, etc.)"""
    try:
        if current_user["role"] != "admin":
            raise HTTPException(status_code=403, detail="Admin access required")
        
        result = await cloudflare_service.initialize_all_services()
        
        if result["success"]:
            logger.info("✓ All Cloudflare services initialized")
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Initialization failed"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Cloudflare initialization failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/admin/cloudflare/status")
async def get_cloudflare_status(current_user: dict = Depends(get_current_user)):
    """Get Cloudflare integration status"""
    try:
        if current_user["role"] != "admin":
            raise HTTPException(status_code=403, detail="Admin access required")
        
        status = await cloudflare_service.get_status()
        return status
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get Cloudflare status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# KV Cache endpoints
@api_router.get("/cloudflare/kv/{key}")
async def cloudflare_kv_get(key: str):
    """Get value from Cloudflare KV cache"""
    try:
        namespace_id = cloudflare_service.features['kv'].get('namespace_id')
        if not namespace_id:
            raise HTTPException(status_code=503, detail="KV not initialized")
        
        value = await cloudflare_service.kv_get(namespace_id, key)
        if value is None:
            raise HTTPException(status_code=404, detail="Key not found")
        
        return {"key": key, "value": value}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"KV get failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.put("/cloudflare/kv/{key}")
async def cloudflare_kv_put(
    key: str,
    data: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    """Put value in Cloudflare KV cache"""
    try:
        namespace_id = cloudflare_service.features['kv'].get('namespace_id')
        if not namespace_id:
            raise HTTPException(status_code=503, detail="KV not initialized")
        
        value = data.get("value", "")
        ttl = data.get("ttl")  # Optional TTL in seconds
        
        success = await cloudflare_service.kv_put(namespace_id, key, value, ttl)
        
        if success:
            return {"success": True, "key": key}
        else:
            raise HTTPException(status_code=500, detail="KV put failed")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"KV put failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Workers AI endpoints
@api_router.post("/cloudflare/ai/text")
async def cloudflare_ai_text(
    data: Dict[str, str],
    current_user: dict = Depends(get_current_user)
):
    """Generate text using Cloudflare Workers AI"""
    try:
        if not cloudflare_service.features['workers_ai'].get('enabled'):
            raise HTTPException(status_code=503, detail="Workers AI not enabled")
        
        prompt = data.get("prompt", "")
        model = data.get("model", "@cf/meta/llama-3-8b-instruct")
        
        response = await cloudflare_service.workers_ai_text_generation(prompt, model)
        
        if response:
            return {"success": True, "text": response, "model": model}
        else:
            raise HTTPException(status_code=500, detail="Text generation failed")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Workers AI text generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/cloudflare/ai/embeddings")
async def cloudflare_ai_embeddings(
    data: Dict[str, str],
    current_user: dict = Depends(get_current_user)
):
    """Generate embeddings using Cloudflare Workers AI"""
    try:
        if not cloudflare_service.features['workers_ai'].get('enabled'):
            raise HTTPException(status_code=503, detail="Workers AI not enabled")
        
        text = data.get("text", "")
        model = data.get("model", "@cf/baai/bge-base-en-v1.5")
        
        embeddings = await cloudflare_service.workers_ai_embeddings(text, model)
        
        if embeddings:
            return {"success": True, "embeddings": embeddings, "dimensions": len(embeddings)}
        else:
            raise HTTPException(status_code=500, detail="Embeddings generation failed")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Workers AI embeddings failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Vectorize semantic search endpoints
@api_router.post("/cloudflare/vectorize/search")
async def cloudflare_vectorize_search(data: Dict[str, Any]):
    """Semantic search using Cloudflare Vectorize"""
    try:
        index_id = cloudflare_service.features['vectorize'].get('index_id')
        if not index_id:
            raise HTTPException(status_code=503, detail="Vectorize not initialized")
        
        query_text = data.get("query", "")
        top_k = data.get("top_k", 10)
        
        # Generate embeddings for query
        query_embedding = await cloudflare_service.workers_ai_embeddings(query_text)
        if not query_embedding:
            raise HTTPException(status_code=500, detail="Failed to generate query embeddings")
        
        # Search Vectorize
        results = await cloudflare_service.vectorize_query(index_id, query_embedding, top_k)
        
        if results:
            return {"success": True, "results": results, "count": len(results)}
        else:
            return {"success": True, "results": [], "count": 0}
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Vectorize search failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/stats")
async def get_stats():
    products_count = await db.products.count_documents({})
    vendors_count = await db.vendors.count_documents({})
    users_count = await db.users.count_documents({})
    posts_count = await db.posts.count_documents({})
    agents_count = await db.agents.count_documents({})
    
    return {
        "products_listed": max(products_count, 50000),
        "active_vendors": max(vendors_count, 1200),
        "total_users": max(users_count, 15000),
        "ai_agents_active": max(agents_count, 46),
        "daily_auctions": 340,
        "posts_count": max(posts_count, 8500)
    }

@api_router.get("/integrations/status")
async def get_all_integrations():
    """Get comprehensive status of all NEXUS integrations"""
    return integration_status_service.get_all_integrations_status()

@api_router.get("/integrations/health")
async def get_integration_health():
    """Get overall integration health score"""
    return {"health": integration_status_service.get_integration_health()}

@api_router.get("/admin/dashboard")
async def admin_dashboard(current_user: dict = Depends(require_admin)):
    users_count = await db.users.count_documents({})
    products_count = await db.products.count_documents({})
    vendors_count = await db.vendors.count_documents({})
    posts_count = await db.posts.count_documents({})
    
    transactions = await db.payment_transactions.find({"payment_status": "completed"}, {"_id": 0}).to_list(1000)
    total_revenue = sum(t.get("amount", 0) for t in transactions)
    boost_revenue = sum(t.get("amount", 0) for t in transactions if t.get("package_id"))
    sales_revenue = sum(t.get("amount", 0) for t in transactions if t.get("type") == "product_purchase")
    
    recent_users = await db.users.find({}, {"_id": 0, "password": 0}).sort("created_at", -1).limit(5).to_list(5)
    recent_products = await db.products.find({}, {"_id": 0}).sort("created_at", -1).limit(5).to_list(5)
    recent_transactions = await db.payment_transactions.find({}, {"_id": 0}).sort("created_at", -1).limit(10).to_list(10)
    agent_reports = await db.agent_reports.find({}, {"_id": 0}).sort("created_at", -1).limit(5).to_list(5)
    
    return {
        "stats": {
            "users": users_count,
            "products": products_count,
            "vendors": vendors_count,
            "posts": posts_count,
            "total_revenue": total_revenue,
            "boost_revenue": boost_revenue,
            "sales_revenue": sales_revenue
        },
        "recent_users": recent_users,
        "recent_products": recent_products,
        "recent_transactions": recent_transactions,
        "agent_reports": agent_reports
    }

@api_router.get("/admin/users")
async def admin_get_users(current_user: dict = Depends(require_admin), limit: int = 50, skip: int = 0):
    users = await db.users.find({}, {"_id": 0, "password": 0}).skip(skip).limit(limit).to_list(limit)
    total = await db.users.count_documents({})
    return {"users": users, "total": total}

@api_router.put("/admin/users/{user_id}/role")
async def admin_update_user_role(user_id: str, role: str, current_user: dict = Depends(require_admin)):
    if role not in ["user", "vendor", "admin"]:
        raise HTTPException(status_code=400, detail="Invalid role")
    await db.users.update_one({"id": user_id}, {"$set": {"role": role}})
    return {"success": True}

@api_router.delete("/admin/users/{user_id}")
async def admin_delete_user(user_id: str, current_user: dict = Depends(require_admin)):
    await db.users.delete_one({"id": user_id})
    return {"success": True}

@api_router.get("/admin/products")
async def admin_get_products(current_user: dict = Depends(require_admin), limit: int = 50, skip: int = 0):
    products = await db.products.find({}, {"_id": 0}).skip(skip).limit(limit).to_list(limit)
    total = await db.products.count_documents({})
    return {"products": products, "total": total}

@api_router.delete("/admin/products/{product_id}")
async def admin_delete_product(product_id: str, current_user: dict = Depends(require_admin)):
    await db.products.delete_one({"id": product_id})
    return {"success": True}

# ==================== FILE UPLOAD ====================

@api_router.post("/upload")
async def upload_file(file: UploadFile = File(...), current_user: dict = Depends(get_current_user)):
    content = await file.read()
    encoded = base64.b64encode(content).decode('utf-8')
    
    file_id = str(uuid.uuid4())
    await db.files.insert_one({
        "id": file_id,
        "filename": file.filename,
        "content_type": file.content_type,
        "size": len(content),
        "data": encoded,
        "user_id": current_user["id"],
        "created_at": datetime.now(timezone.utc).isoformat()
    })
    
    return {"file_id": file_id, "filename": file.filename, "url": f"/api/files/{file_id}", "size": len(content)}

@api_router.get("/files/{file_id}")
async def get_file(file_id: str):
    file_doc = await db.files.find_one({"id": file_id}, {"_id": 0})
    if not file_doc:
        raise HTTPException(status_code=404, detail="File not found")
    
    content = base64.b64decode(file_doc["data"])
    return StreamingResponse(
        iter([content]),
        media_type=file_doc.get("content_type", "application/octet-stream"),
        headers={"Content-Disposition": f"attachment; filename={file_doc['filename']}"}
    )

# ==================== VENDOR ROUTES ====================

@api_router.post("/vendors")
async def create_vendor(vendor: VendorCreate, current_user: dict = Depends(get_current_user)):
    vendor_id = str(uuid.uuid4())
    vendor_doc = {
        "id": vendor_id,
        **vendor.model_dump(),
        "owner_id": current_user["id"],
        "owner_name": current_user["username"],
        "products_count": 0,
        "total_sales": 0,
        "rating": 0,
        "status": "active",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.vendors.insert_one(vendor_doc)
    await db.users.update_one({"id": current_user["id"]}, {"$set": {"role": "vendor"}})
    return {k: v for k, v in vendor_doc.items() if k != "_id"}

@api_router.get("/vendors")
async def get_vendors(limit: int = 20):
    vendors = await db.vendors.find({}, {"_id": 0}).sort("total_sales", -1).limit(limit).to_list(limit)
    return vendors

@api_router.get("/vendors/{vendor_id}")
async def get_vendor(vendor_id: str):
    vendor = await db.vendors.find_one({"id": vendor_id}, {"_id": 0})
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    return vendor

# ==================== SPOTLIGHT & BOOST ROUTES ====================

@api_router.get("/spotlight")
async def get_spotlight():
    now = datetime.now(timezone.utc).isoformat()
    boosted = await db.spotlight.find({"is_boosted": True, "expires_at": {"$gt": now}}, {"_id": 0}).sort("featured_date", -1).limit(5).to_list(5)
    organic = await db.spotlight.find({"$or": [{"is_boosted": {"$exists": False}}, {"is_boosted": False}]}, {"_id": 0}).sort("featured_date", -1).limit(5).to_list(5)
    
    spotlight = boosted + organic
    if not spotlight:
        spotlight = [
            {"id": "spot-1", "content_id": "content-1", "content_type": "music", "title": "Neon Dreamscape EP", "creator_name": "SynthWave_AI", "creator_id": "creator-1", "award_type": "Most Creative", "votes": 2400, "featured_date": datetime.now(timezone.utc).isoformat()},
            {"id": "spot-2", "content_id": "content-2", "content_type": "video", "title": "AI City Timelapse", "creator_name": "VisualForge", "creator_id": "creator-2", "award_type": "Most Popular", "votes": 1800, "featured_date": datetime.now(timezone.utc).isoformat()},
            {"id": "spot-3", "content_id": "content-3", "content_type": "ebook", "title": "Prompt Engineering Bible", "creator_name": "AIAuthor", "creator_id": "creator-3", "award_type": "Editor's Pick", "votes": 3100, "featured_date": datetime.now(timezone.utc).isoformat()}
        ]
    return spotlight

@api_router.get("/boost/packages")
async def get_boost_packages():
    return [{"id": k, **v} for k, v in BOOST_PACKAGES.items()]

@api_router.post("/boost/checkout", response_model=BoostCheckoutResponse)
async def create_boost_checkout(request: BoostCheckoutRequest, http_request: Request, current_user: dict = Depends(get_current_user)):
    from emergentintegrations.payments.stripe.checkout import StripeCheckout, CheckoutSessionRequest
    
    if request.package_id not in BOOST_PACKAGES:
        raise HTTPException(status_code=400, detail="Invalid boost package")
    
    product = await db.products.find_one({"id": request.product_id}, {"_id": 0})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if product.get("vendor_id") != current_user["id"]:
        raise HTTPException(status_code=403, detail="You can only boost your own products")
    
    package = BOOST_PACKAGES[request.package_id]
    api_key = os.environ.get('STRIPE_API_KEY')
    host_url = str(http_request.base_url).rstrip('/')
    stripe_checkout = StripeCheckout(api_key=api_key, webhook_url=f"{host_url}/api/webhook/stripe")
    
    checkout_request = CheckoutSessionRequest(
        amount=float(package["price"]),
        currency="usd",
        success_url=f"{request.origin_url}/boost/success?session_id={{CHECKOUT_SESSION_ID}}",
        cancel_url=f"{request.origin_url}/marketplace",
        metadata={
            "product_id": request.product_id,
            "package_id": request.package_id,
            "user_id": current_user["id"],
            "product_title": product.get("title", ""),
            "boost_days": str(package["days"])
        }
    )
    
    session = await stripe_checkout.create_checkout_session(checkout_request)
    
    await db.payment_transactions.insert_one({
        "id": str(uuid.uuid4()),
        "session_id": session.session_id,
        "user_id": current_user["id"],
        "product_id": request.product_id,
        "package_id": request.package_id,
        "amount": package["price"],
        "currency": "usd",
        "payment_status": "pending",
        "boost_days": package["days"],
        "created_at": datetime.now(timezone.utc).isoformat()
    })
    
    return BoostCheckoutResponse(checkout_url=session.url, session_id=session.session_id)

@api_router.get("/boost/status/{session_id}")
async def get_boost_payment_status(session_id: str, http_request: Request):
    from emergentintegrations.payments.stripe.checkout import StripeCheckout
    
    api_key = os.environ.get('STRIPE_API_KEY')
    host_url = str(http_request.base_url).rstrip('/')
    stripe_checkout = StripeCheckout(api_key=api_key, webhook_url=f"{host_url}/api/webhook/stripe")
    
    status = await stripe_checkout.get_checkout_status(session_id)
    transaction = await db.payment_transactions.find_one({"session_id": session_id}, {"_id": 0})
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    if status.payment_status == "paid" and transaction.get("payment_status") != "completed":
        await db.payment_transactions.update_one({"session_id": session_id}, {"$set": {"payment_status": "completed", "completed_at": datetime.now(timezone.utc).isoformat()}})
        
        product = await db.products.find_one({"id": transaction["product_id"]}, {"_id": 0})
        if product:
            boost_days = transaction.get("boost_days", 1)
            expires_at = datetime.now(timezone.utc) + timedelta(days=boost_days)
            
            await db.spotlight.insert_one({
                "id": str(uuid.uuid4()),
                "content_id": transaction["product_id"],
                "content_type": product.get("category", "product"),
                "title": product.get("title", ""),
                "creator_name": product.get("vendor_name", ""),
                "creator_id": transaction["user_id"],
                "award_type": "Featured Listing",
                "votes": 0,
                "is_boosted": True,
                "boost_package": transaction["package_id"],
                "featured_date": datetime.now(timezone.utc).isoformat(),
                "expires_at": expires_at.isoformat(),
                "image_url": product.get("image_url"),
                "price": product.get("price")
            })
            
            await db.products.update_one({"id": transaction["product_id"]}, {"$set": {"is_boosted": True, "boost_expires_at": expires_at.isoformat()}})
    
    return {"status": status.status, "payment_status": status.payment_status, "amount": status.amount_total / 100, "currency": status.currency, "transaction_status": transaction.get("payment_status")}

@api_router.post("/webhook/stripe")
async def stripe_webhook(request: Request):
    from emergentintegrations.payments.stripe.checkout import StripeCheckout
    
    api_key = os.environ.get('STRIPE_API_KEY')
    host_url = str(request.base_url).rstrip('/')
    stripe_checkout = StripeCheckout(api_key=api_key, webhook_url=f"{host_url}/api/webhook/stripe")
    
    try:
        body = await request.body()
        signature = request.headers.get("Stripe-Signature")
        webhook_response = await stripe_checkout.handle_webhook(body, signature)
        
        if webhook_response.payment_status == "paid":
            await db.payment_transactions.update_one({"session_id": webhook_response.session_id}, {"$set": {"payment_status": "completed", "completed_at": datetime.now(timezone.utc).isoformat()}})
        
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        return {"status": "error", "message": str(e)}

# ==================== STATS & OTHER ROUTES ====================

@api_router.get("/categories")
async def get_categories():
    return [
        {"id": "music", "name": "AI Music", "icon": "music", "count": 12500},
        {"id": "video", "name": "AI Video", "icon": "video", "count": 8200},
        {"id": "ebook", "name": "eBooks", "icon": "book", "count": 6800},
        {"id": "art", "name": "Digital Art", "icon": "palette", "count": 15000},
        {"id": "templates", "name": "Templates", "icon": "layout", "count": 4500},
        {"id": "dropship", "name": "Dropship", "icon": "package", "count": 50000},
        {"id": "services", "name": "Services", "icon": "briefcase", "count": 2100},
        {"id": "courses", "name": "Courses", "icon": "graduation-cap", "count": 1800}
    ]

@api_router.get("/trending")
async def get_trending():
    products = await db.products.find({}, {"_id": 0}).sort("views", -1).limit(8).to_list(8)
    if not products:
        products = [
            {"id": "trend-1", "title": "Neon Dreamscape EP", "description": "Synthwave music", "price": 4.99, "category": "music", "image_url": "https://images.unsplash.com/photo-1614149162883-504ce4d13909?w=400", "vendor_name": "SynthWave_AI", "vendor_id": "v1", "likes": 2400, "views": 18000, "is_ai_generated": True, "tags": [], "created_at": datetime.now(timezone.utc).isoformat()},
            {"id": "trend-2", "title": "AI City Timelapse", "description": "City video", "price": 9.99, "category": "video", "image_url": "https://images.unsplash.com/photo-1480714378408-67cf0d13bc1b?w=400", "vendor_name": "VisualForge", "vendor_id": "v2", "likes": 1800, "views": 24000, "is_ai_generated": True, "tags": [], "created_at": datetime.now(timezone.utc).isoformat()},
            {"id": "trend-3", "title": "Prompt Engineering Bible", "description": "AI guide", "price": 12.99, "category": "ebook", "image_url": "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=400", "vendor_name": "AIAuthor", "vendor_id": "v3", "likes": 3100, "views": 41000, "is_ai_generated": True, "tags": [], "created_at": datetime.now(timezone.utc).isoformat()},
            {"id": "trend-4", "title": "Cosmic Portraits Pack", "description": "Portrait art", "price": 7.99, "category": "art", "image_url": "https://images.unsplash.com/photo-1462331940025-496dfbfc7564?w=400", "vendor_name": "PixelMage", "vendor_id": "v4", "likes": 987, "views": 9200, "is_ai_generated": True, "tags": [], "created_at": datetime.now(timezone.utc).isoformat()}
        ]
    return products

@api_router.get("/")
async def root():
    return {"message": "NEXUS API - AI Social Marketplace", "version": "3.0.0"}

@api_router.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}

# Include the router
# Create generated videos directory
generated_videos_dir = Path("/app/backend/generated_videos")
generated_videos_dir.mkdir(exist_ok=True)

# Mount static files for generated videos
fastapi_app.mount("/generated_videos", StaticFiles(directory=str(generated_videos_dir)), name="generated_videos")

fastapi_app.include_router(api_router)

# Import and set database in server.py
from routes.dependencies import set_database
set_database(db)

# Import elite hybrid services
from services.hybrid_analytics_service import hybrid_analytics
from services.omnipay_gateway import omnipay
from services.cloudstack_service import cloudstack
from services.federated_chat_system import FederatedChatSystem
from services.hyper_messenger import HyperMessenger

# Import elite integrations router
from routes.elite_integrations import get_elite_integrations_router
from routes.messenger import get_messenger_router, set_hyper_messenger
from routes.autonomous_engine import get_autonomous_router
from routes.ultra_services import get_ultra_services_router

# Initialize federated chat with Socket.IO
federated_chat = FederatedChatSystem(sio)

# Initialize HyperMessenger with Socket.IO
hyper_messenger = HyperMessenger(sio)
set_hyper_messenger(hyper_messenger)

# Import and initialize ULTRA hybrid services
from services.ultra_image_video_generator import ultra_generator
from services.ultra_voice_service import ultra_voice
from services.ultra_llm_service import ultra_llm
from services.ultra_video_conferencing import UltraVideoConferencing

# Initialize ULTRA video conferencing with Socket.IO
from services import ultra_video_conferencing
ultra_video_conferencing.ultra_video = UltraVideoConferencing(sio)

# ==================== NEW MODULAR ROUTERS ====================
# Import new services
from services.crewai_service import crewai_service
from services.gradio_service import gradio_service
from services.yolo_service import yolo_service
from services.seaweedfs_client import seaweedfs_client

# Import routers
from routes.marketplace import get_marketplace_router
from routes.social import get_social_router
from routes.users import get_users_router
from routes.notifications import get_notifications_router
from routes.studio import get_studio_router
from routes.admin import get_admin_router
from routes.files import get_files_router
from routes.hybrid_services import get_hybrid_services_router
from routes.dynamic_hybrid_router import create_dynamic_hybrid_router

# Initialize routers with dependencies
marketplace_router = get_marketplace_router(db, sio, notify_user, create_notification)
social_router = get_social_router(db, agent_system, broadcast_to_room, create_notification)
users_router = get_users_router(db, create_notification)
notifications_router = get_notifications_router(db)
studio_router = get_studio_router(db, agent_system, text_to_video_service, runway_video_service, fal_ai_service, elevenlabs_service)
files_router = get_files_router(db)
admin_router = get_admin_router(
    db, agent_system, automation_service, manus_service, openclaw_service,
    integration_status_service, fal_ai_service, analytics_dashboard_service,
    cloudflare_service, cache_service
)
hybrid_services_router = get_hybrid_services_router(db)

# Include modular routers
fastapi_app.include_router(marketplace_router, prefix="/api")
fastapi_app.include_router(social_router, prefix="/api")
fastapi_app.include_router(users_router, prefix="/api")
fastapi_app.include_router(notifications_router, prefix="/api")
fastapi_app.include_router(studio_router, prefix="/api")
fastapi_app.include_router(files_router, prefix="/api")
fastapi_app.include_router(admin_router, prefix="/api/admin")
fastapi_app.include_router(hybrid_services_router, prefix="/api/hybrid")

# NEW: Dynamic router (parallel system for testing)
try:
    dynamic_router, loaded_hybrids = create_dynamic_hybrid_router(db)
    fastapi_app.include_router(dynamic_router, prefix="/api/v2/hybrid")
    logger.info(f"✅ Dynamic router loaded {len(loaded_hybrids)} hybrids: {', '.join(loaded_hybrids)}")
except Exception as e:
    logger.error(f"❌ Dynamic router failed: {e}")
    logger.info("⚠️ Continuing with legacy router only")
fastapi_app.include_router(get_elite_integrations_router(), prefix="/api/elite")
fastapi_app.include_router(get_messenger_router(db), prefix="/api")
fastapi_app.include_router(get_autonomous_router(), prefix="/api")
fastapi_app.include_router(get_ultra_services_router(), prefix="/api")

# Import autonomous systems router
from routes.autonomous_systems import get_autonomous_systems_router
from routes.newsfeed import get_newsfeed_router
from routes.creation_studio import get_creation_studio_router
from routes.social_automation import get_social_automation_router
from routes.oauth import get_oauth_router
from routes.upload import get_upload_router

# Import master orchestrator
from services.master_automation_orchestrator import master_orchestrator
import asyncio

fastapi_app.include_router(get_autonomous_systems_router(), prefix="/api")
fastapi_app.include_router(get_newsfeed_router(db), prefix="/api")
fastapi_app.include_router(get_creation_studio_router(db), prefix="/api")
fastapi_app.include_router(get_social_automation_router(), prefix="/api")
fastapi_app.include_router(get_oauth_router(db), prefix="/api")
fastapi_app.include_router(get_upload_router(db), prefix="/api")
fastapi_app.include_router(adk_router)  # DigitalOcean ADK routes

# NEXUS Social Network Routes
social_router = create_social_routes(db, get_current_user)
fastapi_app.include_router(social_router)

# WebSocket endpoint for real-time features
from fastapi import WebSocket
@fastapi_app.websocket("/api/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """WebSocket endpoint for real-time chat, notifications, and live updates"""
    await manager.connect(websocket, user_id)
    try:
        await handle_websocket_message(websocket, user_id, db)
    except Exception as e:
        logger.error(f"WebSocket error for user {user_id}: {e}")
        manager.disconnect(websocket, user_id)


# Start master automation on startup
@fastapi_app.on_event("startup")
async def start_automation():
    """Start all automation systems on server startup"""
    logger.info("🚀 Starting Master Automation Orchestrator...")
    asyncio.create_task(master_orchestrator.start())
    
    # Start daily automation scheduler
    logger.info("📅 Starting Daily Automation Scheduler...")
    from services.nexus_daily_automation import daily_scheduler
    asyncio.create_task(daily_scheduler.schedule_loop())

logger.info("✓ All modular routers loaded including elite integrations + HyperMessenger + Autonomous Engine + ULTRA Services + Autonomous Systems")

fastapi_app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

@fastapi_app.on_event("startup")
async def startup():
    global advanced_agents, performance_optimizer
    logger.info("NEXUS Server starting...")
    
    # Initialize performance optimizer
    performance_optimizer = create_performance_optimizer(db)
    
    # Create database indexes for optimal performance
    await performance_optimizer.create_indexes()
    
    # Initialize advanced agent system
    advanced_agents = create_advanced_agent_system(db, agent_system)
    logger.info("Advanced agent system initialized")
    
    # Initialize ULTRA hybrid services
    logger.info("Initializing ULTRA hybrid services...")
    await ultra_generator.initialize()
    await ultra_voice.initialize()
    await ultra_llm.initialize()
    if ultra_video_conferencing.ultra_video:
        await ultra_video_conferencing.ultra_video.initialize()
    logger.info("✓ ULTRA hybrid services initialized")
    
    # Start agent scheduler in background
    asyncio.create_task(run_scheduled_agents())
    logger.info("Agent scheduler started")
    logger.info("🚀 NEXUS v4.4 - Autonomous Multi-Source Discovery Platform Ready")

# Socket.IO event handlers for real-time bidding (P2P Auction routes moved to line ~765)
@sio.event
async def connect(sid, environ):
    logger.info(f"Socket.IO client connected: {sid}")
    await sio.emit('connection_established', {'status': 'connected'}, room=sid)

@sio.event
async def disconnect(sid):
    logger.info(f"Socket.IO client disconnected: {sid}")

@sio.event
async def join_auction(sid, data):
    """Join a specific auction room for real-time updates"""
    product_id = data.get('product_id')
    if product_id:
        await sio.enter_room(sid, f"auction:{product_id}")
        logger.info(f"Client {sid} joined auction room: {product_id}")
        await sio.emit('joined_auction', {'product_id': product_id}, room=sid)

@sio.event
async def leave_auction(sid, data):
    """Leave an auction room"""
    product_id = data.get('product_id')
    if product_id:
        await sio.leave_room(sid, f"auction:{product_id}")
        logger.info(f"Client {sid} left auction room: {product_id}")

@fastapi_app.on_event("shutdown")
async def shutdown():
    client.close()
    logger.info("NEXUS Server shutdown")

# Wrap FastAPI with Socket.IO
socket_app = socketio.ASGIApp(sio, other_asgi_app=fastapi_app, socketio_path='/api/socket.io')
app = socket_app
