"""
NEXUS Hybrid: OpenClaw AI Agent
#1 Trending GitHub AI project (302k+ stars) - Personal AI agent platform
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, List
import os
from dotenv import load_dotenv
import logging

load_dotenv()
logger = logging.getLogger(__name__)

class OpenClawRequest(BaseModel):
    task: str
    platform: str = "web"
    skill: Optional[str] = None

class OpenClawEngine:
    def __init__(self, db):
        self.db = db
    
    def get_capabilities(self) -> Dict:
        return {
            "name": "OpenClaw",
            "description": "#1 Trending AI on GitHub (302k stars) - Cross-platform personal AI agent",
            "category": "ai_agents",
            "provider": "OpenClaw",
            "github": "https://github.com/openclaw/openclaw",
            "stars": "302,000+",
            "rank": "#1 Trending AI 2026",
            "features": [
                "Cross-platform agent (Mac/Linux/Windows)",
                "Custom Python skills",
                "Telegram/Messaging integration",
                "Local deployment (Ollama)",
                "Device task execution",
                "ClawBox hardware support"
            ],
            "use_cases": [
                "Personal AI assistant",
                "Device automation",
                "Custom workflows",
                "Private AI deployment"
            ],
            "platforms": [
                "macOS",
                "Linux",
                "Windows (WSL)",
                "ClawBox hardware"
            ],
            "installation": "curl -fsSL https://openclaw.ai/install.sh | bash",
            "requirements": {
                "node": "v22.14+",
                "python": "3.8+",
                "ram": "8GB+"
            },
            "status": "active",
            "note": "Fastest-growing AI project in history (210k+ stars in early 2026)"
        }
    
    async def run_task(self, request: OpenClawRequest) -> Dict:
        """Execute an OpenClaw task"""
        try:
            return {
                "success": True,
                "result": f"[DEMO] OpenClaw agent on {request.platform} would execute: {request.task}",
                "platform": request.platform,
                "note": "OpenClaw requires dedicated installation. Visit openclaw.ai for setup."
            }
        except Exception as e:
            logger.error(f"OpenClaw execution error: {e}")
            raise HTTPException(status_code=500, detail=str(e))

def create_openclaw_engine(db):
    return OpenClawEngine(db)

# Create global instance for ultimate controller
hybrid_openclaw = None
def init_hybrid(db):
    global hybrid_openclaw
    hybrid_openclaw = create_openclaw_engine(db)
    return hybrid_openclaw

def register_routes(db, get_current_user, require_admin):
    router = APIRouter(tags=["OpenClaw"])
    engine = create_openclaw_engine(db)
    
    @router.get("/capabilities")
    async def get_capabilities():
        return engine.get_capabilities()
    
    @router.post("/run")
    async def run_task(request: OpenClawRequest):
        return await engine.run_task(request)
    
    return router
