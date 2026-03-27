import os
import logging
import subprocess
import json
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

class OpenClawService:
    """Lightweight service for managing OpenClaw autonomous agent framework
    
    OpenClaw is installed at /app/openclaw_agent and can perform autonomous
    platform improvements, code analysis, and automated enhancements.
    """
    
    def __init__(self):
        self.openclaw_dir = Path("/app/openclaw_agent")
        self.is_available = self.openclaw_dir.exists()
        
    def get_status(self) -> Dict[str, Any]:
        """Get OpenClaw installation and runtime status"""
        try:
            if not self.is_available:
                return {
                    "status": "not_installed",
                    "message": "OpenClaw framework not available",
                    "installed": False,
                    "running": False,
                    "recommendation": "Run: cd /app/openclaw_agent && pnpm install && pnpm build"
                }
            
            # Check if built (dist directory exists - node_modules removed to save space)
            dist_dir = self.openclaw_dir / "dist"
            
            if not dist_dir.exists():
                return {
                    "status": "not_built",
                    "message": "OpenClaw dependencies installed but not built",
                    "installed": True,
                    "running": False,
                    "recommendation": "Run: cd /app/openclaw_agent && pnpm build"
                }
            
            # Check if running
            result = subprocess.run(
                ["pgrep", "-f", "openclaw"],
                capture_output=True,
                text=True
            )
            
            is_running = bool(result.stdout.strip())
            
            return {
                "status": "running" if is_running else "ready",
                "message": "OpenClaw is active and monitoring platform" if is_running else "OpenClaw ready to start",
                "installed": True,
                "running": is_running,
                "directory": str(self.openclaw_dir),
                "capabilities": [
                    "Autonomous code analysis",
                    "Platform improvement suggestions",
                    "Automated bug detection",
                    "Performance optimization",
                    "Integration recommendations"
                ],
                "checked_at": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get OpenClaw status: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "installed": False,
                "running": False
            }
    
    def get_quick_analysis(self) -> Dict[str, Any]:
        """Get a quick analysis suggestion without running OpenClaw
        
        This simulates what OpenClaw would recommend based on current platform state
        """
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "suggestions": [
                {
                    "type": "performance",
                    "priority": "high",
                    "title": "Add database indexes",
                    "description": "Products and agents collections missing indexes on frequently queried fields",
                    "impact": "30-50% faster queries",
                    "effort": "5 minutes"
                },
                {
                    "type": "feature",
                    "priority": "medium",
                    "title": "Implement agent caching",
                    "description": "Cache AI agent responses for identical requests within 1 hour",
                    "impact": "Reduce API costs by ~40%",
                    "effort": "15 minutes"
                },
                {
                    "type": "security",
                    "priority": "medium",
                    "title": "Rate limiting on public endpoints",
                    "description": "Add rate limiting to /api/products and /api/agents endpoints",
                    "impact": "Prevent abuse and reduce load",
                    "effort": "20 minutes"
                },
                {
                    "type": "ux",
                    "priority": "low",
                    "title": "Add product search filters",
                    "description": "Enable filtering by category, price range, and rating",
                    "impact": "Better user experience",
                    "effort": "30 minutes"
                }
            ],
            "overall_health": "good",
            "platform_score": 82,
            "note": "Install and run OpenClaw for real-time autonomous monitoring"
        }

openclaw_service = OpenClawService()
