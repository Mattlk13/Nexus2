"""
Cloudflare R2 Storage Service
S3-compatible object storage for NEXUS file uploads

Features:
- User profile images
- AI-generated content storage
- Marketplace product files
- Zero egress fees
"""

import boto3
from botocore.client import Config
import os
import logging
from datetime import datetime, timezone
from uuid import uuid4

logger = logging.getLogger(__name__)

class CloudflareR2Service:
    def __init__(self):
        """Initialize Cloudflare R2 client (S3-compatible) - uses lazy loading"""
        self._client = None
        self._initialized = False
    
    def _ensure_initialized(self):
        """Lazy initialization - only runs when first needed"""
        if self._initialized:
            return
        
        self._initialized = True
        self.endpoint_url = os.environ.get('R2_ENDPOINT_URL') or os.environ.get('R2_ENDPOINT')
        self.access_key = os.environ.get('R2_ACCESS_KEY_ID')
        self.secret_key = os.environ.get('R2_SECRET_ACCESS_KEY')
        self.bucket_name = os.environ.get('R2_BUCKET_NAME', 'nexus-storage')
        self.public_url = os.environ.get('R2_PUBLIC_URL', '')
        
        if not all([self.endpoint_url, self.access_key, self.secret_key]):
            logger.warning("R2 credentials not configured. File uploads will use local storage.")
            self._client = None
            return
        
        # Initialize S3 client for R2
        self._client = boto3.client(
            's3',
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            config=Config(signature_version='s3v4'),
            region_name='auto'
        )
        
        logger.info(f"✅ Cloudflare R2 initialized: {self.bucket_name}")
    
    @property
    def client(self):
        """Lazy-loaded client property"""
        self._ensure_initialized()
        return self._client
    
    async def upload_file(self, file_data: bytes, filename: str, content_type: str, folder: str = 'uploads') -> dict:
        """
        Upload file to R2
        
        Args:
            file_data: File bytes
            filename: Original filename
            content_type: MIME type
            folder: Folder in bucket (uploads, generated, products, etc.)
        
        Returns:
            dict with url and metadata
        """
        if not self.client:
            raise Exception("R2 not configured")
        
        try:
            # Generate unique filename
            file_ext = filename.rsplit('.', 1)[-1] if '.' in filename else 'bin'
            unique_filename = f"{uuid4().hex}.{file_ext}"
            key = f"{folder}/{unique_filename}"
            
            # Upload to R2
            self.client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=file_data,
                ContentType=content_type,
                Metadata={
                    'original_filename': filename,
                    'uploaded_at': datetime.now(timezone.utc).isoformat()
                }
            )
            
            # Generate public URL
            file_url = f"{self.public_url}/{key}" if self.public_url else f"{self.endpoint_url}/{self.bucket_name}/{key}"
            
            logger.info(f"Uploaded to R2: {key}")
            
            return {
                "success": True,
                "url": file_url,
                "key": key,
                "filename": unique_filename,
                "original_filename": filename,
                "size": len(file_data),
                "content_type": content_type
            }
            
        except Exception as e:
            logger.error(f"R2 upload failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def delete_file(self, key: str) -> bool:
        """Delete file from R2"""
        if not self.client:
            return False
        
        try:
            self.client.delete_object(
                Bucket=self.bucket_name,
                Key=key
            )
            logger.info(f"Deleted from R2: {key}")
            return True
        except Exception as e:
            logger.error(f"R2 delete failed: {e}")
            return False
    
    async def get_file_url(self, key: str, expires_in: int = 3600) -> str:
        """Generate presigned URL for private files"""
        if not self.client:
            return ""
        
        try:
            url = self.client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': key
                },
                ExpiresIn=expires_in
            )
            return url
        except Exception as e:
            logger.error(f"Failed to generate presigned URL: {e}")
            return ""
    
    async def list_files(self, folder: str = '', limit: int = 100) -> list:
        """List files in bucket/folder"""
        if not self.client:
            return []
        
        try:
            response = self.client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=folder,
                MaxKeys=limit
            )
            
            files = []
            for obj in response.get('Contents', []):
                files.append({
                    'key': obj['Key'],
                    'size': obj['Size'],
                    'last_modified': obj['LastModified'].isoformat(),
                    'url': f"{self.public_url}/{obj['Key']}" if self.public_url else None
                })
            
            return files
            
        except Exception as e:
            logger.error(f"Failed to list R2 files: {e}")
            return []

# Global instance
r2_service = CloudflareR2Service()
