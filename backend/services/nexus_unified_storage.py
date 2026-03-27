"""
NEXUS Unified Storage Service
Multi-backend storage with automatic fallback: R2 → SeaweedFS → Local

Features:
- Primary: Cloudflare R2 (production)
- Backup: SeaweedFS (distributed storage)
- Fallback: Local filesystem
- Automatic failover
- Health monitoring
"""

import os
import logging
from typing import Dict, Optional
from datetime import datetime, timezone
from uuid import uuid4
from pathlib import Path

logger = logging.getLogger(__name__)

class UnifiedStorageService:
    def __init__(self):
        """Initialize multi-backend storage"""
        # Import backends
        from services.cloudflare_r2_service import r2_service
        from services.seaweedfs_client import seaweedfs_client
        
        self.r2 = r2_service
        self.seaweedfs = seaweedfs_client
        
        # Storage priority
        self.backends = ['r2', 'seaweedfs', 'local']
        self.local_path = Path(os.environ.get('LOCAL_STORAGE_PATH', '/app/storage'))
        self.local_path.mkdir(parents=True, exist_ok=True)
        
        logger.info("🗄️ Unified Storage initialized (R2 → SeaweedFS → Local)")
    
    async def upload_file(
        self, 
        file_data: bytes, 
        filename: str, 
        content_type: str,
        folder: str = 'uploads',
        preferred_backend: Optional[str] = None
    ) -> Dict:
        """
        Upload file with automatic backend selection and fallback
        
        Priority:
        1. Cloudflare R2 (production)
        2. SeaweedFS (backup/alternative)
        3. Local filesystem (fallback)
        """
        backends = [preferred_backend] if preferred_backend else self.backends
        
        for backend in backends:
            try:
                if backend == 'r2':
                    result = await self._upload_to_r2(file_data, filename, content_type, folder)
                    if result['success']:
                        return {**result, 'backend': 'r2'}
                
                elif backend == 'seaweedfs':
                    result = await self._upload_to_seaweedfs(file_data, filename, content_type)
                    if result and result.get('success'):
                        return {**result, 'backend': 'seaweedfs'}
                
                elif backend == 'local':
                    result = await self._upload_to_local(file_data, filename, content_type, folder)
                    if result['success']:
                        return {**result, 'backend': 'local'}
                        
            except Exception as e:
                logger.warning(f"{backend} upload failed: {e}, trying next backend...")
                continue
        
        return {
            "success": False,
            "error": "All storage backends failed"
        }
    
    async def _upload_to_r2(self, file_data: bytes, filename: str, content_type: str, folder: str) -> Dict:
        """Upload to Cloudflare R2"""
        try:
            result = await self.r2.upload_file(file_data, filename, content_type, folder)
            return result
        except Exception as e:
            logger.error(f"R2 upload failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _upload_to_seaweedfs(self, file_data: bytes, filename: str, content_type: str) -> Optional[Dict]:
        """Upload to SeaweedFS"""
        try:
            result = await self.seaweedfs.upload_file(file_data, filename, content_type)
            return result
        except Exception as e:
            logger.error(f"SeaweedFS upload failed: {e}")
            return None
    
    async def _upload_to_local(self, file_data: bytes, filename: str, content_type: str, folder: str) -> Dict:
        """Upload to local filesystem"""
        try:
            # Generate unique filename
            file_ext = filename.rsplit('.', 1)[-1] if '.' in filename else 'bin'
            unique_filename = f"{uuid4().hex}.{file_ext}"
            
            # Create folder
            folder_path = self.local_path / folder
            folder_path.mkdir(parents=True, exist_ok=True)
            
            # Write file
            file_path = folder_path / unique_filename
            file_path.write_bytes(file_data)
            
            return {
                "success": True,
                "url": f"/storage/{folder}/{unique_filename}",
                "key": f"{folder}/{unique_filename}",
                "filename": unique_filename,
                "original_filename": filename,
                "size": len(file_data),
                "content_type": content_type
            }
        except Exception as e:
            logger.error(f"Local storage upload failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_backend_status(self) -> Dict:
        """Check health of all storage backends"""
        status = {
            "r2": {
                "available": self.r2.client is not None,
                "priority": 1
            },
            "seaweedfs": {
                "available": self.seaweedfs.enabled and self.seaweedfs.available,
                "priority": 2
            },
            "local": {
                "available": self.local_path.exists(),
                "priority": 3,
                "path": str(self.local_path)
            }
        }
        
        return {
            "backends": status,
            "active_backends": sum(1 for b in status.values() if b['available']),
            "primary": "r2" if status['r2']['available'] else "seaweedfs" if status['seaweedfs']['available'] else "local"
        }

# Global instance
unified_storage = UnifiedStorageService()
