"""
NEXUS Cloudflare Integration Service
Manages R2 storage, KV caching, and Workers optimization
"""
import os
import boto3
from typing import Dict, Optional
from datetime import datetime
from dotenv import load_dotenv
import logging

load_dotenv()
logger = logging.getLogger(__name__)

class CloudflareService:
    """Cloudflare R2, KV, and Workers integration"""
    
    def __init__(self):
        self.r2_enabled = os.getenv('R2_ENABLED', 'false').lower() == 'true'
        self.account_id = os.getenv('CLOUDFLARE_ACCOUNT_ID')
        self.api_token = os.getenv('CLOUDFLARE_API_TOKEN')
        
        if self.r2_enabled:
            self.r2_client = boto3.client(
                's3',
                endpoint_url=os.getenv('R2_ENDPOINT_URL'),
                aws_access_key_id=os.getenv('R2_ACCESS_KEY_ID'),
                aws_secret_access_key=os.getenv('R2_SECRET_ACCESS_KEY'),
                region_name='auto'
            )
            self.bucket_name = os.getenv('R2_BUCKET_NAME', 'nexus-storage')
    
    async def upload_to_r2(self, file_content: bytes, filename: str, content_type: str = 'application/octet-stream') -> Dict:
        """Upload file to Cloudflare R2"""
        try:
            if not self.r2_enabled:
                return {"success": False, "error": "R2 not enabled"}
            
            key = f"nexus/{datetime.now().strftime('%Y/%m/%d')}/{filename}"
            
            self.r2_client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=file_content,
                ContentType=content_type
            )
            
            url = f"{os.getenv('R2_ENDPOINT_URL')}/{self.bucket_name}/{key}"
            
            return {
                "success": True,
                "url": url,
                "key": key,
                "bucket": self.bucket_name
            }
        except Exception as e:
            logger.error(f"R2 upload error: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_from_r2(self, key: str) -> Optional[bytes]:
        """Retrieve file from Cloudflare R2"""
        try:
            if not self.r2_enabled:
                return None
            
            response = self.r2_client.get_object(
                Bucket=self.bucket_name,
                Key=key
            )
            return response['Body'].read()
        except Exception as e:
            logger.error(f"R2 download error: {e}")
            return None
    
    def get_status(self) -> Dict:
        """Get Cloudflare integration status"""
        return {
            "r2_storage": {
                "enabled": self.r2_enabled,
                "bucket": self.bucket_name if self.r2_enabled else None,
                "endpoint": os.getenv('R2_ENDPOINT_URL') if self.r2_enabled else None,
                "features": [
                    "Zero egress fees",
                    "S3-compatible API",
                    "Global distribution",
                    "11 nines durability"
                ]
            },
            "kv_cache": {
                "planned": True,
                "status": "Not yet implemented",
                "use_case": "Cache AI responses, session data"
            },
            "workers": {
                "planned": True,
                "status": "Not yet implemented",
                "use_case": "Edge functions for AI preprocessing"
            },
            "durable_objects": {
                "planned": True,
                "status": "Not yet implemented",
                "use_case": "Stateful AI chat sessions"
            },
            "account_configured": bool(self.account_id and self.api_token)
        }

# Global instance
cloudflare_service = CloudflareService()


    async def kv_write(self, namespace_id: str, key: str, value: str) -> Dict:
        """Write to Cloudflare KV"""
        try:
            if not self.api_token:
                return {"success": False, "error": "Cloudflare API token not configured"}
            
            import aiohttp
            async with aiohttp.ClientSession() as session:
                headers = {"Authorization": f"Bearer {self.api_token}"}
                url = f"https://api.cloudflare.com/client/v4/accounts/{self.account_id}/storage/kv/namespaces/{namespace_id}/values/{key}"
                
                async with session.put(url, headers=headers, data=value.encode()) as resp:
                    if resp.status == 200:
                        return {"success": True, "key": key}
                    else:
                        error = await resp.text()
                        return {"success": False, "error": error}
        except Exception as e:
            logger.error(f"KV write error: {e}")
            return {"success": False, "error": str(e)}
    
    async def kv_read(self, namespace_id: str, key: str) -> Dict:
        """Read from Cloudflare KV"""
        try:
            if not self.api_token:
                return {"success": False, "error": "Cloudflare API token not configured"}
            
            import aiohttp
            async with aiohttp.ClientSession() as session:
                headers = {"Authorization": f"Bearer {self.api_token}"}
                url = f"https://api.cloudflare.com/client/v4/accounts/{self.account_id}/storage/kv/namespaces/{namespace_id}/values/{key}"
                
                async with session.get(url, headers=headers) as resp:
                    if resp.status == 200:
                        value = await resp.text()
                        return {"success": True, "key": key, "value": value}
                    elif resp.status == 404:
                        return {"success": False, "error": "Key not found"}
                    else:
                        error = await resp.text()
                        return {"success": False, "error": error}
        except Exception as e:
            logger.error(f"KV read error: {e}")
            return {"success": False, "error": str(e)}
    
    async def deploy_worker(self, name: str, script: str) -> Dict:
        """Deploy Cloudflare Worker"""
        try:
            if not self.api_token:
                return {"success": False, "error": "Cloudflare API token not configured"}
            
            import aiohttp
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.api_token}",
                    "Content-Type": "application/javascript"
                }
                url = f"https://api.cloudflare.com/client/v4/accounts/{self.account_id}/workers/scripts/{name}"
                
                async with session.put(url, headers=headers, data=script.encode()) as resp:
                    result = await resp.json()
                    if result.get("success"):
                        return {
                            "success": True,
                            "worker_name": name,
                            "url": f"https://{name}.{self.account_id}.workers.dev"
                        }
                    else:
                        return {"success": False, "error": result.get("errors", ["Unknown error"])}
        except Exception as e:
            logger.error(f"Worker deployment error: {e}")
            return {"success": False, "error": str(e)}

# Global instance
cloudflare_service = CloudflareService()

# Route registration for dynamic loading
def register_routes(db, get_current_user, require_admin):
    """Register Cloudflare routes"""
    from fastapi import APIRouter
    router = APIRouter(tags=["Cloudflare"])
    
    @router.get("/capabilities")
    async def get_capabilities():
        """Get Cloudflare capabilities"""
        return cloudflare_service.get_capabilities()
    
    @router.get("/status")
    async def get_status():
        """Get Cloudflare service status"""
        return cloudflare_service.get_status()
    
    @router.post("/kv/write")
    async def write_kv(namespace_id: str, key: str, value: str):
        """Write to KV storage"""
        return await cloudflare_service.kv_write(namespace_id, key, value)
    
    @router.get("/kv/read")
    async def read_kv(namespace_id: str, key: str):
        """Read from KV storage"""
        return await cloudflare_service.kv_read(namespace_id, key)
    
    @router.post("/worker/deploy")
    async def deploy_worker(name: str, script: str):
        """Deploy Worker"""
        return await cloudflare_service.deploy_worker(name, script)
    
    return router

def init_hybrid(db):
    return cloudflare_service
