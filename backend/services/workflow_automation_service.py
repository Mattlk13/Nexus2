import logging
from datetime import datetime, timezone
from typing import Dict, Any, List
from motor.motor_asyncio import AsyncIOMotorDatabase

logger = logging.getLogger(__name__)

class WorkflowAutomationService:
    """Service to catalog AI workflow automation tools from ProductHunt"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.featured_tools = [
            {
                "name": "Zapier",
                "description": "Connect your apps and automate workflows. The industry standard for no-code automation.",
                "category": "Workflow Automation",
                "use_case": "Non-technical teams who want set-and-forget automation across 6,000+ apps",
                "pricing": "Free tier: 100 tasks/mo, Pro: $19.99/mo",
                "rating": 4.8,
                "producthunt_url": "https://www.producthunt.com/products/zapier",
                "website": "https://zapier.com",
                "priority": "critical",
                "features": ["6,000+ integrations", "No-code builder", "AI-powered suggestions", "Reliable infrastructure"]
            },
            {
                "name": "n8n",
                "description": "Open-source workflow automation for technical people. Self-host or use cloud.",
                "category": "Workflow Automation",
                "use_case": "Developers who want to own their automation stack and avoid per-task pricing",
                "pricing": "Self-hosted: Free, Cloud: €20/mo",
                "rating": 4.8,
                "producthunt_url": "https://www.producthunt.com/products/n8n-io",
                "website": "https://n8n.io",
                "priority": "high",
                "features": ["Canvas-based builder", "Self-hosting", "400+ integrations", "No per-task limits"]
            },
            {
                "name": "Relay.app",
                "description": "Build an AI team that works for you. Perfect for ops and compliance teams.",
                "category": "Workflow Automation",
                "use_case": "Operations and compliance teams running sensitive workflows with human approval steps",
                "pricing": "Free tier: 200 steps/mo, Pro: $19/mo",
                "rating": 5.0,
                "producthunt_url": "https://www.producthunt.com/products/relay-app",
                "website": "https://relay.app",
                "priority": "high",
                "features": ["Human-in-the-loop", "Audit trails", "AI agents", "Compliance-ready"]
            },
            {
                "name": "Lindy",
                "description": "Personal AI assistant for inbox, scheduling, and follow-ups.",
                "category": "Personal AI",
                "use_case": "Individuals delegating personal tasks like email management and scheduling",
                "pricing": "Pro: $49.99/mo",
                "rating": 4.4,
                "producthunt_url": "https://www.producthunt.com/products/lindy",
                "website": "https://lindy.ai",
                "priority": "medium",
                "features": ["AI inbox management", "Meeting scheduling", "Pre-built templates", "SOC 2 certified"]
            },
            {
                "name": "Gumloop",
                "description": "Automate any workflow with AI. Rapid prototyping for AI workflows.",
                "category": "AI Prototyping",
                "use_case": "Builders who want to chain prompts and test AI workflows quickly",
                "pricing": "Free tier: 2K credits/mo, Solo: $37/mo",
                "rating": 5.0,
                "producthunt_url": "https://www.producthunt.com/products/gumloop",
                "website": "https://gumloop.com",
                "priority": "medium",
                "features": ["AI-first canvas", "Multi-model support", "Fast prototyping", "Visual workflow builder"]
            },
            {
                "name": "Taskade",
                "description": "One prompt. One app. One living workspace for teams with embedded AI.",
                "category": "Team Collaboration",
                "use_case": "Teams who want collaboration with embedded AI automation",
                "pricing": "Free tier available, Pro plans from $8/mo",
                "rating": 4.7,
                "producthunt_url": "https://www.producthunt.com/products/taskade",
                "website": "https://taskade.com",
                "priority": "high",
                "features": ["AI-powered collaboration", "Task automation", "Real-time sync", "Template library"]
            },
            {
                "name": "Trace",
                "description": "Workflow automations for the human + AI workforce.",
                "category": "Hybrid Automation",
                "use_case": "Teams building automation that handles ambiguity and makes context-aware decisions",
                "pricing": "Contact for pricing",
                "rating": 4.7,
                "producthunt_url": "https://www.producthunt.com/products/trace",
                "website": "https://trace.ai",
                "priority": "high",
                "features": ["AI decision-making", "Context awareness", "Human handoffs", "Slack/Jira/Notion integration"]
            }
        ]
    
    async def catalog_workflow_tools(self) -> Dict[str, Any]:
        """Catalog all workflow automation tools in database"""
        logger.info("📋 Cataloging AI workflow automation tools...")
        
        cataloged = []
        
        for tool in self.featured_tools:
            tool_doc = {
                **tool,
                "id": f"workflow-{tool['name'].lower().replace(' ', '-').replace('.', '-')}",
                "source": "producthunt_ai_workflow_automation",
                "cataloged_at": datetime.now(timezone.utc).isoformat(),
                "status": "featured"
            }
            
            await self.db.workflow_tools.update_one(
                {"id": tool_doc["id"]},
                {"$set": tool_doc},
                upsert=True
            )
            
            cataloged.append(tool_doc)
        
        logger.info(f"✓ Cataloged {len(cataloged)} workflow automation tools")
        
        return {
            "success": True,
            "total_cataloged": len(cataloged),
            "tools": cataloged,
            "by_category": self._group_by_category(cataloged),
            "by_priority": self._group_by_priority(cataloged)
        }
    
    async def get_all_workflow_tools(self) -> List[Dict[str, Any]]:
        """Get all cataloged workflow tools"""
        tools = await self.db.workflow_tools.find(
            {},
            {"_id": 0}
        ).to_list(1000)
        
        return tools
    
    async def get_tools_by_priority(self, priority: str) -> List[Dict[str, Any]]:
        """Get tools by priority"""
        tools = await self.db.workflow_tools.find(
            {"priority": priority},
            {"_id": 0}
        ).to_list(100)
        
        return tools
    
    def _group_by_category(self, tools: List[Dict]) -> Dict[str, int]:
        """Group tools by category"""
        categories = {}
        for tool in tools:
            cat = tool.get("category", "Other")
            categories[cat] = categories.get(cat, 0) + 1
        return categories
    
    def _group_by_priority(self, tools: List[Dict]) -> Dict[str, int]:
        """Group tools by priority"""
        priorities = {}
        for tool in tools:
            pri = tool.get("priority", "low")
            priorities[pri] = priorities.get(pri, 0) + 1
        return priorities

def create_workflow_automation_service(db: AsyncIOMotorDatabase):
    return WorkflowAutomationService(db)
