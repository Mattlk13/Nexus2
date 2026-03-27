"""
Elite Integrations Router - All Hybrid Services
"""
from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

from services.hybrid_analytics_service import hybrid_analytics
from services.omnipay_gateway import omnipay, PaymentMethod
from services.cloudstack_service import cloudstack
from .dependencies import get_current_user, require_admin

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Elite Integrations"])

# ==================== HYBRID ANALYTICS ====================

class AnalyticsEventRequest(BaseModel):
    event_type: str
    properties: Dict[str, Any]
    user_id: Optional[str] = None
    session_id: Optional[str] = None

@router.post("/analytics/track")
async def track_analytics_event(
    event: AnalyticsEventRequest,
    current_user: dict = Depends(get_current_user)
):
    """Track event to hybrid analytics (Matomo + Plausible + Real-time)"""
    success = await hybrid_analytics.track_event(
        event_type=event.event_type,
        properties=event.properties,
        user_id=event.user_id or current_user.get("id"),
        session_id=event.session_id
    )
    
    return {
        "success": success,
        "tracked_to": ["matomo", "plausible", "realtime"]
    }

@router.get("/analytics/realtime")
async def get_realtime_analytics(
    minutes: int = 5,
    current_user: dict = Depends(require_admin)
):
    """Get real-time analytics dashboard data"""
    stats = await hybrid_analytics.get_realtime_stats(minutes)
    return stats

@router.get("/analytics/comprehensive")
async def get_comprehensive_analytics(
    start_date: str,
    end_date: str,
    current_user: dict = Depends(require_admin)
):
    """Get comprehensive analytics from all sources"""
    report = await hybrid_analytics.get_comprehensive_report(start_date, end_date)
    return report

# ==================== OMNIPAY GATEWAY ====================

class PaymentRequest(BaseModel):
    amount: float
    currency: str = "USD"
    payment_method: str
    order_id: str
    customer_email: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

@router.post("/payments/create")
async def create_payment(
    payment: PaymentRequest,
    current_user: dict = Depends(get_current_user)
):
    """Create payment using OmniPay (supports all payment methods)"""
    try:
        payment_method_enum = PaymentMethod(payment.payment_method)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid payment method: {payment.payment_method}")
    
    result = await omnipay.create_payment(
        amount=payment.amount,
        currency=payment.currency,
        payment_method=payment_method_enum,
        order_id=payment.order_id,
        customer_email=payment.customer_email or current_user.get("email"),
        metadata=payment.metadata or {}
    )
    
    if not result.get("success"):
        raise HTTPException(status_code=500, detail=result.get("error"))
    
    return result

@router.get("/payments/methods")
async def get_available_payment_methods():
    """Get list of available payment methods"""
    methods = omnipay.get_available_methods()
    return {
        "available_methods": [m.value for m in methods],
        "count": len(methods)
    }

@router.post("/payments/verify/{payment_id}")
async def verify_payment(
    payment_id: str,
    processor: str,
    current_user: dict = Depends(get_current_user)
):
    """Verify payment status"""
    result = await omnipay.verify_payment(payment_id, processor)
    return result

# ==================== CLOUDSTACK (CLOUDFLARE SUITE) ====================

class ImageClassificationRequest(BaseModel):
    image_url: str

class ImageGenerationRequest(BaseModel):
    prompt: str
    model: str = "@cf/stabilityai/stable-diffusion-xl-base-1.0"

class ImageOptimizationRequest(BaseModel):
    image_url: str
    width: Optional[int] = None
    height: Optional[int] = None
    quality: str = "auto"
    format: str = "auto"

class VideoUploadRequest(BaseModel):
    video_url: str
    metadata: Optional[Dict[str, Any]] = None

@router.post("/cloudstack/image/classify")
async def classify_image(
    request: ImageClassificationRequest,
    current_user: dict = Depends(get_current_user)
):
    """Classify image using Cloudflare Workers AI"""
    result = await cloudstack.classify_image(request.image_url)
    return result

@router.post("/cloudstack/image/generate")
async def generate_image(
    request: ImageGenerationRequest,
    current_user: dict = Depends(get_current_user)
):
    """Generate image using Cloudflare Workers AI"""
    result = await cloudstack.generate_image_from_text(
        prompt=request.prompt,
        model=request.model
    )
    return result

@router.post("/cloudstack/image/describe")
async def describe_image(
    request: ImageClassificationRequest,
    current_user: dict = Depends(get_current_user)
):
    """Generate description for image"""
    result = await cloudstack.describe_image(request.image_url)
    return result

@router.post("/cloudstack/image/optimize")
async def optimize_image(
    request: ImageOptimizationRequest,
    current_user: dict = Depends(get_current_user)
):
    """Optimize image using Cloudflare Images"""
    result = await cloudstack.optimize_image(
        image_url=request.image_url,
        width=request.width,
        height=request.height,
        quality=request.quality,
        format=request.format
    )
    return result

@router.post("/cloudstack/image/remove-background")
async def remove_background(
    request: ImageClassificationRequest,
    current_user: dict = Depends(get_current_user)
):
    """Remove background from image"""
    result = await cloudstack.remove_background(request.image_url)
    return result

@router.post("/cloudstack/video/upload")
async def upload_video(
    request: VideoUploadRequest,
    current_user: dict = Depends(get_current_user)
):
    """Upload video to Cloudflare Stream"""
    result = await cloudstack.upload_video(
        video_url=request.video_url,
        metadata=request.metadata
    )
    return result

@router.get("/cloudstack/video/analytics/{video_id}")
async def get_video_analytics(
    video_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get video analytics"""
    result = await cloudstack.get_video_analytics(video_id)
    return result

@router.get("/cloudstack/status")
async def get_cloudstack_status(current_user: dict = Depends(require_admin)):
    """Get CloudStack service status"""
    return {
        "workers_ai": {
            "enabled": cloudstack.workers_ai_enabled,
            "models": [
                "resnet-50 (classification)",
                "stable-diffusion-xl (text-to-image)",
                "uform-gen2-qwen (image-to-text)"
            ]
        },
        "r2_storage": {
            "enabled": cloudstack.r2_enabled
        },
        "images": {
            "enabled": True,
            "features": ["optimization", "smart-crop", "background-removal"]
        },
        "stream": {
            "enabled": True,
            "features": ["video-hosting", "analytics"]
        }
    }

def get_elite_integrations_router():
    """Return the elite integrations router"""
    return router
