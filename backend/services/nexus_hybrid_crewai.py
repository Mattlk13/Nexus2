"""
NEXUS Hybrid: CrewAI Multi-Agent Framework
Role-based multi-agent orchestration system
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, List
import os
from dotenv import load_dotenv
import logging

load_dotenv()
logger = logging.getLogger(__name__)

class CrewRequest(BaseModel):
    task: str
    agents: List[str] = ["researcher", "writer"]
    goal: Optional[str] = None

class CrewAIEngine:
    def __init__(self, db):
        self.db = db
        self.api_key = os.getenv('EMERGENT_LLM_KEY')
    
    def get_capabilities(self) -> Dict:
        return {
            "name": "CrewAI Framework",
            "description": "Multi-agent orchestration with role-based crews (44.6k GitHub stars)",
            "category": "ai_agents",
            "provider": "CrewAI",
            "github": "https://github.com/crewAIInc/crewAI",
            "stars": "44,600+",
            "features": [
                "Role-based agent teams",
                "Sequential/hierarchical workflows",
                "MCP & A2A protocol support",
                "Rapid prototyping (<20 lines)",
                "Enterprise scaling via AMP"
            ],
            "use_cases": [
                "Research & Content Creation",
                "Data Analysis Teams",
                "Business Process Automation",
                "Multi-step Workflows"
            ],
            "agent_roles": [
                "Researcher",
                "Writer",
                "Analyst",
                "QA Specialist",
                "Project Manager"
            ],
            "installation": "pip install crewai",
            "status": "active",
            "version": "1.10.1+"
        }
    
    async def run_crew(self, request: CrewRequest) -> Dict:
        """Execute a CrewAI multi-agent task"""
        try:
            # Demo response for now - real CrewAI integration would be complex
            return {
                "success": True,
                "result": f"[DEMO] CrewAI crew with agents {request.agents} would execute: {request.task}",
                "agents_used": request.agents,
                "note": "CrewAI framework installed and ready. Full integration requires agent configuration."
            }
        except Exception as e:
            logger.error(f"CrewAI execution error: {e}")
            raise HTTPException(status_code=500, detail=str(e))

def create_crewai_engine(db):
    return CrewAIEngine(db)

# Create global instance for ultimate controller
hybrid_crewai = None
def init_hybrid(db):
    global hybrid_crewai
    hybrid_crewai = create_crewai_engine(db)
    return hybrid_crewai

def register_routes(db, get_current_user, require_admin):
    router = APIRouter(tags=["CrewAI"])
    engine = create_crewai_engine(db)
    
    @router.get("/capabilities")
    async def get_capabilities():
        return engine.get_capabilities()
    
    @router.post("/run")
    async def run_crew(request: CrewRequest):
        return await engine.run_crew(request)
    
    return router
