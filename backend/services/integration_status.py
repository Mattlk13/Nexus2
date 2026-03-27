import os
import logging
from datetime import datetime, timezone
from typing import Dict, Any
from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
load_dotenv(ROOT_DIR / '.env')

logger = logging.getLogger(__name__)

class IntegrationStatusService:
    """Centralized service to check status of all integrations"""
    
    def __init__(self):
        self.integrations = {
            "emergent_llm": os.environ.get('EMERGENT_LLM_KEY', ''),
            "stripe": os.environ.get('STRIPE_API_KEY', ''),
            "resend": os.environ.get('RESEND_API_KEY', ''),
            "github": os.environ.get('GITHUB_TOKEN', ''),
            "gitlab": os.environ.get('GITLAB_TOKEN', ''),
            "producthunt": os.environ.get('PRODUCTHUNT_API_KEY', ''),
            "manus": os.environ.get('MANUS_API_KEY', ''),
            "softr": os.environ.get('SOFTR_API_KEY', ''),
            "elevenlabs": os.environ.get('ELEVENLABS_API_KEY', ''),
            "fal_ai": os.environ.get('FAL_KEY', ''),
            "openclaw": "installed"  # Special handling
        }
    
    def _is_active(self, key: str) -> bool:
        """Check if an API key is configured (not demo/placeholder)"""
        if not key:
            return False
        placeholder_terms = ['demo', 'placeholder', 'your_key', 'test_key']
        return not any(term in key.lower() for term in placeholder_terms)
    
    def get_all_integrations_status(self) -> Dict[str, Any]:
        """Get status of all NEXUS integrations"""
        
        statuses = {
            "emergent_llm": {
                "name": "Emergent LLM Key",
                "description": "Universal key for OpenAI, Gemini, Claude",
                "active": self._is_active(self.integrations["emergent_llm"]),
                "status": "active" if self._is_active(self.integrations["emergent_llm"]) else "missing",
                "features": ["GPT-5.2 (text/music/video)", "Gemini Nano Banana (images)", "Claude Sonnet 4 (moderation)"],
                "priority": "critical",
                "setup_required": not self._is_active(self.integrations["emergent_llm"])
            },
            "stripe": {
                "name": "Stripe Payments",
                "description": "Payment processing for purchases and boosts",
                "active": self._is_active(self.integrations["stripe"]),
                "status": "active" if self._is_active(self.integrations["stripe"]) else "missing",
                "features": ["Product purchases", "Boost payments", "Vendor payouts"],
                "priority": "critical",
                "setup_required": not self._is_active(self.integrations["stripe"])
            },
            "resend": {
                "name": "Resend Email",
                "description": "Transactional email service",
                "active": self._is_active(self.integrations["resend"]),
                "status": "demo_mode" if not self._is_active(self.integrations["resend"]) else "active",
                "features": ["Welcome emails", "Sale notifications", "New follower alerts"],
                "priority": "high",
                "setup_required": not self._is_active(self.integrations["resend"]),
                "demo_behavior": "Logs emails to console instead of sending"
            },
            "github": {
                "name": "GitHub API",
                "description": "Code repository monitoring and discovery",
                "active": self._is_active(self.integrations["github"]),
                "status": "limited" if not self._is_active(self.integrations["github"]) else "active",
                "features": ["Trending AI repos", "Repository search", "CI/CD monitoring"],
                "priority": "medium",
                "setup_required": not self._is_active(self.integrations["github"]),
                "rate_limit": "5,000/hour" if self._is_active(self.integrations["github"]) else "60/hour (unauthenticated)"
            },
            "gitlab": {
                "name": "GitLab API",
                "description": "CI/CD pipeline monitoring",
                "active": self._is_active(self.integrations["gitlab"]),
                "status": "demo_mode" if not self._is_active(self.integrations["gitlab"]) else "active",
                "features": ["Project monitoring", "Pipeline status", "Deployment tracking"],
                "priority": "low",
                "setup_required": not self._is_active(self.integrations["gitlab"]),
                "demo_behavior": "Returns mock project data"
            },
            "producthunt": {
                "name": "ProductHunt API",
                "description": "Discover trending AI products",
                "active": self._is_active(self.integrations["producthunt"]),
                "status": "blocked" if not self._is_active(self.integrations["producthunt"]) else "active",
                "features": ["Top AI products", "Vote counts", "Product discovery"],
                "priority": "medium",
                "setup_required": not self._is_active(self.integrations["producthunt"]),
                "demo_behavior": "Skipped during scans (403 error without API key)"
            },
            "manus": {
                "name": "Manus AI",
                "description": "Autonomous task orchestration",
                "active": self._is_active(self.integrations["manus"]),
                "status": "demo_mode" if not self._is_active(self.integrations["manus"]) else "active",
                "features": ["Complex task execution", "Multi-step workflows", "Autonomous agents"],
                "priority": "low",
                "setup_required": not self._is_active(self.integrations["manus"]),
                "demo_behavior": "Returns mock task IDs and results"
            },
            "softr": {
                "name": "Softr Database",
                "description": "Scrape integrations from Softr database",
                "active": self._is_active(self.integrations["softr"]),
                "status": "scraping_mode" if not self._is_active(self.integrations["softr"]) else "api_mode",
                "features": ["Integration discovery", "Database scraping", "Tool categorization"],
                "priority": "medium",
                "setup_required": False,
                "demo_behavior": "Uses web scraping (add API key for authenticated access)"
            },
            "elevenlabs": {
                "name": "ElevenLabs Voice",
                "description": "Text-to-speech and voice cloning",
                "active": self._is_active(self.integrations["elevenlabs"]),
                "status": "active" if self._is_active(self.integrations["elevenlabs"]) else "missing",
                "features": ["Voice generation", "Speech-to-text", "Voice cloning"],
                "priority": "medium",
                "setup_required": not self._is_active(self.integrations["elevenlabs"]),
                "get_key_url": "https://elevenlabs.io/app/settings/api-keys"
            },
            "fal_ai": {
                "name": "Fal.ai Images",
                "description": "Fast AI image generation with FLUX models",
                "active": self._is_active(self.integrations["fal_ai"]),
                "status": "active" if self._is_active(self.integrations["fal_ai"]) else "missing",
                "features": ["FLUX image generation", "Fast rendering", "Multiple models"],
                "priority": "medium",
                "setup_required": not self._is_active(self.integrations["fal_ai"]),
                "get_key_url": "https://fal.ai/dashboard/keys"
            },
            "openclaw": {
                "name": "OpenClaw Agent",
                "description": "Autonomous platform improvement agent",
                "active": Path("/app/openclaw_agent/dist").exists(),
                "status": "ready" if Path("/app/openclaw_agent/dist").exists() else "not_installed",
                "features": ["Code analysis", "Performance optimization", "Bug detection"],
                "priority": "low",
                "setup_required": not Path("/app/openclaw_agent/dist").exists(),
                "setup_command": "bash /app/setup_openclaw.sh"
            }
        }
        
        # Count active vs inactive
        active_count = sum(1 for s in statuses.values() if s["active"])
        total_count = len(statuses)
        critical_missing = [k for k, v in statuses.items() if v["priority"] == "critical" and not v["active"]]
        
        return {
            "integrations": statuses,
            "summary": {
                "total": total_count,
                "active": active_count,
                "inactive": total_count - active_count,
                "health_score": (active_count / total_count) * 100,
                "critical_missing": critical_missing
            },
            "checked_at": datetime.now(timezone.utc).isoformat()
        }
    
    def get_integration_health(self) -> str:
        """Get overall integration health status"""
        status = self.get_all_integrations_status()
        score = status["summary"]["health_score"]
        
        if score >= 80:
            return "excellent"
        elif score >= 60:
            return "good"
        elif score >= 40:
            return "fair"
        else:
            return "needs_attention"

integration_status_service = IntegrationStatusService()
