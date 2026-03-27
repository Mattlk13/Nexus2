"""
Slack Notification Service
Sends real-time alerts for tests, deployments, errors, and autonomous actions
"""
import logging
import httpx
import os
import json
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from enum import Enum

logger = logging.getLogger(__name__)

class NotificationLevel(Enum):
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class SlackNotificationService:
    """
    Sends notifications to Slack for all autonomous system events.
    
    Events:
    - Test failures/successes
    - Deployment status
    - Health check failures
    - Auto-fix attempts
    - Task completions
    - Security vulnerabilities
    """
    
    def __init__(self):
        self.webhook_url = os.getenv('SLACK_WEBHOOK_URL', '')
        self.enabled = bool(self.webhook_url)
        self.channel = os.getenv('SLACK_CHANNEL', '#nexus-alerts')
        
        if self.enabled:
            logger.info("✓ Slack notifications enabled")
        else:
            logger.info("Slack notifications disabled (set SLACK_WEBHOOK_URL to enable)")
    
    async def send_notification(
        self,
        title: str,
        message: str,
        level: NotificationLevel = NotificationLevel.INFO,
        fields: Optional[Dict[str, str]] = None
    ) -> bool:
        """Send notification to Slack"""
        if not self.enabled:
            return False
        
        # Color based on level
        colors = {
            NotificationLevel.INFO: "#0099ff",
            NotificationLevel.SUCCESS: "#00cc00",
            NotificationLevel.WARNING: "#ff9900",
            NotificationLevel.ERROR: "#ff0000",
            NotificationLevel.CRITICAL: "#990000"
        }
        
        # Build attachment
        attachment = {
            "color": colors[level],
            "title": title,
            "text": message,
            "footer": "NEXUS Autonomous Systems",
            "ts": int(datetime.now(timezone.utc).timestamp())
        }
        
        if fields:
            attachment["fields"] = [
                {"title": k, "value": v, "short": True}
                for k, v in fields.items()
            ]
        
        payload = {
            "channel": self.channel,
            "username": "NEXUS Bot",
            "icon_emoji": ":robot_face:",
            "attachments": [attachment]
        }
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(self.webhook_url, json=payload)
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Slack notification failed: {e}")
            return False
    
    async def notify_test_failure(self, test_results: Dict[str, Any]):
        """Notify about test failures"""
        failed_tests = []
        if not test_results.get("backend_tests", {}).get("passed"):
            failed_tests.append("Backend Tests")
        if not test_results.get("integration_tests", {}).get("passed"):
            failed_tests.append("Integration Tests")
        
        if failed_tests:
            await self.send_notification(
                title="🚨 Test Failures Detected",
                message=f"Failed: {', '.join(failed_tests)}",
                level=NotificationLevel.ERROR,
                fields={
                    "Status": test_results.get("overall_status", "unknown"),
                    "Time": test_results.get("timestamp", "")
                }
            )
    
    async def notify_test_success(self, test_results: Dict[str, Any]):
        """Notify about successful test runs"""
        await self.send_notification(
            title="✅ All Tests Passed",
            message="Complete test suite executed successfully",
            level=NotificationLevel.SUCCESS,
            fields={
                "Coverage": f"{test_results.get('coverage', {}).get('total_coverage', 0):.1f}%",
                "Time": test_results.get("timestamp", "")
            }
        )
    
    async def notify_deployment(self, status: str, details: str):
        """Notify about deployment"""
        level = NotificationLevel.SUCCESS if status == "success" else NotificationLevel.ERROR
        emoji = "🚀" if status == "success" else "❌"
        
        await self.send_notification(
            title=f"{emoji} Deployment {status.title()}",
            message=details,
            level=level
        )
    
    async def notify_health_failure(self, health_status: Dict[str, Any]):
        """Notify about health check failures"""
        failed_services = [
            service for service, healthy in health_status.get("services", {}).items()
            if not healthy
        ]
        
        if failed_services:
            await self.send_notification(
                title="⚠️ Health Check Failed",
                message=f"Services down: {', '.join(failed_services)}",
                level=NotificationLevel.CRITICAL,
                fields={"Auto-Heal": "Attempting restart"}
            )
    
    async def notify_security_vulnerability(self, vulnerability: Dict[str, Any]):
        """Notify about security vulnerabilities"""
        await self.send_notification(
            title="🔒 Security Vulnerability Detected",
            message=vulnerability.get("type", "Unknown"),
            level=NotificationLevel.WARNING,
            fields={
                "Severity": vulnerability.get("severity", "unknown"),
                "Count": str(vulnerability.get("count", 0))
            }
        )
    
    async def notify_task_completion(self, task: Dict[str, Any]):
        """Notify about autonomous task completion"""
        await self.send_notification(
            title="🤖 Task Completed",
            message=task.get("description", "Unknown task"),
            level=NotificationLevel.SUCCESS,
            fields={
                "Status": task.get("status", "unknown"),
                "Duration": f"{task.get('duration', 0):.1f}s"
            }
        )
    
    async def notify_auto_fix_attempt(self, issue: str, success: bool):
        """Notify about auto-fix attempts"""
        level = NotificationLevel.SUCCESS if success else NotificationLevel.WARNING
        emoji = "🔧" if success else "⚙️"
        
        await self.send_notification(
            title=f"{emoji} Auto-Fix {'Successful' if success else 'Attempted'}",
            message=issue,
            level=level
        )

# Singleton
slack_notifications = SlackNotificationService()
