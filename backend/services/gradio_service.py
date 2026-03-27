"""
Gradio Integration Service - Instant AI UIs
"""
import logging
from typing import Dict, Any, Optional
import os

try:
    import gradio as gr
    GRADIO_AVAILABLE = True
except ImportError:
    GRADIO_AVAILABLE = False
    logging.warning("Gradio not available. Install with: pip install gradio")

logger = logging.getLogger(__name__)

class GradioService:
    """Gradio service for creating instant AI interfaces"""
    
    def __init__(self):
        self.available = GRADIO_AVAILABLE
        self.interfaces = {}
    
    def create_ai_chat_interface(self, model_fn):
        """Create a chat interface for AI models"""
        if not self.available:
            return None
        
        try:
            demo = gr.ChatInterface(
                fn=model_fn,
                title="NEXUS AI Chat",
                description="Chat with NEXUS AI assistants",
                examples=[
                    "Tell me about AI tools",
                    "Help me find a product",
                    "Generate an image"
                ]
            )
            self.interfaces['chat'] = demo
            return demo
        except Exception as e:
            logger.error(f"Failed to create chat interface: {e}")
            return None
    
    def create_image_generator_interface(self, generate_fn):
        """Create interface for image generation"""
        if not self.available:
            return None
        
        try:
            demo = gr.Interface(
                fn=generate_fn,
                inputs=[
                    gr.Textbox(label="Prompt", placeholder="Describe the image you want..."),
                    gr.Slider(minimum=1, maximum=10, value=1, step=1, label="Number of images")
                ],
                outputs=gr.Gallery(label="Generated Images"),
                title="NEXUS Image Generator",
                description="Generate images using AI"
            )
            self.interfaces['image_gen'] = demo
            return demo
        except Exception as e:
            logger.error(f"Failed to create image generator: {e}")
            return None
    
    def create_video_generator_interface(self, generate_fn):
        """Create interface for video generation"""
        if not self.available:
            return None
        
        try:
            demo = gr.Interface(
                fn=generate_fn,
                inputs=[
                    gr.Textbox(label="Prompt", placeholder="Describe the video..."),
                    gr.Dropdown(
                        choices=["sora", "runway"],
                        label="Provider",
                        value="sora"
                    ),
                    gr.Slider(minimum=3, maximum=10, value=5, step=1, label="Duration (seconds)")
                ],
                outputs=gr.Video(label="Generated Video"),
                title="NEXUS Video Generator",
                description="Generate videos using Sora 2 or Runway ML"
            )
            self.interfaces['video_gen'] = demo
            return demo
        except Exception as e:
            logger.error(f"Failed to create video generator: {e}")
            return None
    
    def create_object_detection_interface(self, detect_fn):
        """Create interface for object detection using YOLO"""
        if not self.available:
            return None
        
        try:
            demo = gr.Interface(
                fn=detect_fn,
                inputs=gr.Image(label="Upload Image", type="filepath"),
                outputs=[
                    gr.Image(label="Detected Objects"),
                    gr.JSON(label="Detection Results")
                ],
                title="NEXUS Object Detection",
                description="Detect objects in images using YOLO"
            )
            self.interfaces['object_detection'] = demo
            return demo
        except Exception as e:
            logger.error(f"Failed to create object detection interface: {e}")
            return None
    
    def mount_to_fastapi(self, app, path: str = "/gradio"):
        """Mount Gradio interfaces to FastAPI app"""
        if not self.available or not self.interfaces:
            logger.warning("No Gradio interfaces to mount")
            return
        
        try:
            # Create a combined interface with tabs
            with gr.Blocks() as demo:
                gr.Markdown("# NEXUS AI Studio")
                gr.Markdown("Instant AI interfaces for all your creative needs")
                
                with gr.Tabs():
                    for name, interface in self.interfaces.items():
                        with gr.TabItem(name.replace('_', ' ').title()):
                            interface.render()
            
            # Mount to FastAPI
            app = gr.mount_gradio_app(app, demo, path=path)
            logger.info(f"✓ Gradio interfaces mounted at {path}")
            return app
        except Exception as e:
            logger.error(f"Failed to mount Gradio: {e}")
            return app
    
    def get_status(self) -> Dict[str, Any]:
        """Get Gradio service status"""
        return {
            "available": self.available,
            "interfaces": list(self.interfaces.keys()),
            "interface_count": len(self.interfaces)
        }

gradio_service = GradioService()
