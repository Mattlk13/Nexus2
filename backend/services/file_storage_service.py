"""
Unified File Storage Service for NEXUS
Supports multiple storage backends: Cloudflare R2, SeaweedFS, Local
"""
import os
import logging
import uuid
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError
from typing import Dict, Any, Optional, BinaryIO
from datetime import datetime, timezone
from pathlib import Path
import aiofiles

logger = logging.getLogger(__name__)

class FileStorageService:
    """Unified interface for file storage across multiple backends"""
    
    def __init__(self):
        self.backend = os.environ.get('STORAGE_BACKEND', 'r2')  # r2, seaweedfs, local
        self._initialize_backends()
    
    def _initialize_backends(self):
        """Initialize all configured storage backends"""
        # Cloudflare R2 (S3-compatible)
        self.r2_client = None
        if self.backend == 'r2' or os.environ.get('R2_ENABLED', 'true').lower() == 'true':
            try:
                self.r2_client = boto3.client(
                    's3',
                    region_name='auto',
                    endpoint_url=self._get_r2_endpoint(),
                    aws_access_key_id=os.environ.get('R2_ACCESS_KEY_ID'),
                    aws_secret_access_key=os.environ.get('R2_SECRET_ACCESS_KEY'),
                    config=Config(
                        max_pool_connections=50,
                        retries={'max_attempts': 3, 'mode': 'adaptive'}
                    )
                )
                self.r2_bucket = os.environ.get('R2_BUCKET_NAME', 'nexus-storage')
                logger.info(f"✓ Cloudflare R2 initialized: {self.r2_bucket}")
            except Exception as e:
                logger.warning(f"R2 initialization failed: {e}. Falling back to local storage.")
                self.r2_client = None
        
        # SeaweedFS client (will be integrated)
        self.seaweedfs_client = None
        if self.backend == 'seaweedfs' or os.environ.get('SEAWEEDFS_ENABLED', 'false').lower() == 'true':
            self.seaweedfs_master = os.environ.get('SEAWEEDFS_MASTER', 'localhost:9333')
            logger.info(f"SeaweedFS backend prepared: {self.seaweedfs_master}")
        
        # Local storage fallback
        self.local_storage_path = Path(os.environ.get('LOCAL_STORAGE_PATH', '/app/storage'))
        self.local_storage_path.mkdir(parents=True, exist_ok=True)
    
    def _get_r2_endpoint(self) -> str:
        """Get R2 endpoint URL from Cloudflare account ID"""
        account_id = os.environ.get('CLOUDFLARE_ACCOUNT_ID', '')
        return f"https://{account_id}.r2.cloudflarestorage.com"
    
    async def upload_file(
        self,
        file_data: bytes,
        filename: str,
        content_type: str = 'application/octet-stream',
        folder: str = 'uploads',
        metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Upload file to configured storage backend
        
        Args:
            file_data: File bytes
            filename: Original filename
            content_type: MIME type
            folder: Storage folder/prefix
            metadata: Additional metadata
        
        Returns:
            Dict with storage info: {file_id, url, backend, size, ...}
        """
        file_id = str(uuid.uuid4())
        file_extension = Path(filename).suffix
        storage_key = f"{folder}/{file_id}{file_extension}"
        
        result = {
            'file_id': file_id,
            'original_filename': filename,
            'content_type': content_type,
            'size': len(file_data),
            'uploaded_at': datetime.now(timezone.utc).isoformat(),
            'folder': folder
        }
        
        # Try R2 first
        if self.r2_client:
            try:
                self.r2_client.put_object(
                    Bucket=self.r2_bucket,
                    Key=storage_key,
                    Body=file_data,
                    ContentType=content_type,
                    Metadata=metadata or {}
                )
                
                result.update({
                    'backend': 'r2',
                    'storage_key': storage_key,
                    'url': f"https://{self.r2_bucket}.r2.cloudflarestorage.com/{storage_key}",
                    'public_url': f"https://pub.r2.dev/{storage_key}",  # If public bucket
                    'success': True
                })
                logger.info(f"✓ File uploaded to R2: {storage_key}")
                return result
            except ClientError as e:
                logger.error(f"R2 upload failed: {e}. Trying fallback...")
        
        # Try SeaweedFS (if enabled)
        if self.seaweedfs_client:
            try:
                # SeaweedFS upload implementation (to be added)
                pass
            except Exception as e:
                logger.error(f"SeaweedFS upload failed: {e}. Trying fallback...")
        
        # Fallback to local storage
        try:
            local_file_path = self.local_storage_path / folder / f"{file_id}{file_extension}"
            local_file_path.parent.mkdir(parents=True, exist_ok=True)
            
            async with aiofiles.open(local_file_path, 'wb') as f:
                await f.write(file_data)
            
            result.update({
                'backend': 'local',
                'storage_key': str(local_file_path.relative_to(self.local_storage_path)),
                'path': str(local_file_path),
                'url': f"/api/files/{file_id}{file_extension}",
                'success': True
            })
            logger.info(f"✓ File uploaded to local storage: {local_file_path}")
            return result
        except Exception as e:
            logger.error(f"All storage backends failed: {e}")
            result.update({
                'backend': 'failed',
                'error': str(e),
                'success': False
            })
            return result
    
    async def get_file(self, file_id: str, storage_key: str, backend: str = 'r2') -> Optional[bytes]:
        """Retrieve file from storage"""
        if backend == 'r2' and self.r2_client:
            try:
                response = self.r2_client.get_object(
                    Bucket=self.r2_bucket,
                    Key=storage_key
                )
                return response['Body'].read()
            except ClientError as e:
                logger.error(f"R2 get failed: {e}")
                return None
        
        elif backend == 'local':
            try:
                local_path = self.local_storage_path / storage_key
                async with aiofiles.open(local_path, 'rb') as f:
                    return await f.read()
            except Exception as e:
                logger.error(f"Local get failed: {e}")
                return None
        
        return None
    
    async def delete_file(self, storage_key: str, backend: str = 'r2') -> bool:
        """Delete file from storage"""
        if backend == 'r2' and self.r2_client:
            try:
                self.r2_client.delete_object(
                    Bucket=self.r2_bucket,
                    Key=storage_key
                )
                logger.info(f"✓ File deleted from R2: {storage_key}")
                return True
            except ClientError as e:
                logger.error(f"R2 delete failed: {e}")
                return False
        
        elif backend == 'local':
            try:
                local_path = self.local_storage_path / storage_key
                local_path.unlink(missing_ok=True)
                logger.info(f"✓ File deleted from local: {storage_key}")
                return True
            except Exception as e:
                logger.error(f"Local delete failed: {e}")
                return False
        
        return False
    
    def generate_presigned_upload_url(
        self,
        filename: str,
        folder: str = 'uploads',
        expires_in: int = 3600
    ) -> Optional[Dict[str, Any]]:
        """Generate presigned URL for direct client upload (R2 only)"""
        if not self.r2_client:
            return None
        
        try:
            file_id = str(uuid.uuid4())
            file_extension = Path(filename).suffix
            storage_key = f"{folder}/{file_id}{file_extension}"
            
            presigned_data = self.r2_client.generate_presigned_post(
                Bucket=self.r2_bucket,
                Key=storage_key,
                ExpiresIn=expires_in
            )
            
            return {
                'file_id': file_id,
                'storage_key': storage_key,
                'presigned_url': presigned_data['url'],
                'fields': presigned_data['fields'],
                'expires_in': expires_in
            }
        except ClientError as e:
            logger.error(f"Presigned URL generation failed: {e}")
            return None
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage backend status and statistics"""
        stats = {
            'active_backend': self.backend,
            'backends': {
                'r2': {
                    'available': self.r2_client is not None,
                    'bucket': self.r2_bucket if self.r2_client else None
                },
                'seaweedfs': {
                    'available': self.seaweedfs_client is not None,
                    'master': self.seaweedfs_master if hasattr(self, 'seaweedfs_master') else None
                },
                'local': {
                    'available': True,
                    'path': str(self.local_storage_path)
                }
            }
        }
        return stats


# Singleton instance
file_storage_service = FileStorageService()
