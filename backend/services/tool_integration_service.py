import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List
from motor.motor_asyncio import AsyncIOMotorDatabase
import os

logger = logging.getLogger(__name__)

class DiscoveredToolsIntegrationService:
    """Service to integrate all discovered AI tools into NEXUS marketplace
    
    This service processes tools discovered by the autonomous discovery engine
    and integrates them as:
    1. Agent marketplace listings (for all tools)
    2. Direct API integrations (for tools with public APIs)
    """
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        
    async def integrate_all_discovered_tools(self) -> Dict[str, Any]:
        """Integrate all discovered tools from latest aixploria scan"""
        logger.info("🔄 Starting integration of all discovered tools...")
        
        try:
            # Fetch latest scan with all discovered tools
            scan = await self.db.aixploria_scans.find_one(
                {},
                {"_id": 0},
                sort=[("scan_timestamp", -1)]
            )
            
            if not scan:
                return {
                    "success": False,
                    "message": "No scans found. Run a discovery scan first.",
                    "integrated": 0
                }
            
            # Extract all tools from scan
            all_tools = []
            
            # Get tools from each priority level
            for priority_level in ['critical_integrations', 'high_priority', 'medium_priority']:
                tools_list = scan.get(priority_level, [])
                if isinstance(tools_list, list):
                    for tool in tools_list:
                        if isinstance(tool, dict):
                            tool['benefit_level'] = priority_level.replace('_integrations', '').replace('_', ' ')
                            all_tools.append(tool)
                        elif isinstance(tool, str):
                            # Simple string entry
                            all_tools.append({
                                'name': tool,
                                'benefit_level': priority_level.replace('_integrations', '').replace('_', ' ')
                            })
            
            if not all_tools:
                return {
                    "success": False,
                    "message": "No tools found in latest scan",
                    "integrated": 0
                }
            
            logger.info(f"Found {len(all_tools)} tools to integrate from latest scan")
            
            # Integrate as marketplace agents
            agents_created = await self._create_marketplace_agents(all_tools)
            
            return {
                "success": True,
                "message": f"Successfully integrated {agents_created} discovered tools as marketplace agents",
                "scan_id": scan.get('scan_id', 'unknown'),
                "scan_timestamp": scan.get('scan_timestamp', 'unknown'),
                "total_tools_found": len(all_tools),
                "agents_created": agents_created,
                "integration_details": {
                    "critical": len([t for t in all_tools if 'critical' in t.get('benefit_level', '')]),
                    "high": len([t for t in all_tools if 'high' in t.get('benefit_level', '')]),
                    "medium": len([t for t in all_tools if 'medium' in t.get('benefit_level', '')])
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to integrate tools: {str(e)}")
            return {
                "success": False,
                "message": str(e),
                "integrated": 0
            }
    
    def _is_api_integratable(self, tool: Dict[str, Any]) -> bool:
        """Check if tool likely has a public API for direct integration"""
        name = tool.get('name', '').lower()
        category = tool.get('category', '').lower()
        
        # Keywords indicating API availability
        api_keywords = [
            'gpt', 'claude', 'gemini', 'mistral', 'llm', 'api',
            'openai', 'anthropic', 'google', 'chatbot', 'generation',
            'bot', 'sdk', 'developer'
        ]
        
        # Check name and category
        return any(keyword in name or keyword in category for keyword in api_keywords)
    
    async def _create_marketplace_agents(self, tools: List[Dict[str, Any]]) -> int:
        """Create agent marketplace listings for discovered tools"""
        created = 0
        
        for tool in tools:
            try:
                # Check if agent already exists
                existing = await self.db.agents.find_one(
                    {"name": tool['name']},
                    {"_id": 0}
                )
                
                if existing:
                    logger.debug(f"Agent {tool['name']} already exists, skipping")
                    continue
                
                # Create agent document
                agent = {
                    "id": f"discovered-{tool['name'].lower().replace(' ', '-')}",
                    "name": tool['name'],
                    "description": tool.get('description', f"AI tool for {tool.get('category', 'general tasks')}"),
                    "category": self._map_category(tool.get('category', 'General')),
                    "icon": self._get_icon_for_category(tool.get('category', 'General')),
                    "color": self._get_color_for_category(tool.get('category', 'General')),
                    "capabilities": self._generate_capabilities(tool),
                    "pricing": {
                        "free": True,
                        "premium": False
                    },
                    "status": "active",
                    "source": "discovered_autonomous",
                    "discovery_score": tool.get('nexus_score', 50),
                    "external_url": tool.get('url', ''),
                    "discovered_at": tool.get('discovered_at', datetime.now(timezone.utc).isoformat()),
                    "benefit_level": tool.get('benefit_level', 'medium'),
                    "created_at": datetime.now(timezone.utc).isoformat()
                }
                
                # Insert agent
                await self.db.agents.insert_one(agent)
                created += 1
                logger.info(f"✓ Created agent: {tool['name']}")
                
            except Exception as e:
                logger.error(f"Failed to create agent for {tool.get('name', 'unknown')}: {str(e)}")
                continue
        
        logger.info(f"✓ Created {created} new agent marketplace listings")
        return created
    
    def _map_category(self, original_category: str) -> str:
        """Map discovered tool category to NEXUS agent category"""
        mapping = {
            'chatbot': 'Chatbot',
            'code generation': 'Developer',
            'code': 'Developer',
            'video creation': 'Video',
            'video': 'Video',
            'audio': 'Music',
            'music generation': 'Music',
            'image generation': 'Art',
            'image': 'Art',
            'llm': 'Chatbot',
            'writing': 'Writing',
            'email': 'Marketing',
            'marketing': 'Marketing',
            'business': 'Business',
            'data': 'Data',
            'design': 'Art'
        }
        
        original_lower = original_category.lower()
        for key, value in mapping.items():
            if key in original_lower:
                return value
        
        return 'General'
    
    def _get_icon_for_category(self, category: str) -> str:
        """Get appropriate icon for category"""
        icons = {
            'Chatbot': '💬',
            'Developer': '💻',
            'Video': '🎬',
            'Music': '🎵',
            'Art': '🎨',
            'Writing': '✍️',
            'Marketing': '📈',
            'Business': '💼',
            'Data': '📊',
            'General': '🤖'
        }
        mapped_cat = self._map_category(category)
        return icons.get(mapped_cat, '🤖')
    
    def _get_color_for_category(self, category: str) -> str:
        """Get color scheme for category"""
        colors = {
            'Chatbot': 'from-blue-500 to-purple-500',
            'Developer': 'from-green-500 to-teal-500',
            'Video': 'from-red-500 to-pink-500',
            'Music': 'from-purple-500 to-pink-500',
            'Art': 'from-yellow-500 to-orange-500',
            'Writing': 'from-indigo-500 to-blue-500',
            'Marketing': 'from-orange-500 to-red-500',
            'Business': 'from-gray-500 to-slate-500',
            'Data': 'from-cyan-500 to-blue-500',
            'General': 'from-gray-400 to-gray-600'
        }
        mapped_cat = self._map_category(category)
        return colors.get(mapped_cat, 'from-gray-400 to-gray-600')
    
    def _generate_capabilities(self, tool: Dict[str, Any]) -> List[str]:
        """Generate capability list based on tool info"""
        category = tool.get('category', '').lower()
        name = tool.get('name', '').lower()
        
        base_capabilities = {
            'chatbot': ['Natural conversation', 'Context awareness', 'Multi-turn dialogue'],
            'code': ['Code generation', 'Debugging assistance', 'Documentation'],
            'video': ['Video generation', 'Editing tools', 'Effects'],
            'audio': ['Audio generation', 'Sound effects', 'Voice synthesis'],
            'music': ['Music composition', 'Beat generation', 'Audio mixing'],
            'image': ['Image generation', 'Style transfer', 'Enhancement'],
            'writing': ['Content creation', 'Editing', 'Suggestions'],
            'llm': ['Text generation', 'Analysis', 'Reasoning']
        }
        
        # Find matching capabilities
        for key, caps in base_capabilities.items():
            if key in category or key in name:
                return caps
        
        return ['AI-powered automation', 'Smart processing', 'Advanced features']
    
    async def get_integration_status(self) -> Dict[str, Any]:
        """Get status of tool integration"""
        try:
            # Get latest scan
            scan = await self.db.aixploria_scans.find_one(
                {},
                {"_id": 0},
                sort=[("scan_timestamp", -1)]
            )
            
            if not scan:
                return {
                    "total_discovered": 0,
                    "integrated": 0,
                    "pending_integration": 0,
                    "marketplace_agents_created": 0,
                    "integration_rate": "0%"
                }
            
            total_discovered = scan.get('total_tools_discovered', 0)
            
            # Get agent count created from discoveries
            discovered_agents = await self.db.agents.count_documents(
                {"source": "discovered_autonomous"}
            )
            
            # Check how many from scan are now agents
            integrated = discovered_agents
            pending = max(0, total_discovered - integrated)
            
            return {
                "total_discovered": total_discovered,
                "integrated": integrated,
                "pending_integration": pending,
                "marketplace_agents_created": discovered_agents,
                "integration_rate": f"{(integrated/total_discovered*100):.1f}%" if total_discovered > 0 else "0%",
                "latest_scan": scan.get('scan_timestamp', 'N/A')[:19]
            }
            
        except Exception as e:
            logger.error(f"Failed to get integration status: {str(e)}")
            return {
                "total_discovered": 0,
                "integrated": 0,
                "pending_integration": 0,
                "marketplace_agents_created": 0,
                "integration_rate": "0%"
            }

def create_discovered_tools_integration_service(db: AsyncIOMotorDatabase):
    return DiscoveredToolsIntegrationService(db)
