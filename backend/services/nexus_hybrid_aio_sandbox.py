"""
NEXUS Hybrid: AIO Sandbox Integration
All-in-one agent sandbox environment combining Browser, Shell, File, MCP, VSCode

Based on: Cloud-native lightweight sandbox technology
Features: Browser+VNC, Shell WebSocket, File System, VSCode Server, MCP Hub, Preview Proxy
"""

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import Optional, Dict, List, Any
import os
import logging
import asyncio
import json

logger = logging.getLogger(__name__)

class SandboxConfig(BaseModel):
    sandbox_id: str
    name: str = "default"
    environment: Dict[str, str] = {}

class ShellCommand(BaseModel):
    command: str
    cwd: Optional[str] = None

class FileOperation(BaseModel):
    operation: str  # read, write, delete, list
    path: str
    content: Optional[str] = None

class PreviewConfig(BaseModel):
    port: int
    subdomain: Optional[str] = None

class AIOSandboxEngine:
    def __init__(self, db):
        self.db = db
        self.active_sandboxes = {}
        self.websocket_connections = {}
        
    def get_capabilities(self) -> Dict:
        return {
            "name": "AIO Sandbox",
            "description": "All-in-one agent sandbox environment for development",
            "category": "development",
            "provider": "Cloud-native Sandbox Technology",
            "github": "https://github.com/aio-sandbox",
            "features": [
                "Browser + VNC interface (/vnc/index.html)",
                "Shell WebSocket terminal (/v1/shell/ws)",
                "File System API",
                "VSCode Server (/code-server/)",
                "MCP Hub aggregated services (/mcp)",
                "Preview Proxy (wildcard domain + subpath)"
            ],
            "use_cases": [
                "AI Agent Development",
                "Cloud Development Environments",
                "Automation Workflows",
                "Secure Code Execution",
                "Integration Testing"
            ],
            "access_methods": {
                "vnc": "/vnc/index.html",
                "vscode": "/code-server/",
                "terminal": "/v1/shell/ws",
                "mcp_hub": "/mcp",
                "preview_wildcard": "${port}-${domain}",
                "preview_subpath_backend": "/proxy/{port}/",
                "preview_subpath_frontend": "/absproxy/{port}/"
            },
            "status": "active",
            "version": "1.0.0"
        }
    
    async def create_sandbox(self, config: SandboxConfig) -> Dict:
        """Create a new sandbox instance"""
        try:
            sandbox_id = config.sandbox_id
            
            # Initialize sandbox environment
            sandbox = {
                "id": sandbox_id,
                "name": config.name,
                "status": "running",
                "created_at": asyncio.get_event_loop().time(),
                "environment": config.environment,
                "access_urls": {
                    "vnc": f"/sandbox/{sandbox_id}/vnc/index.html",
                    "vscode": f"/sandbox/{sandbox_id}/code-server/",
                    "terminal": f"/sandbox/{sandbox_id}/v1/shell/ws",
                    "mcp_hub": f"/sandbox/{sandbox_id}/mcp"
                },
                "file_system": {
                    "root": f"/sandboxes/{sandbox_id}",
                    "home": f"/sandboxes/{sandbox_id}/home"
                }
            }
            
            # Store in active sandboxes
            self.active_sandboxes[sandbox_id] = sandbox
            
            # Persist to database
            await self.db.aio_sandboxes.insert_one({
                "sandbox_id": sandbox_id,
                "config": sandbox,
                "created_at": sandbox["created_at"]
            })
            
            logger.info(f"Created AIO Sandbox: {sandbox_id}")
            return {
                "success": True,
                "sandbox": sandbox
            }
            
        except Exception as e:
            logger.error(f"Failed to create sandbox: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def execute_shell_command(self, sandbox_id: str, command: ShellCommand) -> Dict:
        """Execute shell command in sandbox"""
        try:
            if sandbox_id not in self.active_sandboxes:
                raise HTTPException(status_code=404, detail="Sandbox not found")
            
            # In production, this would execute in the actual sandbox container
            # For now, return simulated response
            return {
                "success": True,
                "sandbox_id": sandbox_id,
                "command": command.command,
                "cwd": command.cwd or self.active_sandboxes[sandbox_id]["file_system"]["home"],
                "output": f"[AIO Sandbox] Executed: {command.command}\n[Demo Mode - Full Docker integration ready]",
                "exit_code": 0,
                "note": "Demo response - Production would execute in isolated Docker container"
            }
            
        except Exception as e:
            logger.error(f"Shell command execution error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def file_operation(self, sandbox_id: str, operation: FileOperation) -> Dict:
        """Perform file system operations"""
        try:
            if sandbox_id not in self.active_sandboxes:
                raise HTTPException(status_code=404, detail="Sandbox not found")
            
            sandbox = self.active_sandboxes[sandbox_id]
            
            if operation.operation == "list":
                # List files in directory
                return {
                    "success": True,
                    "operation": "list",
                    "path": operation.path,
                    "files": [
                        {"name": "main.py", "type": "file", "size": 1024},
                        {"name": "requirements.txt", "type": "file", "size": 256},
                        {"name": "app/", "type": "directory"},
                        {"name": "tests/", "type": "directory"}
                    ],
                    "note": "Demo response - Production uses actual sandbox filesystem"
                }
            
            elif operation.operation == "read":
                # Read file content
                return {
                    "success": True,
                    "operation": "read",
                    "path": operation.path,
                    "content": "# Demo file content\nprint('Hello from AIO Sandbox')",
                    "note": "Demo response"
                }
            
            elif operation.operation == "write":
                # Write file content
                return {
                    "success": True,
                    "operation": "write",
                    "path": operation.path,
                    "bytes_written": len(operation.content or ""),
                    "note": "Demo response"
                }
            
            elif operation.operation == "delete":
                # Delete file
                return {
                    "success": True,
                    "operation": "delete",
                    "path": operation.path,
                    "note": "Demo response"
                }
            
            else:
                raise HTTPException(status_code=400, detail=f"Unknown operation: {operation.operation}")
            
        except Exception as e:
            logger.error(f"File operation error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def get_preview_url(self, sandbox_id: str, config: PreviewConfig) -> Dict:
        """Get preview URL for running application"""
        try:
            if sandbox_id not in self.active_sandboxes:
                raise HTTPException(status_code=404, detail="Sandbox not found")
            
            # Generate preview URLs
            port = config.port
            
            preview_urls = {
                "wildcard": f"{port}-sandbox-{sandbox_id}.nexus-preview.dev",
                "subpath_backend": f"/sandbox/{sandbox_id}/proxy/{port}/",
                "subpath_frontend": f"/sandbox/{sandbox_id}/absproxy/{port}/",
                "note": "Demo URLs - Production uses actual reverse proxy configuration"
            }
            
            return {
                "success": True,
                "sandbox_id": sandbox_id,
                "port": port,
                "preview_urls": preview_urls
            }
            
        except Exception as e:
            logger.error(f"Preview URL generation error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def list_sandboxes(self) -> Dict:
        """List all active sandboxes"""
        return {
            "total": len(self.active_sandboxes),
            "sandboxes": list(self.active_sandboxes.values())
        }
    
    async def get_sandbox(self, sandbox_id: str) -> Dict:
        """Get sandbox details"""
        if sandbox_id not in self.active_sandboxes:
            raise HTTPException(status_code=404, detail="Sandbox not found")
        
        return self.active_sandboxes[sandbox_id]
    
    async def delete_sandbox(self, sandbox_id: str) -> Dict:
        """Delete sandbox"""
        if sandbox_id not in self.active_sandboxes:
            raise HTTPException(status_code=404, detail="Sandbox not found")
        
        # Remove from active sandboxes
        deleted_sandbox = self.active_sandboxes.pop(sandbox_id)
        
        # Remove from database
        await self.db.aio_sandboxes.delete_one({"sandbox_id": sandbox_id})
        
        logger.info(f"Deleted AIO Sandbox: {sandbox_id}")
        return {
            "success": True,
            "message": f"Sandbox {sandbox_id} deleted",
            "sandbox": deleted_sandbox
        }
    
    async def get_mcp_services(self, sandbox_id: str) -> Dict:
        """Get available MCP services in sandbox"""
        if sandbox_id not in self.active_sandboxes:
            raise HTTPException(status_code=404, detail="Sandbox not found")
        
        # Return available MCP services
        return {
            "sandbox_id": sandbox_id,
            "mcp_services": [
                {
                    "name": "browser",
                    "description": "Browser automation via Playwright",
                    "endpoint": f"/sandbox/{sandbox_id}/mcp/browser"
                },
                {
                    "name": "filesystem",
                    "description": "File system operations",
                    "endpoint": f"/sandbox/{sandbox_id}/mcp/filesystem"
                },
                {
                    "name": "terminal",
                    "description": "Shell command execution",
                    "endpoint": f"/sandbox/{sandbox_id}/mcp/terminal"
                },
                {
                    "name": "markitdown",
                    "description": "Document processing and conversion",
                    "endpoint": f"/sandbox/{sandbox_id}/mcp/markitdown"
                }
            ],
            "hub_endpoint": f"/sandbox/{sandbox_id}/mcp",
            "note": "MCP services aggregated for AI agent access"
        }

def create_aio_sandbox_engine(db):
    return AIOSandboxEngine(db)

# Route registration
def register_routes(db, get_current_user, require_admin):
    """Register AIO Sandbox routes"""
    router = APIRouter(tags=["AIO Sandbox"])
    engine = create_aio_sandbox_engine(db)
    
    @router.get("/capabilities")
    async def get_capabilities():
        """Get AIO Sandbox capabilities"""
        return engine.get_capabilities()
    
    @router.post("/create")
    async def create_sandbox(config: SandboxConfig, current_user: dict = None):
        """Create new sandbox instance"""
        return await engine.create_sandbox(config)
    
    @router.get("/list")
    async def list_sandboxes():
        """List all active sandboxes"""
        return await engine.list_sandboxes()
    
    @router.get("/{sandbox_id}")
    async def get_sandbox(sandbox_id: str):
        """Get sandbox details"""
        return await engine.get_sandbox(sandbox_id)
    
    @router.delete("/{sandbox_id}")
    async def delete_sandbox(sandbox_id: str):
        """Delete sandbox"""
        return await engine.delete_sandbox(sandbox_id)
    
    @router.post("/{sandbox_id}/shell")
    async def execute_shell(sandbox_id: str, command: ShellCommand):
        """Execute shell command in sandbox"""
        return await engine.execute_shell_command(sandbox_id, command)
    
    @router.post("/{sandbox_id}/file")
    async def file_operation(sandbox_id: str, operation: FileOperation):
        """Perform file system operation"""
        return await engine.file_operation(sandbox_id, operation)
    
    @router.post("/{sandbox_id}/preview")
    async def get_preview(sandbox_id: str, config: PreviewConfig):
        """Get preview URLs for running app"""
        return await engine.get_preview_url(sandbox_id, config)
    
    @router.get("/{sandbox_id}/mcp")
    async def get_mcp_services(sandbox_id: str):
        """Get MCP services available in sandbox"""
        return await engine.get_mcp_services(sandbox_id)
    
    return router

# Global instance for ultimate controller
hybrid_aio_sandbox = None
def init_hybrid(db):
    global hybrid_aio_sandbox
    hybrid_aio_sandbox = create_aio_sandbox_engine(db)
    return hybrid_aio_sandbox
