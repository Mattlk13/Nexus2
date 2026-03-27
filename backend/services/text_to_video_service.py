import logging
import os
import asyncio
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from emergentintegrations.llm.openai.video_generation import OpenAIVideoGeneration
import base64
from pathlib import Path

load_dotenv()

logger = logging.getLogger(__name__)

class TextToVideoService:
    """Service for generating videos from text prompts using Sora 2"""
    
    def __init__(self):
        self.api_key = os.environ.get('EMERGENT_LLM_KEY', '')
        self.output_dir = Path('/app/backend/generated_videos')
        self.output_dir.mkdir(exist_ok=True)
        
    async def generate_video(
        self, 
        prompt: str, 
        model: str = "sora-2",
        size: str = "1280x720",
        duration: int = 4,
        output_filename: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate video from text prompt using Sora 2
        
        Args:
            prompt: Text description of the video to generate
            model: "sora-2" (default) or "sora-2-pro"
            size: Video resolution - "1280x720", "1792x1024", "1024x1792", or "1024x1024"
            duration: Video duration in seconds - 4, 8, or 12
            output_filename: Optional custom filename (without extension)
            
        Returns:
            Dict with success status, video path, and metadata
        """
        try:
            if not self.api_key:
                return {
                    "success": False,
                    "error": "EMERGENT_LLM_KEY not configured"
                }
            
            # Validate parameters
            valid_sizes = ["1280x720", "1792x1024", "1024x1792", "1024x1024"]
            valid_durations = [4, 8, 12]
            valid_models = ["sora-2", "sora-2-pro"]
            
            if size not in valid_sizes:
                return {
                    "success": False,
                    "error": f"Invalid size. Must be one of: {', '.join(valid_sizes)}"
                }
            
            if duration not in valid_durations:
                return {
                    "success": False,
                    "error": f"Invalid duration. Must be one of: {', '.join(map(str, valid_durations))}"
                }
            
            if model not in valid_models:
                return {
                    "success": False,
                    "error": f"Invalid model. Must be one of: {', '.join(valid_models)}"
                }
            
            # Generate unique filename if not provided
            if not output_filename:
                import uuid
                output_filename = f"video_{uuid.uuid4().hex[:8]}"
            
            output_path = self.output_dir / f"{output_filename}.mp4"
            
            logger.info(f"Generating video with Sora 2: {model}, {size}, {duration}s")
            
            # Run generation in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            video_bytes = await loop.run_in_executor(
                None,
                self._generate_sync,
                prompt,
                model,
                size,
                duration
            )
            
            if not video_bytes:
                return {
                    "success": False,
                    "error": "Video generation failed - no data returned"
                }
            
            # Save video file
            with open(output_path, 'wb') as f:
                f.write(video_bytes)
            
            logger.info(f"✓ Video generated successfully: {output_path}")
            
            # Return relative path for serving
            relative_path = f"/generated_videos/{output_filename}.mp4"
            
            return {
                "success": True,
                "video_path": str(output_path),
                "video_url": relative_path,
                "model": model,
                "size": size,
                "duration": duration,
                "prompt": prompt
            }
            
        except Exception as e:
            logger.error(f"Video generation error: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _generate_sync(self, prompt: str, model: str, size: str, duration: int) -> Optional[bytes]:
        """Synchronous video generation (runs in thread pool)"""
        try:
            # Create new instance for each request
            video_gen = OpenAIVideoGeneration(api_key=self.api_key)
            
            # Adjust max_wait_time based on duration and model
            max_wait_time = 600  # 10 minutes default
            if duration >= 8 or model == "sora-2-pro":
                max_wait_time = 900  # 15 minutes for longer/pro videos
            
            video_bytes = video_gen.text_to_video(
                prompt=prompt,
                model=model,
                size=size,
                duration=duration,
                max_wait_time=max_wait_time
            )
            
            return video_bytes
            
        except Exception as e:
            logger.error(f"Sync video generation failed: {str(e)}")
            return None

# Create singleton instance
text_to_video_service = TextToVideoService()
