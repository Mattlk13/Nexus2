"""
File Upload Routes with Cloudflare R2 Integration
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from typing import List
import logging

from .dependencies import get_current_user
from services.cloudflare_r2_service import r2_service
from services.cloudflare_images_service import cloudflare_images

logger = logging.getLogger(__name__)
router = APIRouter(tags=["File Upload"])

def get_upload_router(db):
    """Create upload router with Cloudflare R2 integration"""
    
    @router.post("/upload/image")
    async def upload_image(
        file: UploadFile = File(...),
        current_user: dict = Depends(get_current_user)
    ):
        """Upload image to Cloudflare Images for optimization"""
        try:
            # Validate file type
            if not file.content_type.startswith('image/'):
                raise HTTPException(status_code=400, detail="File must be an image")
            
            # Read file data
            file_data = await file.read()
            
            # Upload to Cloudflare Images for automatic optimization
            result = await cloudflare_images.upload_image(
                file_data,
                file.filename,
                metadata={
                    'user_id': current_user['id'],
                    'username': current_user['username']
                }
            )
            
            if not result['success']:
                # Fallback to R2 if Cloudflare Images not configured
                result = await r2_service.upload_file(
                    file_data,
                    file.filename,
                    file.content_type,
                    folder='images'
                )
            
            # Save reference in database
            if result['success']:
                upload_doc = {
                    "id": result.get('image_id') or result.get('key'),
                    "user_id": current_user['id'],
                    "filename": file.filename,
                    "url": result.get('variants', {}).get('public') or result['url'],
                    "type": "image",
                    "service": "cloudflare_images" if 'image_id' in result else "r2",
                    "created_at": result.get('uploaded_at') or result.get('created_at')
                }
                await db.uploads.insert_one(upload_doc)
            
            return result
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Image upload failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.post("/upload/file")
    async def upload_file(
        file: UploadFile = File(...),
        folder: str = "uploads",
        current_user: dict = Depends(get_current_user)
    ):
        """Upload any file to Cloudflare R2"""
        try:
            # Read file data
            file_data = await file.read()
            
            # Validate file size (50MB limit)
            if len(file_data) > 50 * 1024 * 1024:
                raise HTTPException(status_code=400, detail="File too large (max 50MB)")
            
            # Upload to R2
            result = await r2_service.upload_file(
                file_data,
                file.filename,
                file.content_type,
                folder=folder
            )
            
            if not result['success']:
                raise HTTPException(status_code=500, detail=result.get('error'))
            
            # Save reference in database
            upload_doc = {
                "id": result['key'],
                "user_id": current_user['id'],
                "filename": file.filename,
                "url": result['url'],
                "type": file.content_type,
                "size": result['size'],
                "service": "r2",
                "created_at": result.get('created_at')
            }
            await db.uploads.insert_one(upload_doc)
            
            return result
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"File upload failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/uploads")
    async def get_user_uploads(
        current_user: dict = Depends(get_current_user)
    ):
        """Get all user's uploaded files"""
        try:
            uploads = await db.uploads.find(
                {"user_id": current_user['id']},
                {"_id": 0}
            ).sort("created_at", -1).to_list(100)
            
            return {"uploads": uploads}
            
        except Exception as e:
            logger.error(f"Failed to fetch uploads: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.delete("/uploads/{upload_id}")
    async def delete_upload(
        upload_id: str,
        current_user: dict = Depends(get_current_user)
    ):
        """Delete uploaded file"""
        try:
            # Get upload record
            upload = await db.uploads.find_one(
                {"id": upload_id, "user_id": current_user['id']},
                {"_id": 0}
            )
            
            if not upload:
                raise HTTPException(status_code=404, detail="Upload not found")
            
            # Delete from storage
            if upload['service'] == 'cloudflare_images':
                await cloudflare_images.delete_image(upload['id'])
            elif upload['service'] == 'r2':
                await r2_service.delete_file(upload['id'])
            
            # Delete from database
            await db.uploads.delete_one({"id": upload_id})
            
            return {"success": True, "message": "Upload deleted"}
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to delete upload: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    return router
