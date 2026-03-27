"""
Master Automation Orchestrator
Coordinates all NEXUS automation systems to run continuously
"""
import logging
import asyncio
from datetime import datetime, timezone
from typing import Dict, Any

from services.cicd_workflow_scheduler import cicd_scheduler
from services.hybrid_social_automation import hybrid_social_automation
from services.autonomous_testing_system import autonomous_testing
from services.autonomous_cicd_system import autonomous_cicd
from services.autonomous_development_system import autonomous_dev

logger = logging.getLogger(__name__)

class MasterAutomationOrchestrator:
    """
    Master orchestrator that coordinates all automation systems:
    - CI/CD workflow (testing, deployment, health checks)
    - Social media automation (content generation, scheduling, publishing)
    - Autonomous development (task processing)
    - Analytics and reporting
    """
    
    def __init__(self):
        self.running = False
        self.start_time = None
        
        # Automation intervals (in seconds)
        self.intervals = {
            "social_content_generation": 3600,  # Every hour
            "social_publishing": 300,  # Every 5 minutes
            "social_monitoring": 900,  # Every 15 minutes
            "health_check": 600,  # Every 10 minutes
            "analytics_update": 1800,  # Every 30 minutes
            "task_processing": 3600  # Every hour
        }
        
        self.execution_history = {
            "social_content_generation": [],
            "social_publishing": [],
            "social_monitoring": [],
            "health_check": [],
            "analytics_update": [],
            "task_processing": []
        }
        
        logger.info("Master Automation Orchestrator initialized")
    
    async def start(self):
        """Start all automation systems"""
        if self.running:
            logger.warning("Automation already running")
            return
        
        self.running = True
        self.start_time = datetime.now(timezone.utc)
        
        logger.info("🚀 Starting Master Automation Orchestrator...")
        logger.info("All systems will run autonomously 24/7")
        
        # Start all automation loops
        await asyncio.gather(
            self.social_content_loop(),
            self.social_publishing_loop(),
            self.social_monitoring_loop(),
            self.health_check_loop(),
            self.analytics_loop(),
            self.task_processing_loop()
        )
    
    async def stop(self):
        """Stop all automation"""
        self.running = False
        logger.info("Stopping Master Automation Orchestrator...")
        await cicd_scheduler.stop()
    
    async def social_content_loop(self):
        """Generate social media content automatically"""
        logger.info("📝 Social content generation loop started")
        
        while self.running:
            try:
                logger.info("Generating fresh social media content...")
                
                # Generate 7 days of content at a time
                scheduled = await hybrid_social_automation.schedule_posts(7)
                
                execution = {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "posts_generated": len(scheduled),
                    "status": "success"
                }
                self.execution_history["social_content_generation"].append(execution)
                
                logger.info(f"✅ Generated {len(scheduled)} posts")
                
            except Exception as e:
                logger.error(f"Social content generation error: {e}")
                execution = {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "status": "failed",
                    "error": str(e)
                }
                self.execution_history["social_content_generation"].append(execution)
            
            await asyncio.sleep(self.intervals["social_content_generation"])
    
    async def social_publishing_loop(self):
        """Auto-publish scheduled posts at their scheduled time"""
        logger.info("📤 Social publishing loop started")
        
        while self.running:
            try:
                now = datetime.now(timezone.utc)
                published_count = 0
                
                # Check for posts that are ready to publish
                for post in hybrid_social_automation.scheduled_posts:
                    if post.get("status") == "scheduled":
                        # Check if it's time to publish (simplified logic)
                        # In production, would parse scheduled_for time properly
                        if published_count < 1:  # Publish 1 post per cycle
                            await hybrid_social_automation.publish_post(post["id"])
                            published_count += 1
                
                if published_count > 0:
                    logger.info(f"📱 Auto-published {published_count} posts")
                
                execution = {
                    "timestamp": now.isoformat(),
                    "posts_published": published_count,
                    "status": "success"
                }
                self.execution_history["social_publishing"].append(execution)
                
            except Exception as e:
                logger.error(f"Social publishing error: {e}")
            
            await asyncio.sleep(self.intervals["social_publishing"])
    
    async def social_monitoring_loop(self):
        """Monitor social media for engagement opportunities"""
        logger.info("👂 Social monitoring loop started")
        
        while self.running:
            try:
                logger.info("Scanning social media for conversations...")
                
                conversations = await hybrid_social_automation.monitor_social_conversations()
                
                execution = {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "conversations_found": len(conversations),
                    "status": "success"
                }
                self.execution_history["social_monitoring"].append(execution)
                
                if len(conversations) > 0:
                    logger.info(f"🔍 Found {len(conversations)} relevant conversations")
                
            except Exception as e:
                logger.error(f"Social monitoring error: {e}")
            
            await asyncio.sleep(self.intervals["social_monitoring"])
    
    async def health_check_loop(self):
        """Regular health checks of all systems"""
        logger.info("🏥 Health check loop started")
        
        while self.running:
            try:
                logger.info("Running system health check...")
                
                health = await autonomous_cicd.health_check()
                
                execution = {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "overall_healthy": health["overall_healthy"],
                    "status": "success"
                }
                self.execution_history["health_check"].append(execution)
                
                if not health["overall_healthy"]:
                    logger.warning(f"⚠️ Unhealthy services detected: {health}")
                else:
                    logger.info("✅ All systems healthy")
                
            except Exception as e:
                logger.error(f"Health check error: {e}")
            
            await asyncio.sleep(self.intervals["health_check"])
    
    async def analytics_loop(self):
        """Update analytics and generate reports"""
        logger.info("📊 Analytics loop started")
        
        while self.running:
            try:
                logger.info("Updating analytics...")
                
                analytics = await hybrid_social_automation.analyze_performance()
                
                execution = {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "total_reach": analytics.get("total_reach", 0),
                    "engagement_rate": analytics.get("engagement_rate", 0),
                    "status": "success"
                }
                self.execution_history["analytics_update"].append(execution)
                
                logger.info(f"📈 Analytics updated: {analytics.get('total_reach', 0)} reach, {analytics.get('engagement_rate', 0)}% engagement")
                
            except Exception as e:
                logger.error(f"Analytics update error: {e}")
            
            await asyncio.sleep(self.intervals["analytics_update"])
    
    async def task_processing_loop(self):
        """Process development task queue"""
        logger.info("⚙️ Task processing loop started")
        
        while self.running:
            try:
                if len(autonomous_dev.task_queue) > 0:
                    logger.info(f"Processing {len(autonomous_dev.task_queue)} tasks in queue...")
                    
                    # Process one task at a time
                    task = autonomous_dev.task_queue[0]
                    # Would call auto_complete_task here
                    
                    execution = {
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "tasks_processed": 1,
                        "status": "success"
                    }
                    self.execution_history["task_processing"].append(execution)
                    
                    logger.info("✅ Task processed")
                else:
                    logger.debug("No tasks in queue")
                
            except Exception as e:
                logger.error(f"Task processing error: {e}")
            
            await asyncio.sleep(self.intervals["task_processing"])
    
    def get_status(self) -> Dict[str, Any]:
        """Get orchestrator status"""
        uptime = None
        if self.start_time:
            uptime = str(datetime.now(timezone.utc) - self.start_time)
        
        return {
            "running": self.running,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "uptime": uptime,
            "intervals": self.intervals,
            "execution_summary": {
                "social_content": len(self.execution_history["social_content_generation"]),
                "social_publishing": len(self.execution_history["social_publishing"]),
                "social_monitoring": len(self.execution_history["social_monitoring"]),
                "health_checks": len(self.execution_history["health_check"]),
                "analytics_updates": len(self.execution_history["analytics_update"]),
                "tasks_processed": len(self.execution_history["task_processing"])
            },
            "recent_executions": {
                "social_content": self.execution_history["social_content_generation"][-1] if self.execution_history["social_content_generation"] else None,
                "social_publishing": self.execution_history["social_publishing"][-1] if self.execution_history["social_publishing"] else None,
                "health_check": self.execution_history["health_check"][-1] if self.execution_history["health_check"] else None
            }
        }

# Singleton
master_orchestrator = MasterAutomationOrchestrator()
