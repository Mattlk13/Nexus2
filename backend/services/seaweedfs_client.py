"""
SeaweedFS Client - Distributed object storage
Preparation for future integration
"""
import logging
import aiohttp
from typing import Dict, Any, Optional
import os

logger = logging.getLogger(__name__)

class SeaweedFSClient:
    """SeaweedFS distributed storage client"""
    
    def __init__(self):
        self.master_url = os.environ.get('SEAWEEDFS_MASTER', 'localhost:9333')
        self.enabled = os.environ.get('SEAWEEDFS_ENABLED', 'false').lower() == 'true'
        self.available = False
        
        if self.enabled:
            logger.info(f"SeaweedFS client initialized (master: {self.master_url})")
    
    async def assign_file_key(self) -> Optional[Dict[str, Any]]:
        """Assign a new file key from SeaweedFS master"""
        if not self.enabled:
            return None
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"http://{self.master_url}/dir/assign",
                    timeout=5
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.available = True
                        return {
                            'fid': data['fid'],
                            'url': data['url'],
                            'public_url': data.get('publicUrl', data['url'])
                        }
                    return None
        except Exception as e:
            logger.warning(f"SeaweedFS not available: {e}")
            self.available = False
            return None
    
    async def upload_file(self, file_data: bytes, filename: str, content_type: str = 'application/octet-stream') -> Optional[Dict[str, Any]]:
        """Upload file to SeaweedFS"""
        if not self.enabled:
            return None
        
        try:
            # Get file assignment
            assignment = await self.assign_file_key()
            if not assignment:
                return None
            
            # Upload to assigned volume server
            fid = assignment['fid']
            url = assignment['url']
            
            async with aiohttp.ClientSession() as session:
                form_data = aiohttp.FormData()
                form_data.add_field('file', file_data, filename=filename, content_type=content_type)
                
                async with session.post(
                    f"http://{url}/{fid}",
                    data=form_data,
                    timeout=30
                ) as response:
                    if response.status in [200, 201]:
                        result = await response.json()
                        return {
                            'success': True,
                            'fid': fid,
                            'url': f"http://{assignment['public_url']}/{fid}",
                            'size': result.get('size'),
                            'name': result.get('name')
                        }
                    return None
        except Exception as e:
            logger.error(f"SeaweedFS upload failed: {e}")
            return None
    
    async def delete_file(self, fid: str) -> bool:
        """Delete file from SeaweedFS"""
        if not self.enabled:
            return False
        
        try:
            # Lookup volume server for this fid
            volume_id = fid.split(',')[0]
            
            async with aiohttp.ClientSession() as session:
                # Lookup
                async with session.get(
                    f"http://{self.master_url}/dir/lookup?volumeId={volume_id}",
                    timeout=5
                ) as response:
                    if response.status != 200:
                        return False
                    
                    data = await response.json()
                    locations = data.get('locations', [])
                    if not locations:
                        return False
                    
                    url = locations[0]['url']
                
                # Delete
                async with session.delete(
                    f"http://{url}/{fid}",
                    timeout=5
                ) as response:
                    return response.status == 200
        except Exception as e:
            logger.error(f"SeaweedFS delete failed: {e}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get SeaweedFS status"""
        return {
            'enabled': self.enabled,
            'available': self.available,
            'master': self.master_url if self.enabled else None
        }

seaweedfs_client = SeaweedFSClient()
