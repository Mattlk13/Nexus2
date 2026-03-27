"""
YOLO Object Detection Service using Ultralytics
"""
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
import os

try:
    from ultralytics import YOLO
    import cv2
    import numpy as np
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    logging.warning("YOLO not available. Install with: pip install ultralytics opencv-python")

logger = logging.getLogger(__name__)

class YOLOService:
    """YOLO object detection and image analysis service"""
    
    def __init__(self):
        self.available = YOLO_AVAILABLE
        self.model = None
        self.model_name = "yolov8n.pt"  # Nano model for speed
        
        if self.available:
            self._load_model()
    
    def _load_model(self):
        """Load YOLO model"""
        try:
            self.model = YOLO(self.model_name)
            logger.info(f"✓ YOLO model loaded: {self.model_name}")
        except Exception as e:
            logger.error(f"YOLO model loading failed: {e}")
            self.available = False
    
    async def detect_objects(self, image_path: str, confidence: float = 0.25) -> Dict[str, Any]:
        """Detect objects in an image"""
        if not self.available or not self.model:
            return {
                "success": False,
                "error": "YOLO not available"
            }
        
        try:
            # Run inference
            results = self.model(image_path, conf=confidence)
            
            # Parse results
            detections = []
            for r in results:
                boxes = r.boxes
                for box in boxes:
                    detection = {
                        "class": self.model.names[int(box.cls[0])],
                        "confidence": float(box.conf[0]),
                        "bbox": box.xyxy[0].tolist()  # [x1, y1, x2, y2]
                    }
                    detections.append(detection)
            
            return {
                "success": True,
                "detections": detections,
                "count": len(detections),
                "image": image_path
            }
        except Exception as e:
            logger.error(f"Object detection failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def detect_and_annotate(self, image_path: str, output_path: str, confidence: float = 0.25) -> Dict[str, Any]:
        """Detect objects and save annotated image"""
        if not self.available or not self.model:
            return {
                "success": False,
                "error": "YOLO not available"
            }
        
        try:
            # Run inference
            results = self.model(image_path, conf=confidence)
            
            # Save annotated image
            annotated = results[0].plot()
            cv2.imwrite(output_path, annotated)
            
            # Parse detections
            detections = []
            boxes = results[0].boxes
            for box in boxes:
                detection = {
                    "class": self.model.names[int(box.cls[0])],
                    "confidence": float(box.conf[0])
                }
                detections.append(detection)
            
            return {
                "success": True,
                "detections": detections,
                "count": len(detections),
                "annotated_image": output_path
            }
        except Exception as e:
            logger.error(f"Annotation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def analyze_video(self, video_path: str, output_path: str, confidence: float = 0.25) -> Dict[str, Any]:
        """Analyze video and detect objects"""
        if not self.available or not self.model:
            return {
                "success": False,
                "error": "YOLO not available"
            }
        
        try:
            # Run inference on video
            results = self.model(video_path, conf=confidence, stream=True)
            
            # Process frames
            total_detections = 0
            unique_classes = set()
            
            for r in results:
                boxes = r.boxes
                total_detections += len(boxes)
                for box in boxes:
                    class_name = self.model.names[int(box.cls[0])]
                    unique_classes.add(class_name)
            
            return {
                "success": True,
                "total_detections": total_detections,
                "unique_objects": list(unique_classes),
                "video": video_path
            }
        except Exception as e:
            logger.error(f"Video analysis failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_status(self) -> Dict[str, Any]:
        """Get YOLO service status"""
        return {
            "available": self.available,
            "model": self.model_name if self.available else None,
            "classes": len(self.model.names) if self.available and self.model else 0
        }

yolo_service = YOLOService()
