# DigitalOcean ADK API Routes for NEXUS

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from services.digitalocean_adk_service import adk_service

router = APIRouter(prefix="/api/adk", tags=["DigitalOcean ADK"])

# Request Models
class CreateAgentRequest(BaseModel):
    agent_name: str
    deployment_name: str = "development"
    description: str = ""
    model: str = "openai-gpt-oss-120b"

class TestAgentRequest(BaseModel):
    agent_name: str
    prompt: str

class DeployAgentRequest(BaseModel):
    agent_name: str
    deployment_name: str = "development"

class CallAgentRequest(BaseModel):
    deployment_url: str
    prompt: str

# Routes

@router.get("/status")
async def get_adk_status():
    """Get ADK integration status"""
    return {
        "adk_available": adk_service.adk_available,
        "workspace_root": str(adk_service.workspace_root),
        "gradient_key_configured": bool(adk_service.gradient_model_key),
        "do_token_configured": bool(adk_service.do_api_token),
        "status": "operational" if adk_service.adk_available else "adk_not_installed"
    }

@router.post("/agents/create")
async def create_agent(request: CreateAgentRequest):
    """Create a new AI agent"""
    result = await adk_service.create_agent(
        agent_name=request.agent_name,
        deployment_name=request.deployment_name,
        description=request.description,
        model=request.model
    )
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    
    return result

@router.get("/agents")
async def list_agents():
    """List all agents"""
    agents = adk_service.list_agents()
    return {
        "agents": agents,
        "count": len(agents)
    }

@router.get("/agents/{agent_name}")
async def get_agent(agent_name: str):
    """Get agent details"""
    agent = adk_service.get_agent(agent_name)
    
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_name}' not found")
    
    return {"agent": agent}

@router.post("/agents/test")
async def test_agent(request: TestAgentRequest):
    """Test agent locally"""
    result = await adk_service.test_agent_local(
        agent_name=request.agent_name,
        prompt=request.prompt
    )
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    
    return result

@router.post("/agents/deploy")
async def deploy_agent(request: DeployAgentRequest):
    """Deploy agent to DigitalOcean"""
    result = await adk_service.deploy_agent(
        agent_name=request.agent_name,
        deployment_name=request.deployment_name
    )
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    
    return result

@router.post("/agents/call")
async def call_agent(request: CallAgentRequest):
    """Call a deployed agent"""
    result = await adk_service.call_deployed_agent(
        deployment_url=request.deployment_url,
        prompt=request.prompt
    )
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    
    return result

@router.delete("/agents/{agent_name}")
async def delete_agent(agent_name: str):
    """Delete an agent"""
    result = await adk_service.delete_agent(agent_name)
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    
    return result

@router.get("/agents/{agent_name}/logs")
async def get_agent_logs(agent_name: str):
    """Get agent logs"""
    result = adk_service.get_agent_logs(agent_name)
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    
    return result

@router.get("/models")
async def list_available_models():
    """List available models for agents"""
    return {
        "models": [
            {
                "id": "openai-gpt-oss-120b",
                "name": "GPT OSS 120B",
                "provider": "OpenAI",
                "type": "text-generation"
            },
            {
                "id": "meta-llama-3.1-405b-instruct",
                "name": "Llama 3.1 405B",
                "provider": "Meta",
                "type": "text-generation"
            },
            {
                "id": "anthropic-claude-3.5-sonnet",
                "name": "Claude 3.5 Sonnet",
                "provider": "Anthropic",
                "type": "text-generation"
            }
        ]
    }

# Register routes
def register_routes(app):
    """Register ADK routes with main app"""
    app.include_router(router)
