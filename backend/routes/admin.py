"""
Admin routes - Analytics, agents, management
"""
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Dict, Any, List
from datetime import datetime, timezone
import uuid
import logging

from .dependencies import require_admin

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Admin"])

class TaskCreate(BaseModel):
    title: str
    description: str
    priority: str = "medium"

def get_admin_router(
    db: AsyncIOMotorDatabase,
    agent_system,
    automation_service,
    manus_service,
    openclaw_service,
    integration_status_service,
    fal_ai_service,
    analytics_service,
    cloudflare_service,
    redis_service
):
    """Create admin router with dependencies"""
    
    # ==================== AI AGENTS ====================
    
    @router.get("/agents")
    async def get_agents():
        """Get all AI agents"""
        agents = await agent_system.get_agents()
        return agents
    
    @router.post("/agents/{agent_id}/run")
    async def run_agent(agent_id: str, current_user: dict = Depends(require_admin)):
        """Run a specific agent manually"""
        try:
            result = await agent_system.run_agent(agent_id)
            return {
                "success": True,
                "agent_id": agent_id,
                "result": result
            }
        except Exception as e:
            logger.error(f"Agent run failed: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/agents/{agent_id}/reports")
    async def get_agent_reports(agent_id: str, limit: int = 10):
        """Get agent execution reports"""
        reports = await db.agent_reports.find(
            {"agent_id": agent_id},
            {"_id": 0}
        ).sort("created_at", -1).limit(limit).to_list(limit)
        return reports
    
    # ==================== AUTOMATION & DISCOVERY ====================
    
    @router.post("/automation/discover-tools")
    async def trigger_tool_discovery(categories: List[str], current_user: dict = Depends(require_admin)):
        """Trigger tool discovery"""
        try:
            result = await automation_service.discover_tools(categories)
            return result
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.post("/automation/integrate-tool")
    async def integrate_discovered_tool(
        tool_data: Dict[str, Any],
        background_tasks: BackgroundTasks,
        current_user: dict = Depends(require_admin)
    ):
        """Integrate a discovered tool"""
        background_tasks.add_task(automation_service.integrate_tool, tool_data)
        return {"status": "integration_started", "tool": tool_data.get("name")}
    
    # ==================== MANUS AI TASKS ====================
    
    @router.post("/manus/task")
    async def create_manus_task(task: Dict[str, Any], current_user: dict = Depends(require_admin)):
        """Create Manus AI task"""
        try:
            result = await manus_service.create_task(
                title=task.get("title"),
                description=task.get("description"),
                context=task.get("context", {})
            )
            return result
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/manus/task/{task_id}")
    async def get_manus_task_status(task_id: str, current_user: dict = Depends(require_admin)):
        """Get Manus task status"""
        try:
            status = await manus_service.get_task_status(task_id)
            return status
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    # ==================== OPENCLAW ====================
    
    @router.get("/openclaw/status")
    async def get_openclaw_status():
        """Get OpenClaw status"""
        return openclaw_service.get_status()
    
    @router.get("/openclaw/analysis")
    async def get_openclaw_analysis():
        """Get OpenClaw platform analysis"""
        return openclaw_service.get_quick_analysis()
    
    # ==================== INTEGRATIONS STATUS ====================
    
    @router.get("/integrations/status")
    async def get_integrations_status():
        """Get all integrations status"""
        return await integration_status_service.get_all_status()
    
    @router.get("/integrations/health")
    async def get_integrations_health():
        """Get integrations health"""
        return await integration_status_service.health_check()
    
    # ==================== FAL.AI TEST ====================
    
    @router.get("/integrations/fal/test")
    async def test_fal_integration():
        """Test Fal.ai integration"""
        try:
            result = await fal_ai_service.test_connection()
            return result
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    # ==================== ANALYTICS ====================
    
    @router.get("/analytics/dashboard")
    async def get_admin_analytics(current_user: dict = Depends(require_admin)):
        """Get admin analytics dashboard"""
        try:
            total_users = await db.users.count_documents({})
            total_products = await db.products.count_documents({})
            total_purchases = await db.purchases.count_documents({})
            total_posts = await db.posts.count_documents({})
            
            recent_users = await db.users.find(
                {},
                {"_id": 0, "password": 0}
            ).sort("created_at", -1).limit(10).to_list(10)
            
            revenue = await db.purchases.aggregate([
                {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
            ]).to_list(1)
            
            total_revenue = revenue[0]["total"] if revenue else 0
            
            return {
                "total_users": total_users,
                "total_products": total_products,
                "total_purchases": total_purchases,
                "total_posts": total_posts,
                "total_revenue": total_revenue,
                "recent_users": recent_users
            }
        except Exception as e:
            logger.error(f"Analytics failed: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/analytics/detailed")
    async def get_detailed_analytics(current_user: dict = Depends(require_admin)):
        """Get detailed analytics"""
        try:
            return await analytics_service.get_detailed_analytics()
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    # ==================== CACHE MANAGEMENT ====================
    
    @router.post("/cache/clear")
    async def clear_cache(pattern: str = "*", current_user: dict = Depends(require_admin)):
        """Clear Redis cache"""
        try:
            result = await redis_service.clear_cache(pattern)
            return {"success": True, "cleared": result}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/cache/stats")
    async def get_cache_stats(current_user: dict = Depends(require_admin)):
        """Get cache statistics"""
        try:
            stats = await redis_service.get_stats()
            return stats
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    # ==================== CLOUDFLARE ====================
    
    @router.get("/cloudflare/status")
    async def get_cloudflare_status(current_user: dict = Depends(require_admin)):
        """Get Cloudflare integration status"""
        return await cloudflare_service.get_status()
    
    @router.post("/cloudflare/kv/set")
    async def set_cloudflare_kv(
        data: Dict[str, Any],
        current_user: dict = Depends(require_admin)
    ):
        """Set Cloudflare KV value"""
        try:
            result = await cloudflare_service.kv_put(
                namespace_id=data.get("namespace_id"),
                key=data.get("key"),
                value=data.get("value")
            )
            return {"success": result}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    return router
