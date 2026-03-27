import os
import asyncio
import logging
import aiohttp
from datetime import datetime, timezone
from typing import Dict, Any, List
from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
load_dotenv(ROOT_DIR / '.env')

GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN', '')
GITLAB_TOKEN = os.environ.get('GITLAB_TOKEN', '')

logger = logging.getLogger(__name__)

class AutomationService:
    """Enhanced service for automated tool discovery and CI/CD integration"""
    
    def __init__(self):
        self.github_token = GITHUB_TOKEN
        self.gitlab_token = GITLAB_TOKEN
        self.discovered_tools = []
        self.discovery_in_progress = False
        self.last_discovery_time = None
        self.discovery_history = []
    
    async def search_github_tools(self, keywords: List[str], category: str) -> List[Dict[str, Any]]:
        """Search GitHub for relevant tools and libraries"""
        if not self.github_token or self.github_token == "github_demo_token_placeholder":
            logger.warning("GitHub token not configured - returning mock data")
            return [
                {
                    "name": "mock-marketing-tool",
                    "description": "AI marketing automation",
                    "stars": 1200,
                    "url": "https://github.com/example/tool",
                    "category": category,
                    "mocked": True
                }
            ]
        
        headers = {
            "Authorization": f"token {self.github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        tools = []
        for keyword in keywords:
            try:
                query = f"{keyword} marketplace automation"
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        f"https://api.github.com/search/repositories?q={query}&sort=stars&order=desc&per_page=5",
                        headers=headers
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            for repo in data.get("items", []):
                                tools.append({
                                    "name": repo["name"],
                                    "description": repo["description"],
                                    "stars": repo["stargazers_count"],
                                    "url": repo["html_url"],
                                    "language": repo["language"],
                                    "category": category,
                                    "last_updated": repo["updated_at"]
                                })
                await asyncio.sleep(1)  # Rate limiting
            except Exception as e:
                logger.error(f"GitHub search error for {keyword}: {str(e)}")
        
        return tools
    
    async def evaluate_tool_benefit(self, tool: Dict[str, Any], platform_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate if a tool would benefit the platform"""
        # Simple scoring algorithm
        score = 0
        reasons = []
        
        # Star count scoring
        stars = tool.get("stars", 0)
        if stars > 5000:
            score += 30
            reasons.append("Highly popular and trusted")
        elif stars > 1000:
            score += 20
            reasons.append("Well-established")
        elif stars > 100:
            score += 10
        
        # Language compatibility
        language = tool.get("language", "").lower()
        if language in ["python", "javascript", "typescript"]:
            score += 20
            reasons.append("Compatible with our stack")
        
        # Category relevance
        category = tool.get("category", "").lower()
        if category in ["marketing", "analytics", "automation", "payments", "ai"]:
            score += 25
            reasons.append(f"High relevance to {category}")
        
        # Recent activity
        last_updated = tool.get("last_updated", "")
        if last_updated and "2025" in last_updated or "2024" in last_updated:
            score += 15
            reasons.append("Recently maintained")
        
        benefit_level = "low"
        if score >= 70:
            benefit_level = "high"
        elif score >= 40:
            benefit_level = "medium"
        
        return {
            "tool": tool,
            "score": score,
            "benefit_level": benefit_level,
            "reasons": reasons,
            "recommendation": "integrate" if score >= 60 else "monitor"
        }
    
    async def auto_discover_tools(self, categories: List[str]) -> Dict[str, Any]:
        """Enhanced auto-discovery with coordination and rate limiting"""
        
        # Prevent concurrent discoveries
        if self.discovery_in_progress:
            logger.warning("Discovery already in progress, skipping...")
            return {"status": "skipped", "reason": "Discovery in progress", "timestamp": datetime.now(timezone.utc).isoformat()}
        
        self.discovery_in_progress = True
        
        try:
            logger.info(f"Starting coordinated auto-discovery for categories: {categories}")
            
            discovery_results = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "categories_searched": categories,
                "tools_found": [],
                "high_priority_integrations": [],
                "monitoring_list": []
            }
            
            category_keywords = {
                "marketing": ["marketing automation", "social media", "email campaign", "analytics"],
                "investor_tools": ["crm", "fundraising", "pitch deck", "investor relations"],
                "admin_dashboard": ["admin panel", "dashboard", "monitoring", "analytics"],
                "payments": ["payment gateway", "crypto payment", "billing"],
                "ai_tools": ["llm integration", "image generation", "content generation"],
                "automation": ["workflow automation", "task scheduler", "ci cd"]
            }
            
            for category in categories:
                keywords = category_keywords.get(category, [category])
                tools = await self.search_github_tools(keywords, category)
                
                for tool in tools:
                    evaluation = await self.evaluate_tool_benefit(tool, {})
                    discovery_results["tools_found"].append(evaluation)
                    
                    if evaluation["benefit_level"] == "high":
                        discovery_results["high_priority_integrations"].append(evaluation)
                    elif evaluation["benefit_level"] == "medium":
                        discovery_results["monitoring_list"].append(evaluation)
                
                # Rate limiting between categories
                await asyncio.sleep(2)
            
            # Track discovery
            discovery_record = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "tools_found": len(discovery_results["tools_found"]),
                "high_priority": len(discovery_results["high_priority_integrations"]),
                "sources": ["github"]
            }
            
            self.discovery_history.append(discovery_record)
            if len(self.discovery_history) > 10:
                self.discovery_history.pop(0)
            
            self.last_discovery_time = datetime.now(timezone.utc)
            
            logger.info(f"✓ Coordinated discovery complete: {len(discovery_results['tools_found'])} tools, {len(discovery_results['high_priority_integrations'])} high-priority")
            discovery_results["status"] = "completed"
            return discovery_results
            
        except Exception as e:
            logger.error(f"Auto-discovery failed: {e}")
            return {"status": "error", "error": str(e), "timestamp": datetime.now(timezone.utc).isoformat()}
        finally:
            self.discovery_in_progress = False
    
    def get_discovery_stats(self) -> Dict[str, Any]:
        """Get discovery statistics and history"""
        return {
            "discovery_in_progress": self.discovery_in_progress,
            "last_discovery": self.last_discovery_time.isoformat() if self.last_discovery_time else None,
            "recent_discoveries": self.discovery_history[-5:],
            "total_discoveries": len(self.discovery_history)
        }
    
    async def create_github_webhook(self, repo_url: str) -> Dict[str, Any]:
        """Create webhook for CI/CD integration"""
        logger.info(f"GitHub webhook integration for {repo_url}")
        # Placeholder for CI/CD webhook creation
        return {
            "webhook_id": "mock_webhook",
            "repo": repo_url,
            "events": ["push", "pull_request", "release"],
            "status": "active"
        }

automation_service = AutomationService()
