"""
Runway ML Video Generation Service
Supports multiple Runway models including Gen-3 Alpha and Gen-3 Alpha Turbo
"""
import logging
import os
import asyncio
import httpx
from typing import Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class RunwayVideoService:
    """Service for generating videos using Runway ML API"""
    
    def __init__(self):
        self.api_key = os.environ.get('RUNWAYML_API_KEY', '')
        self.base_url = "https://api.dev.runwayml.com/v1"
        self.output_dir = Path('/app/backend/generated_videos')
        self.output_dir.mkdir(exist_ok=True)
        
        # Available models
        self.models = {
            "gen3a_turbo": "gen3a_turbo",  # Fastest, 5-10s
            "gen3_alpha": "gen3_alpha"      # Higher quality, 5-10s
        }
    
    async def generate_video(
        self,
        prompt: str,
        model: str = "gen3a_turbo",
        duration: int = 5,
        aspect_ratio: str = "16:9",
        output_filename: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate video from text prompt using Runway ML
        
        Args:
            prompt: Text description of the video
            model: Model to use (gen3a_turbo or gen3_alpha)
            duration: Video duration (5 or 10 seconds)
            aspect_ratio: Video aspect ratio (e.g., "1280:720", "1920:1080", "1024:1024")
            output_filename: Optional custom filename
            
        Returns:
            Dict with success status, task_id, and generation info
        """
        try:
            if not self.api_key:
                return {
                    "success": False,
                    "error": "RUNWAYML_API_KEY not configured"
                }
            
            # Validate parameters
            if model not in self.models:
                return {
                    "success": False,
                    "error": f"Invalid model. Must be one of: {', '.join(self.models.keys())}"
                }
            
            if duration not in [5, 10]:
                return {
                    "success": False,
                    "error": "Duration must be 5 or 10 seconds"
                }
            
            # Prepare request
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "X-Runway-Version": "2024-11-06"
            }
            
            payload = {
                "model": self.models[model],
                "promptText": prompt,
                "duration": duration,
                "ratio": aspect_ratio,
                "watermark": False
            }
            
            logger.info(f"Generating video with Runway {model}: {prompt[:100]}")
            
            # Create generation task
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/image_to_video",
                    headers=headers,
                    json=payload
                )
                
                if response.status_code != 200:
                    error_detail = response.text
                    logger.error(f"Runway API error: {error_detail}")
                    return {
                        "success": False,
                        "error": f"API error: {error_detail}"
                    }
                
                data = response.json()
                task_id = data.get("id")
                
                if not task_id:
                    return {
                        "success": False,
                        "error": "No task ID returned from API"
                    }
                
                logger.info(f"✓ Runway task created: {task_id}")
                
                # Start polling in background
                asyncio.create_task(self._poll_and_download(task_id, output_filename))
                
                return {
                    "success": True,
                    "task_id": task_id,
                    "model": model,
                    "prompt": prompt,
                    "duration": duration,
                    "status": "processing"
                }
                
        except Exception as e:
            logger.error(f"Runway video generation error: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        Check the status of a Runway generation task
        
        Args:
            task_id: The task ID to check
            
        Returns:
            Dict with task status and video URL if complete
        """
        try:
            if not self.api_key:
                return {
                    "success": False,
                    "error": "RUNWAYML_API_KEY not configured"
                }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.base_url}/tasks/{task_id}",
                    headers=headers
                )
                
                if response.status_code != 200:
                    return {
                        "success": False,
                        "error": f"Failed to get status: {response.text}"
                    }
                
                data = response.json()
                status = data.get("status", "unknown")
                
                result = {
                    "success": True,
                    "task_id": task_id,
                    "status": status,
                    "progress": data.get("progress", 0)
                }
                
                # If completed, get video URL
                if status == "SUCCEEDED":
                    output = data.get("output", [])
                    if output and len(output) > 0:
                        video_url = output[0]
                        result["video_url"] = video_url
                        
                        # Check if we have it downloaded locally
                        local_path = self.output_dir / f"{task_id}.mp4"
                        if local_path.exists():
                            result["local_url"] = f"/generated_videos/{task_id}.mp4"
                
                elif status == "FAILED":
                    result["error"] = data.get("failure", "Generation failed")
                
                return result
                
        except Exception as e:
            logger.error(f"Error checking Runway task status: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _poll_and_download(
        self,
        task_id: str,
        output_filename: Optional[str] = None,
        max_wait: int = 600
    ):
        """
        Poll task status and download video when complete
        
        Args:
            task_id: Task ID to poll
            output_filename: Optional custom filename
            max_wait: Maximum time to wait in seconds
        """
        try:
            import time
            start_time = time.time()
            poll_interval = 5  # Poll every 5 seconds
            
            while (time.time() - start_time) < max_wait:
                status_result = await self.get_task_status(task_id)
                
                if not status_result.get("success"):
                    logger.error(f"Failed to get status for task {task_id}")
                    break
                
                status = status_result.get("status")
                
                if status == "SUCCEEDED":
                    video_url = status_result.get("video_url")
                    if video_url:
                        logger.info(f"✓ Runway video ready: {task_id}")
                        # Download video
                        await self._download_video(video_url, task_id, output_filename)
                    break
                
                elif status == "FAILED":
                    error = status_result.get("error", "Unknown error")
                    logger.error(f"✗ Runway generation failed for {task_id}: {error}")
                    break
                
                # Still processing
                await asyncio.sleep(poll_interval)
            
            if (time.time() - start_time) >= max_wait:
                logger.warning(f"⚠ Runway task {task_id} timeout after {max_wait}s")
                
        except Exception as e:
            logger.error(f"Error in polling task {task_id}: {str(e)}")
    
    async def _download_video(
        self,
        video_url: str,
        task_id: str,
        output_filename: Optional[str] = None
    ):
        """Download video from Runway URL and save locally"""
        try:
            if not output_filename:
                output_filename = task_id
            
            output_path = self.output_dir / f"{output_filename}.mp4"
            
            logger.info(f"Downloading Runway video: {task_id}")
            
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.get(video_url)
                
                if response.status_code == 200:
                    output_path.write_bytes(response.content)
                    logger.info(f"✓ Runway video saved: {output_path}")
                else:
                    logger.error(f"Failed to download video: HTTP {response.status_code}")
                    
        except Exception as e:
            logger.error(f"Error downloading video: {str(e)}")

# Create singleton instance
runway_video_service = RunwayVideoService()
