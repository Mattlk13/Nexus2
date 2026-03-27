import logging
import aiohttp
import os
from datetime import datetime, timezone
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class CloudflareWorkersService:
    """Integration with Cloudflare Workers for edge computing and optimization"""
    
    def __init__(self):
        self.api_key = os.environ.get('CLOUDFLARE_API_KEY', '')
        self.account_id = os.environ.get('CLOUDFLARE_ACCOUNT_ID', '')
        self.base_url = 'https://api.cloudflare.com/client/v4'
        
    async def deploy_worker(self, name: str, script: str) -> Dict[str, Any]:
        """Deploy a Cloudflare Worker script"""
        if not self.api_key:
            return {
                "success": False,
                "message": "Cloudflare API key not configured",
                "demo_mode": True
            }
        
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/accounts/{self.account_id}/workers/scripts/{name}"
                headers = {
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/javascript'
                }
                
                async with session.put(url, headers=headers, data=script) as response:
                    data = await response.json()
                    return {
                        "success": response.status == 200,
                        "message": "Worker deployed successfully" if response.status == 200 else data.get('errors', [])[0].get('message', 'Unknown error'),
                        "worker_name": name
                    }
        except Exception as e:
            logger.error(f"Failed to deploy worker: {str(e)}")
            return {
                "success": False,
                "message": str(e)
            }
    
    async def list_workers(self) -> List[Dict[str, Any]]:
        """List all deployed Cloudflare Workers"""
        if not self.api_key:
            return [
                {"name": "image-optimizer", "status": "demo", "routes": ["*/images/*"]},
                {"name": "api-cache", "status": "demo", "routes": ["*/api/products"]},
                {"name": "analytics-tracker", "status": "demo", "routes": ["*/track"]}
            ]
        
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/accounts/{self.account_id}/workers/scripts"
                headers = {'Authorization': f'Bearer {self.api_key}'}
                
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('result', [])
                    return []
        except Exception as e:
            logger.error(f"Failed to list workers: {str(e)}")
            return []

cloudflare_workers_service = CloudflareWorkersService()
