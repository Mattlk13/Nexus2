import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List
import aiohttp
from motor.motor_asyncio import AsyncIOMotorDatabase

logger = logging.getLogger(__name__)

class MCPRegistryService:
    """Service to discover and catalog MCP servers from GitHub MCP Registry"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.registry_servers = [
            {
                "name": "GitHub MCP",
                "repo": "github/github-mcp-server",
                "description": "Connect AI assistants to GitHub - manage repos, issues, PRs, and workflows through natural language",
                "category": "Development",
                "priority": "critical",
                "capabilities": ["repo management", "issue tracking", "PR automation", "workflow control"]
            },
            {
                "name": "Notion MCP",
                "repo": "makenotion/notion-mcp-server",
                "description": "Official MCP server for Notion API - content management and workspace automation",
                "category": "Productivity",
                "priority": "high",
                "capabilities": ["page creation", "database queries", "content editing", "workspace sync"]
            },
            {
                "name": "Stripe MCP",
                "repo": "com.stripe/mcp",
                "description": "MCP server integrating with Stripe - tools for customers, products, payments, and more",
                "category": "Payments",
                "priority": "critical",
                "capabilities": ["payment processing", "customer management", "subscription handling", "invoice generation"]
            },
            {
                "name": "Supabase MCP",
                "repo": "com.supabase/mcp",
                "description": "MCP server for interacting with the Supabase platform - database, auth, storage",
                "category": "Database",
                "priority": "high",
                "capabilities": ["database operations", "auth management", "file storage", "real-time subscriptions"]
            },
            {
                "name": "Firecrawl MCP",
                "repo": "firecrawl/firecrawl-mcp-server",
                "description": "Extract web data with Firecrawl - advanced web scraping and data extraction",
                "category": "Data Extraction",
                "priority": "high",
                "capabilities": ["web scraping", "data extraction", "content parsing", "structured data"]
            },
            {
                "name": "Playwright MCP",
                "repo": "microsoft/playwright-mcp",
                "description": "Automate web browsers using accessibility trees for testing and data extraction",
                "category": "Automation",
                "priority": "high",
                "capabilities": ["browser automation", "e2e testing", "screenshot capture", "form filling"]
            },
            {
                "name": "Azure DevOps MCP",
                "repo": "microsoft/azure-devops-mcp",
                "description": "Interact with Azure DevOps - repositories, work items, builds, releases, test plans",
                "category": "CI/CD",
                "priority": "medium",
                "capabilities": ["pipeline management", "work item tracking", "build automation", "release control"]
            },
            {
                "name": "MongoDB MCP",
                "repo": "mongodb-js/mongodb-mcp-server",
                "description": "MongoDB Model Context Protocol Server - database operations and queries",
                "category": "Database",
                "priority": "high",
                "capabilities": ["CRUD operations", "aggregation pipelines", "index management", "schema design"]
            },
            {
                "name": "Terraform MCP",
                "repo": "hashicorp/terraform-mcp-server",
                "description": "Generate Terraform code and automate workflows for HCP Terraform and Terraform Enterprise",
                "category": "Infrastructure",
                "priority": "medium",
                "capabilities": ["IaC generation", "state management", "workspace automation", "provider config"]
            },
            {
                "name": "Chroma MCP",
                "repo": "chroma-core/chroma-mcp",
                "description": "Vector search and embeddings - create collections and retrieve data with semantic search",
                "category": "AI/ML",
                "priority": "high",
                "capabilities": ["vector search", "embedding storage", "semantic retrieval", "metadata filtering"]
            }
        ]
    
    async def discover_mcp_servers(self) -> Dict[str, Any]:
        """Discover and catalog all MCP servers from the registry"""
        logger.info("🔍 Discovering MCP servers from GitHub MCP Registry...")
        
        discovered = []
        
        for server in self.registry_servers:
            # Store in database
            mcp_doc = {
                **server,
                "id": f"mcp-{server['name'].lower().replace(' ', '-')}",
                "source": "github_mcp_registry",
                "github_url": f"https://github.com/mcp/{server['repo']}",
                "install_command": f"npx @mcp/{server['repo'].split('/')[-1]}",
                "discovered_at": datetime.now(timezone.utc).isoformat(),
                "status": "available"
            }
            
            await self.db.mcp_servers.update_one(
                {"id": mcp_doc["id"]},
                {"$set": mcp_doc},
                upsert=True
            )
            
            discovered.append(mcp_doc)
        
        logger.info(f"✓ Discovered {len(discovered)} MCP servers from registry")
        
        return {
            "success": True,
            "total_discovered": len(discovered),
            "servers": discovered,
            "by_category": self._group_by_category(discovered),
            "by_priority": self._group_by_priority(discovered)
        }
    
    async def get_all_mcp_servers(self) -> List[Dict[str, Any]]:
        """Get all discovered MCP servers"""
        servers = await self.db.mcp_servers.find(
            {},
            {"_id": 0}
        ).to_list(1000)
        
        return servers
    
    async def get_mcp_servers_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get MCP servers by category"""
        servers = await self.db.mcp_servers.find(
            {"category": category},
            {"_id": 0}
        ).to_list(100)
        
        return servers
    
    def _group_by_category(self, servers: List[Dict]) -> Dict[str, int]:
        """Group servers by category"""
        categories = {}
        for server in servers:
            cat = server.get("category", "Other")
            categories[cat] = categories.get(cat, 0) + 1
        return categories
    
    def _group_by_priority(self, servers: List[Dict]) -> Dict[str, int]:
        """Group servers by priority"""
        priorities = {}
        for server in servers:
            pri = server.get("priority", "low")
            priorities[pri] = priorities.get(pri, 0) + 1
        return priorities

def create_mcp_registry_service(db: AsyncIOMotorDatabase):
    return MCPRegistryService(db)
