"""
Authentication routes
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timezone
import uuid
import bcrypt
import jwt
import os

router = APIRouter(prefix="/auth", tags=["Authentication"])

# JWT Config
JWT_SECRET = os.environ.get('JWT_SECRET', 'nexus-secret-key-2025')
JWT_ALGORITHM = "HS256"

# Models
class UserRegister(BaseModel):
    email: str
    password: str
    username: str

class UserLogin(BaseModel):
    email: str
    password: str

# Helper functions
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

def get_auth_router(db: AsyncIOMotorDatabase):
    """Create auth router with database dependency"""
    
    from routes.dependencies import get_current_user
    
    @router.post("/register")
    async def register(user: UserRegister):
        """Register a new user"""
        existing = await db.users.find_one({"email": user.email}, {"_id": 0})
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        user_id = str(uuid.uuid4())
        user_doc = {
            "id": user_id,
            "email": user.email,
            "username": user.username,
            "password": hash_password(user.password),
            "role": "user",
            "avatar": f"https://api.dicebear.com/7.x/avataaars/svg?seed={user.username}",
            "bio": "",
            "location": "",
            "website": "",
            "social_links": {},
            "followers": [],
            "following": [],
            "created_at": datetime.now(timezone.utc).isoformat(),
            "total_sales": 0,
            "total_earnings": 0.0,
            "verified": False
        }
        await db.users.insert_one(user_doc)
        
        token = create_token(user_id, user.email, "user")
        user_doc.pop("password", None)
        
        return {"token": token, "user": user_doc}
    
    @router.post("/login")
    async def login(credentials: UserLogin):
        """Login user"""
        user = await db.users.find_one({"email": credentials.email}, {"_id": 0})
        if not user or not verify_password(credentials.password, user["password"]):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        token = create_token(user["id"], user["email"], user.get("role", "user"))
        user.pop("password", None)
        
        return {"token": token, "user": user}
    
    @router.get("/me")
    async def get_me(current_user: dict = Depends(get_current_user)):
        """Get current user profile"""
        return current_user
    
    return router
