"""
Autonomous Integration Engine Router
API endpoints for controlling the self-improving platform
"""
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

from services.autonomous_integration_engine import autonomous_engine
from .dependencies import require_admin

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Autonomous Engine"])

# ==================== MODELS ====================

class DiscoverRequest(BaseModel):
    category: Optional[str] = None
    limit: int = 100

class EvaluateRequest(BaseModel):
    integration_name: str
    source: str
    url: str

class HybridGenerationRequest(BaseModel):
    category: str
    integration_names: List[str]

def get_autonomous_router():
    """Create autonomous engine router"""
    
    # ==================== STATUS & CONTROL ====================
    
    @router.get("/autonomous/status")
    async def get_engine_status(current_user: dict = Depends(require_admin)):
        """Get autonomous engine status"""
        status = autonomous_engine.get_status()
        
        return {
            **status,
            "description": "Autonomous Integration Engine - Continuously discovers and integrates new technologies"
        }
    
    @router.post("/autonomous/start-loop")
    async def start_continuous_loop(
        background_tasks: BackgroundTasks,
        current_user: dict = Depends(require_admin)
    ):
        """Start the continuous improvement loop"""
        # Run in background
        background_tasks.add_task(autonomous_engine.continuous_improvement_loop)
        
        return {
            "success": True,
            "message": "Autonomous improvement loop started",
            "note": "Engine will discover and evaluate integrations every hour"
        }
    
    @router.post("/autonomous/stop-loop")
    async def stop_continuous_loop(current_user: dict = Depends(require_admin)):
        """Stop the continuous improvement loop"""
        # Would need to implement stop mechanism
        return {
            "success": True,
            "message": "Loop stop requested (implement stop mechanism in production)"
        }
    
    # ==================== DISCOVERY ====================
    
    @router.post("/autonomous/discover")
    async def discover_integrations(
        request: DiscoverRequest,
        current_user: dict = Depends(require_admin)
    ):
        """
        Manually trigger discovery of new integrations.
        
        Searches GitHub, PyPI, NPM, Product Hunt, etc. for potential integrations.
        """
        discovered = await autonomous_engine.discover_integrations(
            category=request.category
        )
        
        # Limit results
        limited = discovered[:request.limit]
        
        return {
            "success": True,
            "discovered_count": len(limited),
            "total_found": len(discovered),
            "integrations": limited,
            "sources": ["GitHub", "PyPI", "NPM", "Product Hunt", "Hacker News", "Reddit"]
        }
    
    # ==================== EVALUATION ====================
    
    @router.post("/autonomous/evaluate")
    async def evaluate_integration(
        request: EvaluateRequest,
        current_user: dict = Depends(require_admin)
    ):
        """
        Evaluate an integration for quality and compatibility.
        
        Returns scores for:
        - Code quality
        - Security
        - Performance
        - Compatibility with NEXUS
        """
        integration = {
            "name": request.integration_name,
            "source": request.source,
            "url": request.url
        }
        
        evaluation = await autonomous_engine.evaluate_integration(integration)
        
        return {
            "success": True,
            "evaluation": evaluation
        }
    
    # ==================== HYBRID GENERATION ====================
    
    @router.post("/autonomous/generate-hybrid")
    async def generate_hybrid_integration(
        request: HybridGenerationRequest,
        current_user: dict = Depends(require_admin)
    ):
        """
        Generate a hybrid integration combining multiple tools.
        
        Example: Combine Stripe + BTCPay + Aurpay → OmniPay
        """
        # Mock integrations for demo
        integrations = [
            {"name": name, "category": request.category}
            for name in request.integration_names
        ]
        
        hybrid = await autonomous_engine.generate_hybrid_integration(
            integrations,
            request.category
        )
        
        return {
            "success": True,
            "hybrid": hybrid,
            "note": "Review generated code before deploying"
        }
    
    # ==================== QUEUE MANAGEMENT ====================
    
    @router.get("/autonomous/queue")
    async def get_integration_queue(current_user: dict = Depends(require_admin)):
        """Get queue of integrations pending implementation"""
        return {
            "queue": autonomous_engine.integration_queue,
            "count": len(autonomous_engine.integration_queue)
        }
    
    @router.delete("/autonomous/queue/{index}")
    async def remove_from_queue(
        index: int,
        current_user: dict = Depends(require_admin)
    ):
        """Remove integration from queue"""
        if 0 <= index < len(autonomous_engine.integration_queue):
            removed = autonomous_engine.integration_queue.pop(index)
            return {
                "success": True,
                "removed": removed
            }
        
        raise HTTPException(status_code=404, detail="Queue index not found")
    
    # ==================== AUTO-UPDATE ====================
    
    @router.post("/autonomous/auto-update/{integration_name}")
    async def trigger_auto_update(
        integration_name: str,
        current_user: dict = Depends(require_admin)
    ):
        """
        Manually trigger auto-update for an integration.
        
        Checks for updates, tests, and deploys if safe.
        """
        success = await autonomous_engine.auto_update_integration(integration_name)
        
        return {
            "success": success,
            "integration": integration_name,
            "message": "Update completed" if success else "Update failed or no update available"
        }
    
    @router.post("/autonomous/auto-update-all")
    async def trigger_auto_update_all(
        background_tasks: BackgroundTasks,
        current_user: dict = Depends(require_admin)
    ):
        """Trigger auto-update for all integrations"""
        async def update_all():
            for integration_name in autonomous_engine.current_integrations.keys():
                await autonomous_engine.auto_update_integration(integration_name)
        
        background_tasks.add_task(update_all)
        
        return {
            "success": True,
            "message": f"Auto-update started for {len(autonomous_engine.current_integrations)} integrations",
            "integrations": list(autonomous_engine.current_integrations.keys())
        }
    
    # ==================== CURRENT INTEGRATIONS ====================
    
    @router.get("/autonomous/integrations")
    async def get_current_integrations(current_user: dict = Depends(require_admin)):
        """Get all current NEXUS integrations"""
        return {
            "integrations": autonomous_engine.current_integrations,
            "count": len(autonomous_engine.current_integrations)
        }
    
    @router.get("/autonomous/integrations/{name}")
    async def get_integration_details(
        name: str,
        current_user: dict = Depends(require_admin)
    ):
        """Get details about a specific integration"""
        if name in autonomous_engine.current_integrations:
            return {
                "integration": autonomous_engine.current_integrations[name]
            }
        
        raise HTTPException(status_code=404, detail="Integration not found")
    
    return router
