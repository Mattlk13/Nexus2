"""
File Upload routes - R2 storage integration
"""
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional, List
from datetime import datetime, timezone
import uuid
import logging

from services.file_storage_service import file_storage_service
from .dependencies import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Files"])

class FileMetadata(BaseModel):
    id: str
    filename: str
    content_type: str
    size: int
    storage_backend: str
    url: str
    uploaded_by: str
    uploaded_at: str

def get_files_router(db: AsyncIOMotorDatabase):
    """Create files router with dependencies"""
    
    @router.post("/files/upload")
    async def upload_file(
        file: UploadFile = File(...),
        folder: str = "uploads",
        current_user: dict = Depends(get_current_user)
    ):
        """Upload file to R2 storage"""
        try:
            # Read file data
            file_data = await file.read()
            
            # Upload to storage
            result = await file_storage_service.upload_file(
                file_data=file_data,
                filename=file.filename,
                content_type=file.content_type,
                folder=folder,
                metadata={
                    "uploaded_by": current_user["id"],
                    "username": current_user["username"]
                }
            )
            
            if not result.get("success"):
                raise HTTPException(status_code=500, detail=result.get("error", "Upload failed"))
            
            # Save metadata to database
            file_doc = {
                "id": result["file_id"],
                "filename": result["original_filename"],
                "content_type": result["content_type"],
                "size": result["size"],
                "storage_backend": result["backend"],
                "storage_key": result["storage_key"],
                "url": result["url"],
                "uploaded_by": current_user["id"],
                "uploaded_at": result["uploaded_at"],
                "folder": folder
            }
            await db.files.insert_one(file_doc)
            
            logger.info(f"✓ File uploaded: {file.filename} via {result['backend']}")
            
            return {k: v for k, v in file_doc.items() if k != "_id"}
        
        except Exception as e:
            logger.error(f"File upload failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.post("/files/upload-multiple")
    async def upload_multiple_files(
        files: List[UploadFile] = File(...),
        folder: str = "uploads",
        current_user: dict = Depends(get_current_user)
    ):
        """Upload multiple files"""
        uploaded_files = []
        errors = []
        
        for file in files:
            try:
                file_data = await file.read()
                
                result = await file_storage_service.upload_file(
                    file_data=file_data,
                    filename=file.filename,
                    content_type=file.content_type,
                    folder=folder,
                    metadata={"uploaded_by": current_user["id"]}
                )
                
                if result.get("success"):
                    file_doc = {
                        "id": result["file_id"],
                        "filename": result["original_filename"],
                        "content_type": result["content_type"],
                        "size": result["size"],
                        "storage_backend": result["backend"],
                        "storage_key": result["storage_key"],
                        "url": result["url"],
                        "uploaded_by": current_user["id"],
                        "uploaded_at": result["uploaded_at"]
                    }
                    await db.files.insert_one(file_doc)
                    uploaded_files.append({k: v for k, v in file_doc.items() if k != "_id"})
                else:
                    errors.append({"filename": file.filename, "error": result.get("error")})
            except Exception as e:
                errors.append({"filename": file.filename, "error": str(e)})
        
        return {
            "uploaded": uploaded_files,
            "errors": errors,
            "total": len(files),
            "successful": len(uploaded_files)
        }
    
    @router.get("/files/my-files")
    async def get_my_files(
        current_user: dict = Depends(get_current_user),
        limit: int = 50
    ):
        """Get user's uploaded files"""
        files = await db.files.find(
            {"uploaded_by": current_user["id"]},
            {"_id": 0}
        ).sort("uploaded_at", -1).limit(limit).to_list(limit)
        
        return files
    
    @router.get("/files/{file_id}")
    async def get_file_metadata(file_id: str):
        """Get file metadata"""
        file_doc = await db.files.find_one({"id": file_id}, {"_id": 0})
        if not file_doc:
            raise HTTPException(status_code=404, detail="File not found")
        return file_doc
    
    @router.delete("/files/{file_id}")
    async def delete_file(
        file_id: str,
        current_user: dict = Depends(get_current_user)
    ):
        """Delete file"""
        file_doc = await db.files.find_one({"id": file_id}, {"_id": 0})
        if not file_doc:
            raise HTTPException(status_code=404, detail="File not found")
        
        if file_doc["uploaded_by"] != current_user["id"] and current_user.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Permission denied")
        
        # Delete from storage
        success = await file_storage_service.delete_file(
            storage_key=file_doc["storage_key"],
            backend=file_doc["storage_backend"]
        )
        
        if success:
            # Delete from database
            await db.files.delete_one({"id": file_id})
            return {"success": True, "message": "File deleted"}
        else:
            raise HTTPException(status_code=500, detail="Failed to delete file from storage")
    
    @router.get("/files/storage/stats")
    async def get_storage_stats(current_user: dict = Depends(get_current_user)):
        """Get storage statistics"""
        # User stats
        user_files = await db.files.find({"uploaded_by": current_user["id"]}, {"_id": 0}).to_list(1000)
        total_size = sum(f.get("size", 0) for f in user_files)
        
        # Storage backend stats
        backend_stats = file_storage_service.get_storage_stats()
        
        return {
            "user_stats": {
                "total_files": len(user_files),
                "total_size_bytes": total_size,
                "total_size_mb": round(total_size / (1024 * 1024), 2)
            },
            "backend_stats": backend_stats
        }
    
    @router.get("/files/presigned-url")
    async def generate_presigned_url(
        filename: str,
        folder: str = "uploads",
        expires_in: int = 3600,
        current_user: dict = Depends(get_current_user)
    ):
        """Generate presigned URL for direct upload"""
        presigned_data = file_storage_service.generate_presigned_upload_url(
            filename=filename,
            folder=folder,
            expires_in=expires_in
        )
        
        if not presigned_data:
            raise HTTPException(status_code=500, detail="Failed to generate presigned URL")
        
        return presigned_data
    
    return router
