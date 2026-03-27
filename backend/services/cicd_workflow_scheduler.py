"""
CI/CD Workflow Scheduler - Automated Testing & Deployment
Runs autonomous systems on a schedule for continuous improvement
"""
import logging
import asyncio
from datetime import datetime, timezone
from typing import Dict, Any
import os

from services.autonomous_testing_system import autonomous_testing
from services.autonomous_cicd_system import autonomous_cicd
from services.autonomous_development_system import autonomous_dev
from services.slack_notification_service import slack_notifications
from services.github_integration_service import github_integration

logger = logging.getLogger(__name__)

class CICDWorkflowScheduler:
    """
    Automated CI/CD workflow that runs on schedule:
    - Tests every 30 minutes
    - Health checks every 15 minutes
    - Process task queue every hour
    - Send notifications to Slack
    - Create GitHub PRs for completed tasks
    """
    
    def __init__(self):
        self.running = False
        self.test_interval = 1800  # 30 minutes
        self.health_interval = 900  # 15 minutes
        self.task_interval = 3600  # 1 hour
        
        self.last_test_run = None
        self.last_health_check = None
        self.last_task_process = None
        
        # Check if integrations are enabled
        self.slack_enabled = bool(os.getenv('SLACK_WEBHOOK_URL'))
        self.github_enabled = bool(os.getenv('GITHUB_TOKEN'))
        
        logger.info(f"CI/CD Workflow Scheduler initialized")
        logger.info(f"Slack notifications: {'✓ enabled' if self.slack_enabled else '✗ disabled'}")
        logger.info(f"GitHub integration: {'✓ enabled' if self.github_enabled else '✗ disabled'}")
    
    async def start(self):
        """Start the CI/CD workflow scheduler"""
        if self.running:
            logger.warning("CI/CD workflow already running")
            return
        
        self.running = True
        logger.info("🚀 Starting automated CI/CD workflow...")
        
        # Send startup notification
        if self.slack_enabled:
            await slack_notifications.send_notification(
                title="🚀 CI/CD Workflow Started",
                message="Autonomous testing, health monitoring, and task processing are now active.",
                level="INFO"
            )
        
        # Start all workflow loops
        await asyncio.gather(
            self.test_loop(),
            self.health_loop(),
            self.task_loop()
        )
    
    async def stop(self):
        """Stop the CI/CD workflow"""
        self.running = False
        logger.info("Stopping CI/CD workflow...")
        
        if self.slack_enabled:
            await slack_notifications.send_notification(
                title="⏸️ CI/CD Workflow Stopped",
                message="Automated workflows have been paused.",
                level="WARNING"
            )
    
    async def test_loop(self):
        """Automated testing loop - runs every 30 minutes"""
        logger.info(f"📋 Test loop started (interval: {self.test_interval}s)")
        
        while self.running:
            try:
                logger.info("Running automated test suite...")
                self.last_test_run = datetime.now(timezone.utc)
                
                # Run all tests
                results = await autonomous_testing.run_all_tests()
                
                # Notify about results
                status_emoji = "✅" if results["overall_status"] == "passed" else "❌"
                
                if self.slack_enabled:
                    await slack_notifications.send_notification(
                        title=f"{status_emoji} Automated Test Results",
                        message=f"""
**Status:** {results['overall_status']}
**Backend Tests:** {'✓' if results['backend_tests']['passed'] else '✗'}
**Integration Tests:** {'✓' if results['integration_tests']['passed'] else '✗'}
**Performance Tests:** {'✓' if results['performance_tests']['passed'] else '✗'}
**Coverage:** {results.get('coverage', {}).get('percentage', 'N/A')}%
                        """,
                        level="SUCCESS" if results["overall_status"] == "passed" else "ERROR"
                    )
                
                logger.info(f"Test suite completed: {results['overall_status']}")
                
            except Exception as e:
                logger.error(f"Test loop error: {e}")
                if self.slack_enabled:
                    await slack_notifications.send_notification(
                        title="❌ Test Loop Error",
                        message=str(e),
                        level="ERROR"
                    )
            
            # Wait for next run
            await asyncio.sleep(self.test_interval)
    
    async def health_loop(self):
        """Health monitoring loop - runs every 15 minutes"""
        logger.info(f"🏥 Health loop started (interval: {self.health_interval}s)")
        
        while self.running:
            try:
                logger.info("Running health check...")
                self.last_health_check = datetime.now(timezone.utc)
                
                # Run health check
                health = await autonomous_cicd.health_check()
                
                # Alert if unhealthy
                if not health["overall_healthy"]:
                    unhealthy_services = [
                        svc for svc, healthy in health["services"].items()
                        if not healthy
                    ]
                    
                    logger.warning(f"Unhealthy services detected: {unhealthy_services}")
                    
                    if self.slack_enabled:
                        await slack_notifications.send_notification(
                            title="⚠️ Health Check Alert",
                            message=f"Unhealthy services: {', '.join(unhealthy_services)}",
                            level="WARNING"
                        )
                    
                    # Attempt auto-healing
                    logger.info("Attempting auto-heal...")
                    await autonomous_cicd._auto_heal(health)
                else:
                    logger.info("All services healthy ✓")
                
            except Exception as e:
                logger.error(f"Health loop error: {e}")
            
            # Wait for next run
            await asyncio.sleep(self.health_interval)
    
    async def task_loop(self):
        """Task processing loop - runs every hour"""
        logger.info(f"⚙️ Task loop started (interval: {self.task_interval}s)")
        
        while self.running:
            try:
                logger.info("Processing task queue...")
                self.last_task_process = datetime.now(timezone.utc)
                
                # Check if there are tasks in queue
                if len(autonomous_dev.task_queue) > 0:
                    logger.info(f"Found {len(autonomous_dev.task_queue)} tasks in queue")
                    
                    # Process one task at a time
                    task = autonomous_dev.task_queue[0]
                    
                    if self.slack_enabled:
                        await slack_notifications.send_notification(
                            title="🔧 Processing Task",
                            message=f"Starting work on: {task['description']}",
                            level="INFO"
                        )
                    
                    # Auto-complete the task
                    result = await autonomous_dev.auto_complete_task(task['description'])
                    
                    # Notify about completion
                    if result.get("success"):
                        logger.info(f"Task completed successfully: {task['description']}")
                        
                        if self.slack_enabled:
                            await slack_notifications.send_notification(
                                title="✅ Task Completed",
                                message=f"Successfully completed: {task['description']}",
                                level="SUCCESS"
                            )
                        
                        # Create GitHub PR if enabled
                        if self.github_enabled and result.get("code_generated"):
                            logger.info("Creating GitHub PR...")
                            # Would create PR here
                            # (implementation depends on github_integration_service)
                    else:
                        logger.error(f"Task failed: {task['description']}")
                        
                        if self.slack_enabled:
                            await slack_notifications.send_notification(
                                title="❌ Task Failed",
                                message=f"Failed to complete: {task['description']}",
                                level="ERROR"
                            )
                else:
                    logger.debug("No tasks in queue")
                
            except Exception as e:
                logger.error(f"Task loop error: {e}")
            
            # Wait for next run
            await asyncio.sleep(self.task_interval)
    
    def get_status(self) -> Dict[str, Any]:
        """Get scheduler status"""
        return {
            "running": self.running,
            "last_test_run": self.last_test_run.isoformat() if self.last_test_run else None,
            "last_health_check": self.last_health_check.isoformat() if self.last_health_check else None,
            "last_task_process": self.last_task_process.isoformat() if self.last_task_process else None,
            "slack_enabled": self.slack_enabled,
            "github_enabled": self.github_enabled,
            "intervals": {
                "test": f"{self.test_interval}s (30 min)",
                "health": f"{self.health_interval}s (15 min)",
                "task": f"{self.task_interval}s (60 min)"
            }
        }

# Singleton
cicd_scheduler = CICDWorkflowScheduler()
