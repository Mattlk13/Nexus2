"""
NEXUS Daily Automation Scheduler
Runs automated tasks on schedule

Tasks:
- Investor discovery (daily)
- System health checks
- Data backups
- Analytics updates
"""

import asyncio
import logging
from datetime import datetime, timezone, time
from typing import Dict
import os

logger = logging.getLogger(__name__)

class DailyAutomationScheduler:
    def __init__(self, db=None):
        """Initialize scheduler"""
        self.db = db
        self.running = False
        logger.info("📅 Daily Automation Scheduler initialized")
    
    async def run_investor_discovery(self) -> Dict:
        """Run daily investor discovery"""
        try:
            from services.nexus_investor_discovery import create_investor_discovery_service
            discovery_service = create_investor_discovery_service(self.db)
            
            logger.info("🔍 Running daily investor discovery...")
            result = await discovery_service.daily_investor_update()
            
            return result
        except Exception as e:
            logger.error(f"Investor discovery automation failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def run_system_health_check(self) -> Dict:
        """Check system health"""
        try:
            from services.nexus_unified_storage import unified_storage
            from services.nexus_ultimate_controller import ultimate_controller
            
            storage_status = await unified_storage.get_backend_status()
            controller_status = ultimate_controller.get_system_status()
            
            health = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "storage": storage_status,
                "controller": controller_status,
                "status": "healthy" if storage_status['active_backends'] > 0 else "degraded"
            }
            
            # Log to database
            if self.db:
                await self.db.health_checks.insert_one(health)
            
            logger.info(f"✅ System health: {health['status']}")
            return {"success": True, "health": health}
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def run_analytics_update(self) -> Dict:
        """Update analytics and metrics"""
        try:
            from services.nexus_investor_dashboard import create_investor_dashboard_service
            from services.nexus_marketing_dashboard import create_marketing_dashboard_service
            
            investor_dashboard = create_investor_dashboard_service(self.db)
            marketing_dashboard = create_marketing_dashboard_service(self.db)
            
            # Generate daily reports
            investor_report = await investor_dashboard.generate_investor_report("daily")
            marketing_report = await marketing_dashboard.generate_marketing_report("daily")
            
            logger.info("📊 Analytics updated")
            return {
                "success": True,
                "investor_report": investor_report.get('success'),
                "marketing_report": marketing_report.get('success')
            }
            
        except Exception as e:
            logger.error(f"Analytics update failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def run_daily_tasks(self):
        """Run all daily tasks"""
        logger.info("🌅 Starting daily automation tasks...")
        
        results = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "tasks": {}
        }
        
        # Task 1: Investor Discovery
        results['tasks']['investor_discovery'] = await self.run_investor_discovery()
        
        # Task 2: System Health Check
        results['tasks']['health_check'] = await self.run_system_health_check()
        
        # Task 3: Analytics Update
        results['tasks']['analytics'] = await self.run_analytics_update()
        
        # Log results
        if self.db:
            await self.db.automation_logs.insert_one(results)
        
        logger.info(f"✅ Daily tasks completed: {sum(1 for t in results['tasks'].values() if t.get('success'))}/3 successful")
        
        return results
    
    async def schedule_loop(self):
        """Main scheduling loop - runs at specific time daily"""
        self.running = True
        
        # Run time: 2 AM UTC daily
        target_hour = 2
        target_minute = 0
        
        logger.info(f"Scheduler started - will run daily at {target_hour:02d}:{target_minute:02d} UTC")
        
        while self.running:
            now = datetime.now(timezone.utc)
            
            # Check if it's time to run
            if now.hour == target_hour and now.minute == target_minute:
                await self.run_daily_tasks()
                # Sleep for 60 seconds to avoid running multiple times
                await asyncio.sleep(60)
            
            # Check every minute
            await asyncio.sleep(60)
    
    def stop(self):
        """Stop the scheduler"""
        self.running = False
        logger.info("Scheduler stopped")

# Global instance
daily_scheduler = DailyAutomationScheduler()
