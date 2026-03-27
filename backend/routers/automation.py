from fastapi import APIRouter, Depends, BackgroundTasks, Query
from typing import Optional, Dict, Any
import logging
from datetime import datetime, timezone
from services.automation_service import automation_service
from services.aixploria_service import aixploria_service
from services.cicd_service import cicd_service
from .auth import require_admin
import os
from motor.motor_asyncio import AsyncIOMotorClient

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Automation"])

def get_db():
    client = AsyncIOMotorClient(os.environ['MONGO_URL'])
    return client[os.environ['DB_NAME']]

@router.post("/automation/discover-tools")
async def discover_tools_endpoint(background_tasks: BackgroundTasks, admin: dict = Depends(require_admin)):
    """Trigger AI tool discovery"""
    background_tasks.add_task(automation_service.auto_discover_tools)
    return {"status": "discovery_started", "message": "Tool discovery running in background"}

@router.get("/automation/discovered-tools")
async def get_discovered_tools(admin: dict = Depends(require_admin)):
    db = get_db()
    tools = await db.discovered_tools.find({}, {"_id": 0}).sort("discovered_at", -1).limit(100).to_list(100)
    return {"tools": tools, "count": len(tools)}

@router.post("/admin/aixploria/scan")
async def trigger_aixploria_scan(
    background_tasks: BackgroundTasks,
    comprehensive: Optional[bool] = Query(False, description="Include all 50+ categories (slower)"),
    admin: dict = Depends(require_admin)
):
    """Trigger AIxploria multi-source discovery scan"""
    
    async def run_scan():
        try:
            db = get_db()
            result = await aixploria_service.discover_and_evaluate(include_all_categories=comprehensive)
            
            # Store all discovered tools
            if result["total_tools_discovered"] > 0:
                tools_to_store = (
                    result["critical_integrations"] +
                    result["high_priority"] +
                    result["medium_priority"]
                )
                
                for tool in tools_to_store:
                    await db.aixploria_tools.update_one(
                        {"name": tool["name"]},
                        {"$set": tool},
                        upsert=True
                    )
                
                logger.info(f"✓ Stored {len(tools_to_store)} tools in database")
        except Exception as e:
            logger.error(f"Scan error: {e}")
    
    background_tasks.add_task(run_scan)
    
    return {
        "status": "scan_started",
        "scan_mode": "comprehensive" if comprehensive else "standard",
        "message": "Discovery scan running in background. Check stats in 30-60 seconds."
    }

@router.get("/admin/aixploria/tools")
async def get_aixploria_tools(
    benefit_level: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    source: Optional[str] = Query(None),
    limit: int = Query(100, le=500),
    admin: dict = Depends(require_admin)
):
    """Get discovered AI tools with filtering"""
    db = get_db()
    
    query = {}
    if benefit_level:
        query["benefit_level"] = benefit_level
    if source:
        query["source"] = source
    if category:
        query["nexus_categories"] = category
    
    tools = await db.aixploria_tools.find(query, {"_id": 0}).sort("nexus_score", -1).limit(limit).to_list(limit)
    
    return {
        "tools": tools,
        "count": len(tools),
        "filters_applied": query
    }

@router.get("/admin/aixploria/stats")
async def get_aixploria_stats(admin: dict = Depends(require_admin)):
    """Get AIxploria discovery statistics"""
    db = get_db()
    
    total_scans = await db.aixploria_scans.count_documents({})
    total_tools = await db.aixploria_tools.count_documents({})
    critical_tools = await db.aixploria_tools.count_documents({"benefit_level": "critical"})
    high_tools = await db.aixploria_tools.count_documents({"benefit_level": "high"})
    
    recent_scans = await db.aixploria_scans.find(
        {}, {"_id": 0}
    ).sort("scan_timestamp", -1).limit(5).to_list(5)
    
    return {
        "total_scans": total_scans,
        "total_tools_discovered": total_tools,
        "critical_integrations": critical_tools,
        "high_priority_tools": high_tools,
        "recent_scans": recent_scans
    }

@router.get("/admin/performance")
async def get_performance_metrics(admin: dict = Depends(require_admin)):
    """Get database and system performance metrics"""
    db = get_db()
    
    collections = ["users", "products", "posts", "notifications", "aixploria_tools", "agent_reports"]
    metrics = {}
    
    for collection_name in collections:
        collection = db[collection_name]
        count = await collection.count_documents({})
        metrics[collection_name] = {"document_count": count}
    
    return {"collections": metrics, "timestamp": datetime.now(timezone.utc).isoformat()}

@router.get("/admin/aixploria/latest-scan")
async def get_latest_scan(admin: dict = Depends(require_admin)):
    """Get most recent AIxploria scan results"""
    db = get_db()
    
    latest = await db.aixploria_scans.find_one(
        {},
        {"_id": 0},
        sort=[("scan_timestamp", -1)]
    )
    
    if not latest:
        return {"message": "No scans found", "scans_count": 0}
    
    return latest

@router.get("/cicd/status")
async def get_cicd_status(admin: dict = Depends(require_admin)):
    """Get CI/CD integration status"""
    status = await cicd_service.get_integration_status()
    return status

@router.post("/cicd/deploy")
async def trigger_deployment(environment: str = "production", admin: dict = Depends(require_admin)):
    """Trigger deployment"""
    result = await cicd_service.trigger_deployment(environment)
    return result

@router.post("/cicd/test")
async def run_tests(admin: dict = Depends(require_admin)):
    """Run automated tests"""
    result = await cicd_service.run_automated_tests()
    return result

@router.get("/cicd/repositories")
async def search_repositories(query: str = "ai tools", limit: int = 20, admin: dict = Depends(require_admin)):
    """Search GitHub repositories for AI tools"""
    repos = await cicd_service.search_ai_repositories(query, limit)
    return {"repositories": repos, "count": len(repos)}

@router.get("/integrations/status")
async def get_integration_status(admin: dict = Depends(require_admin)):
    """Get comprehensive status of all NEXUS integrations"""
    from services.integration_status import integration_status_service
    return integration_status_service.get_all_integrations_status()

@router.get("/integrations/health")
async def get_integration_health():
    """Get overall integration health (public endpoint)"""
    from services.integration_status import integration_status_service
    return {"health": integration_status_service.get_integration_health()}
