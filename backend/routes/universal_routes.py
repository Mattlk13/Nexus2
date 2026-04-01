"""
NEXUS Universal Agent Routes
API endpoints for the Universal Omni-Agent
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Optional
import logging
from services.universal_router_service import (
    create_universal_router_service,
    UniversalRequest,
    UniversalResponse
)
from routes.dependencies import get_optional_user

logger = logging.getLogger(__name__)

def create_universal_routes(db):
    """Create Universal Agent router with all endpoints"""
    router = APIRouter(prefix="/api/universal", tags=["Universal Agent"])
    
    # Initialize service
    universal_service = create_universal_router_service(db)
    
    @router.post("/process", response_model=UniversalResponse)
    async def process_universal_request(
        request: UniversalRequest,
        current_user: Optional[Dict] = Depends(get_optional_user)
    ):
        """
        Universal Agent endpoint - processes ANY user request
        
        - Classifies intent using GPT-5.1
        - Routes to appropriate hybrid service
        - Returns unified response
        """
        try:
            # Add user_id if authenticated
            if current_user:
                request.user_id = current_user.get("id")
            
            # Process the request
            response = await universal_service.process_request(request)
            return response
            
        except Exception as e:
            logger.error(f"Universal agent processing error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/services")
    async def get_available_services():
        """
        Get list of all available services that can be routed to
        """
        return universal_service.get_available_services()
    
    @router.get("/history/{session_id}")
    async def get_conversation_history(
        session_id: str,
        limit: int = 50,
        current_user: Optional[Dict] = Depends(get_optional_user)
    ):
        """
        Retrieve conversation history for a session
        """
        try:
            history = await universal_service.get_conversation_history(session_id, limit)
            return {
                "session_id": session_id,
                "total": len(history),
                "conversations": history
            }
        except Exception as e:
            logger.error(f"Failed to retrieve history: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/status")
    async def get_status():
        """
        Get Universal Agent status
        """
        return {
            "status": "active",
            "name": "NEXUS Universal Omni-Agent",
            "description": "AI that routes ANY request to 44+ specialized services",
            "total_services": len(universal_service.service_map),
            "llm_model": "GPT-5.1 (Emergent Universal Key)",
            "capabilities": [
                "Intent Classification",
                "Smart Routing",
                "Multi-Service Orchestration",
                "Conversation History"
            ]
        }
    
    return router
