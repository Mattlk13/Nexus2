"""
Autonomous Systems Router - Central Control for All Autonomous Systems
"""
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, Optional
import logging

from services.autonomous_testing_system import autonomous_testing
from services.slack_notification_service import slack_notifications
from services.github_integration_service import github_integration
from services.llm_finetuning_service import llm_finetuning
from services.posthog_ab_testing_service import posthog_ab_testing

from services.autonomous_cicd_system import autonomous_cicd
from services.autonomous_development_system import autonomous_dev
from services.cicd_workflow_scheduler import cicd_scheduler
from .dependencies import require_admin

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Autonomous Systems"])

# ==================== MODELS ====================

class TaskRequest(BaseModel):
    description: str
    priority: int = 5

class BugFixRequest(BaseModel):
    description: str
    error_log: Optional[str] = None

def get_autonomous_systems_router():
    """Create autonomous systems router"""
    
    # ==================== MASTER CONTROL ====================
    
    @router.get("/autonomous-systems/status")
    async def get_all_systems_status(current_user: dict = Depends(require_admin)):
        """Get status of all autonomous systems"""
        return {
            "testing": autonomous_testing.get_status(),
            "cicd": autonomous_cicd.get_status(),
            "development": autonomous_dev.get_status(),
            "philosophy": "Self-testing, self-deploying, self-improving platform"
        }
    
    @router.post("/autonomous-systems/start-all")
    async def start_all_autonomous_systems(
        background_tasks: BackgroundTasks,
        current_user: dict = Depends(require_admin)
    ):
        """Start all autonomous systems including CI/CD scheduler"""
        background_tasks.add_task(autonomous_testing.run_continuous_testing)
        background_tasks.add_task(autonomous_cicd.continuous_monitoring)
        background_tasks.add_task(autonomous_dev.continuous_development_loop)
        background_tasks.add_task(cicd_scheduler.start)
        
        return {
            "success": True,
            "message": "All autonomous systems and CI/CD scheduler started",
            "systems": ["testing", "cicd", "development", "cicd_scheduler"]
        }
    
    @router.get("/autonomous-systems/scheduler/status")
    async def get_scheduler_status(current_user: dict = Depends(require_admin)):
        """Get CI/CD scheduler status"""
        return cicd_scheduler.get_status()
    
    @router.post("/autonomous-systems/scheduler/start")
    async def start_scheduler(
        background_tasks: BackgroundTasks,
        current_user: dict = Depends(require_admin)
    ):
        """Start CI/CD workflow scheduler"""
        background_tasks.add_task(cicd_scheduler.start)
        return {"success": True, "message": "CI/CD scheduler started"}
    
    @router.post("/autonomous-systems/scheduler/stop")
    async def stop_scheduler(current_user: dict = Depends(require_admin)):
        """Stop CI/CD workflow scheduler"""
        await cicd_scheduler.stop()
        return {"success": True, "message": "CI/CD scheduler stopped"}
    
    # ==================== TESTING SYSTEM ====================
    
    @router.post("/autonomous-systems/testing/run")
    async def run_tests(current_user: dict = Depends(require_admin)):
        """Run all tests immediately"""
        results = await autonomous_testing.run_all_tests()
        return results
    
    @router.get("/autonomous-systems/testing/status")
    async def get_testing_status(current_user: dict = Depends(require_admin)):
        """Get testing system status"""
        return autonomous_testing.get_status()
    
    @router.post("/autonomous-systems/testing/start-continuous")
    async def start_continuous_testing(
        background_tasks: BackgroundTasks,
        current_user: dict = Depends(require_admin)
    ):
        """Start continuous testing loop"""
        background_tasks.add_task(autonomous_testing.run_continuous_testing)
        return {"success": True, "message": "Continuous testing started"}
    
    # ==================== CI/CD SYSTEM ====================
    
    @router.post("/autonomous-systems/cicd/audit")
    async def run_audit(current_user: dict = Depends(require_admin)):
        """Run comprehensive code audit"""
        results = await autonomous_cicd.run_audit()
        return results
    
    @router.post("/autonomous-systems/cicd/optimize")
    async def auto_optimize(current_user: dict = Depends(require_admin)):
        """Auto-apply optimizations"""
        results = await autonomous_cicd.auto_optimize()
        return results
    
    @router.get("/autonomous-systems/cicd/health")
    async def health_check(current_user: dict = Depends(require_admin)):
        """Check platform health"""
        health = await autonomous_cicd.health_check()
        return health
    
    @router.post("/autonomous-systems/cicd/start-monitoring")
    async def start_monitoring(
        background_tasks: BackgroundTasks,
        current_user: dict = Depends(require_admin)
    ):
        """Start continuous health monitoring"""
        background_tasks.add_task(autonomous_cicd.continuous_monitoring)
        return {"success": True, "message": "Continuous monitoring started"}
    
    # ==================== DEVELOPMENT SYSTEM ====================
    
    @router.post("/autonomous-systems/dev/add-task")
    async def add_development_task(
        request: TaskRequest,
        current_user: dict = Depends(require_admin)
    ):
        """Add task to autonomous development queue"""
        autonomous_dev.add_task(request.description, request.priority)
        return {
            "success": True,
            "message": "Task added to queue",
            "queue_size": len(autonomous_dev.task_queue)
        }
    
    @router.post("/autonomous-systems/dev/complete-task")
    async def auto_complete_task(
        request: TaskRequest,
        current_user: dict = Depends(require_admin)
    ):
        """Auto-complete a single task immediately"""
        result = await autonomous_dev.auto_complete_task(request.description)
        return result
    
    @router.post("/autonomous-systems/dev/fix-bug")
    async def auto_fix_bug(
        request: BugFixRequest,
        current_user: dict = Depends(require_admin)
    ):
        """Auto-fix a reported bug"""
        result = await autonomous_dev.auto_fix_bug(
            request.description,
            request.error_log
        )
        return result
    
    @router.post("/autonomous-systems/dev/start-continuous")
    async def start_continuous_development(
        background_tasks: BackgroundTasks,
        current_user: dict = Depends(require_admin)
    ):
        """Start continuous development loop"""
        background_tasks.add_task(autonomous_dev.continuous_development_loop)
        return {"success": True, "message": "Continuous development started"}
    
    @router.get("/autonomous-systems/dev/queue")
    async def get_task_queue(current_user: dict = Depends(require_admin)):
        """Get current task queue"""
        return {
            "queue": autonomous_dev.task_queue,
            "active_task": autonomous_dev.active_task
        }
    
    # ==================== ANALYTICS ====================
    
    @router.get("/autonomous-systems/analytics")
    async def get_analytics(current_user: dict = Depends(require_admin)):
        """Get analytics across all autonomous systems"""
        return {
            "total_tests_run": len(autonomous_testing.test_results),
            "test_pass_rate": sum(1 for t in autonomous_testing.test_results if t.get("overall_status") == "passed") / max(len(autonomous_testing.test_results), 1) * 100,
            "total_deployments": len(autonomous_cicd.deployment_history),
            "health_checks": len(autonomous_cicd.health_checks),
            "current_health": autonomous_cicd.health_checks[-1] if autonomous_cicd.health_checks else None,
            "completed_tasks": len(autonomous_dev.completed_tasks),
            "failed_tasks": len(autonomous_dev.failed_tasks),
            "task_success_rate": len(autonomous_dev.completed_tasks) / max(len(autonomous_dev.completed_tasks) + len(autonomous_dev.failed_tasks), 1) * 100
        }
    
    return router
