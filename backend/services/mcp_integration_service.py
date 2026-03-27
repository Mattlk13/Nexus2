import logging
import os
import json
import asyncio
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
import subprocess

logger = logging.getLogger(__name__)

class MCPServerIntegrationService:
    """Service to integrate and use MCP (Model Context Protocol) servers
    
    Allows NEXUS to connect to discovered MCP servers and use their tools/capabilities
    """
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.active_servers = {}
        
    async def discover_available_mcp_servers(self) -> List[Dict[str, Any]]:
        """Get list of discovered MCP servers from mega scans"""
        try:
            # Get latest mega scan
            scan = await self.db.mega_scans.find_one(
                {},
                {"_id": 0},
                sort=[("scan_timestamp", -1)]
            )
            
            if not scan:
                return []
            
            # Extract MCP servers
            mcp_data = scan.get('results', {}).get('sources', {}).get('mcp_servers', {})
            servers = mcp_data.get('servers', [])
            
            logger.info(f"Found {len(servers)} MCP servers from discovery")
            return servers
            
        except Exception as e:
            logger.error(f"Failed to get MCP servers: {str(e)}")
            return []
    
    async def connect_to_mcp_server(self, server_config: Dict[str, Any]) -> Dict[str, Any]:
        """Connect to an MCP server and get its capabilities
        
        Args:
            server_config: {
                "name": "weather-server",
                "url": "github.com/user/mcp-weather",
                "transport": "stdio",  # or "http"
                "command": "python server.py"  # for stdio
            }
        """
        try:
            server_name = server_config.get('name')
            transport = server_config.get('transport', 'stdio')
            
            if transport == 'stdio':
                # For local/stdio MCP servers
                result = await self._connect_stdio_server(server_config)
            elif transport == 'http':
                # For HTTP-based MCP servers
                result = await self._connect_http_server(server_config)
            else:
                return {
                    "success": False,
                    "error": f"Unsupported transport: {transport}"
                }
            
            # Store active connection
            if result.get('success'):
                self.active_servers[server_name] = {
                    "config": server_config,
                    "capabilities": result.get('capabilities', []),
                    "connected_at": datetime.now(timezone.utc).isoformat()
                }
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to connect to MCP server: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _connect_stdio_server(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Connect to stdio-based MCP server"""
        # For now, return demo capabilities
        # Full implementation would spawn subprocess and communicate via stdio
        return {
            "success": False,
            "demo_mode": True,
            "message": "Stdio MCP servers require local installation",
            "capabilities": [
                {"name": "example_tool", "description": "Example capability"}
            ]
        }
    
    async def _connect_http_server(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Connect to HTTP-based MCP server"""
        import aiohttp
        
        try:
            url = config.get('url')
            if not url.startswith('http'):
                url = f"https://{url}"
            
            async with aiohttp.ClientSession() as session:
                # Send MCP initialization request
                init_request = {
                    "jsonrpc": "2.0",
                    "method": "initialize",
                    "params": {
                        "protocolVersion": "2024-11-05",
                        "clientInfo": {
                            "name": "nexus-ai",
                            "version": "4.4.0"
                        }
                    },
                    "id": 1
                }
                
                async with session.post(url, json=init_request, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "success": True,
                            "server_info": data.get('result', {}),
                            "capabilities": data.get('result', {}).get('capabilities', [])
                        }
                    else:
                        return {
                            "success": False,
                            "error": f"HTTP {response.status}"
                        }
                        
        except Exception as e:
            logger.error(f"HTTP MCP connection failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def call_mcp_tool(
        self, 
        server_name: str, 
        tool_name: str, 
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Call a tool on a connected MCP server"""
        try:
            if server_name not in self.active_servers:
                return {
                    "success": False,
                    "error": "Server not connected"
                }
            
            server_info = self.active_servers[server_name]
            config = server_info['config']
            
            # For demo, return mock response
            return {
                "success": True,
                "demo_mode": True,
                "result": {
                    "tool": tool_name,
                    "arguments": arguments,
                    "response": "Demo response - MCP tool execution simulated"
                }
            }
            
        except Exception as e:
            logger.error(f"MCP tool call failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def list_active_servers(self) -> List[Dict[str, Any]]:
        """List all active MCP server connections"""
        return [
            {
                "name": name,
                "capabilities": info['capabilities'],
                "connected_at": info['connected_at']
            }
            for name, info in self.active_servers.items()
        ]
    
    async def get_mcp_integration_status(self) -> Dict[str, Any]:
        """Get MCP integration status"""
        discovered = await self.discover_available_mcp_servers()
        
        return {
            "discovered_servers": len(discovered),
            "active_connections": len(self.active_servers),
            "available_servers": [
                {
                    "name": s.get('name'),
                    "url": s.get('url'),
                    "source": s.get('source')
                }
                for s in discovered
            ],
            "active_servers": await self.list_active_servers(),
            "status": "demo_mode",
            "message": "MCP integration available - servers discovered but not yet connected"
        }

def create_mcp_server_integration_service(db: AsyncIOMotorDatabase):
    return MCPServerIntegrationService(db)
