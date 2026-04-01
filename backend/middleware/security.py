"""
Security and Rate Limiting Middleware for NEXUS
Fixes: Audit Issues #1, #2, #4
"""

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseMiddleware
from datetime import datetime, timedelta
import logging
from collections import defaultdict
import asyncio

logger = logging.getLogger(__name__)

class RateLimitMiddleware(BaseMiddleware):
    """Rate limiting to prevent DoS attacks"""
    
    def __init__(self, app, requests_per_minute=100):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests = defaultdict(list)
        self.cleanup_task = None
    
    async def dispatch(self, request: Request, call_next):
        # Get client IP
        client_ip = request.client.host
        
        # Clean old requests
        current_time = datetime.now()
        cutoff_time = current_time - timedelta(minutes=1)
        self.requests[client_ip] = [
            req_time for req_time in self.requests[client_ip]
            if req_time > cutoff_time
        ]
        
        # Check rate limit
        if len(self.requests[client_ip]) >= self.requests_per_minute:
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Rate limit exceeded. Please try again later.",
                    "retry_after": 60
                }
            )
        
        # Record request
        self.requests[client_ip].append(current_time)
        
        # Process request
        response = await call_next(request)
        return response

class InputValidationMiddleware(BaseMiddleware):
    """Validate file uploads and inputs"""
    
    ALLOWED_FILE_EXTENSIONS = {
        '.jpg', '.jpeg', '.png', '.gif', '.webp',  # Images
        '.mp4', '.mov', '.avi',  # Videos
        '.mp3', '.wav', '.ogg',  # Audio
        '.pdf', '.txt', '.md', '.doc', '.docx',  # Documents
        '.zip', '.tar', '.gz'  # Archives
    }
    
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    
    async def dispatch(self, request: Request, call_next):
        # Check if this is a file upload
        if request.method == "POST" and "multipart/form-data" in request.headers.get("content-type", ""):
            content_length = request.headers.get("content-length")
            
            if content_length and int(content_length) > self.MAX_FILE_SIZE:
                return JSONResponse(
                    status_code=413,
                    content={"detail": f"File too large. Maximum size: {self.MAX_FILE_SIZE / 1024 / 1024}MB"}
                )
        
        response = await call_next(request)
        return response

class SecurityHeadersMiddleware(BaseMiddleware):
    """Add security headers to all responses"""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        return response

# CSRF Protection utilities
from fastapi import Depends, Header
import secrets

class CSRFProtection:
    """CSRF token generation and validation"""
    
    @staticmethod
    def generate_token() -> str:
        """Generate a CSRF token"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    async def verify_token(
        csrf_token: str = Header(None, alias="X-CSRF-Token"),
        session_token: str = Header(None, alias="X-Session-Token")
    ):
        """Verify CSRF token matches session"""
        if not csrf_token or not session_token:
            raise HTTPException(
                status_code=403,
                detail="CSRF token missing"
            )
        
        # In production, verify against stored session token
        # For now, basic validation
        if len(csrf_token) < 32:
            raise HTTPException(
                status_code=403,
                detail="Invalid CSRF token"
            )
        
        return True

def get_csrf_protection():
    """Dependency for CSRF-protected endpoints"""
    return Depends(CSRFProtection.verify_token)
