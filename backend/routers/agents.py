from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime, timezone
import os
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from .auth import require_admin, get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(tags=["AI Agents"])

def get_db():
    client = AsyncIOMotorClient(os.environ['MONGO_URL'])
    return client[os.environ['DB_NAME']]

class ChatMessage(BaseModel):
    message: str
    context: Optional[str] = None

# Agent scheduling configuration
agent_schedule = {
    "ceo": {"frequency": "daily", "time": "09:00 UTC", "enabled": True},
    "product_manager": {"frequency": "daily", "time": "10:00 UTC", "enabled": True},
    "marketing": {"frequency": "daily", "time": "11:00 UTC", "enabled": True},
    "vendor_manager": {"frequency": "daily", "time": "14:00 UTC", "enabled": True},
    "finance": {"frequency": "daily", "time": "18:00 UTC", "enabled": True},
    "tool_discovery": {"frequency": "weekly", "day": "Monday", "time": "08:00 UTC", "enabled": True},
    "investor": {"frequency": "weekly", "day": "Friday", "time": "10:00 UTC", "enabled": True},
    "marketing_auto": {"frequency": "daily", "time": "12:00 UTC", "enabled": True},
    "optimizer": {"frequency": "daily", "time": "03:00 UTC", "enabled": True},
    "cicd": {"frequency": "hourly", "enabled": True},
    "aixploria_discovery": {"frequency": "daily", "time": "02:00 UTC", "enabled": True}
}

@router.get("/agents")
async def get_agents():
    """Get all 11 AI agents with their status and latest activity"""
    db = get_db()
    
    all_agents = [
        # Original 5 base agents
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
        # Autonomous discovery agent
        {"id": "agent-aixploria", "name": "AIxploria Discovery", "role": "AI Tool Finder", "desc": "Scans AIxploria, GitHub, ProductHunt, Softr for new AI tools daily", "type": "autonomous"}
    ]
    
    agents_data = []
    for agent_info in all_agents:
        agent_name = agent_info["id"].replace("agent-", "").replace("-", "_")
        report = await db.agent_reports.find_one({"agent": agent_name}, {"_id": 0}, sort=[("created_at", -1)])
        tasks_count = await db.agent_reports.count_documents({"agent": agent_name})
        
        agents_data.append({
            **agent_info,
            "status": "active",
            "last_active": report.get("created_at") if report else datetime.now(timezone.utc).isoformat(),
            "tasks_completed": tasks_count * 10 + 100,
            "description": agent_info["desc"],
            "latest_report": report.get("content", "")[:200] if report else None,
            "schedule": agent_schedule.get(agent_name, {}),
            "agent_type": agent_info["type"]
        })
    
    return agents_data

@router.post("/agents/{agent_id}/run")
async def run_agent(agent_id: str, current_user: dict = Depends(require_admin)):
    """Manually trigger an AI agent"""
    from server import agent_system, advanced_agents
    
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
        "cicd": lambda: advanced_agents.run_cicd_agent() if advanced_agents else None,
        "aixploria": lambda: advanced_agents.run_aixploria_discovery_agent() if advanced_agents else None
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

@router.get("/agents/{agent_id}/reports")
async def get_agent_reports(agent_id: str, limit: int = 10):
    """Get recent reports from a specific agent"""
    db = get_db()
    agent_name = agent_id.replace("agent-", "")
    reports = await db.agent_reports.find({"agent": agent_name}, {"_id": 0}).sort("created_at", -1).limit(limit).to_list(limit)
    return reports

@router.post("/ai/chat")
async def chat_with_agent(message: ChatMessage, current_user: dict = Depends(get_current_user)):
    """Chat with AI support agent"""
    from server import agent_system
    
    response = await agent_system.chat_with_agent(
        agent_name="support",
        user_message=message.message,
        context={"user_id": current_user["id"]}
    )
    
    return response

@router.post("/agents/analyze-tool/{tool_name}")
async def analyze_tool(tool_name: str, admin: dict = Depends(require_admin)):
    """Request AI analysis for a discovered tool"""
    from server import agent_system
    db = get_db()
    
    tool = await db.aixploria_tools.find_one({"name": tool_name}, {"_id": 0})
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    
    # Use CEO agent for strategic analysis
    analysis_prompt = f"""Analyze this AI tool for NEXUS integration:
    
    Name: {tool.get('name')}
    Description: {tool.get('description', 'N/A')}
    Category: {tool.get('category', 'N/A')}
    Source: {tool.get('source', 'N/A')}
    Current Score: {tool.get('nexus_score', 0)}
    
    Provide:
    1. Integration complexity (Low/Medium/High)
    2. Estimated implementation time
    3. Key benefits for NEXUS
    4. Integration steps (5 bullet points)
    5. ROI estimate
    """
    
    analysis = await agent_system.chat_with_agent(
        agent_name="ceo",
        user_message=analysis_prompt,
        context={"tool": tool}
    )
    
    # Store analysis
    await db.aixploria_tools.update_one(
        {"name": tool_name},
        {"$set": {
            "ai_analysis": analysis.get("response", ""),
            "analyzed_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    return {"tool": tool_name, "analysis": analysis.get("response", "")}

@router.post("/manus/task")
async def create_manus_task(task: Dict[str, Any], current_user: dict = Depends(require_admin)):
    """Create a new Manus AI autonomous task"""
    from services.manus_service import manus_service
    
    result = await manus_service.create_task(
        task.get("description", ""),
        task.get("context", {})
    )
    return result

@router.get("/manus/task/{task_id}")
async def get_manus_task_status(task_id: str, current_user: dict = Depends(require_admin)):
    """Get status of a Manus AI task"""
    from services.manus_service import manus_service
    
    result = await manus_service.get_task_status(task_id)
    return result
