"""
NEXUS Hybrid: Groq Cloud
Ultra-fast LLM inference with Groq's LPU technology
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, List
import os
from dotenv import load_dotenv
import logging

load_dotenv()
logger = logging.getLogger(__name__)

class ChatRequest(BaseModel):
    message: str
    model: str = "llama-3.3-70b-versatile"
    temperature: float = 0.7

class GroqEngine:
    def __init__(self, db):
        self.db = db
        # Groq API key will be set up later (free tier)
        self.api_key = os.getenv('GROQ_API_KEY', 'demo_key_placeholder')
    
    def get_capabilities(self) -> Dict:
        return {
            "name": "Groq Cloud",
            "description": "Ultra-fast LLM inference (30x faster than GPT) using LPU hardware",
            "category": "llm_inference",
            "provider": "Groq",
            "models": [
                "llama-3.3-70b-versatile",
                "llama-3.3-70b-instruct",
                "mixtral-8x7b-32768",
                "gemma2-9b-it"
            ],
            "features": [
                "Near-instant responses (<1s)",
                "LPU (Language Processing Unit) hardware",
                "OpenAI-compatible API",
                "Free tier available",
                "Real-time streaming"
            ],
            "speed": "~500 tokens/second",
            "pricing": "Free tier + Pay-as-you-go",
            "status": "active",
            "setup_required": "API key from console.groq.com"
        }
    
    async def chat(self, request: ChatRequest) -> Dict:
        """Chat with Groq (demo response for now)"""
        try:
            if self.api_key == 'demo_key_placeholder':
                return {
                    "success": True,
                    "response": "[DEMO] Groq response would appear here. Set GROQ_API_KEY to enable.",
                    "model": request.model,
                    "note": "Visit console.groq.com to get free API key"
                }
            
            # Real Groq integration when API key is set
            from groq import Groq
            client = Groq(api_key=self.api_key)
            
            completion = client.chat.completions.create(
                model=request.model,
                messages=[{"role": "user", "content": request.message}],
                temperature=request.temperature
            )
            
            return {
                "success": True,
                "response": completion.choices[0].message.content,
                "model": request.model
            }
        except Exception as e:
            logger.error(f"Groq chat error: {e}")
            return {
                "success": False,
                "error": str(e),
                "note": "Ensure GROQ_API_KEY is set in .env"
            }

def create_groq_engine(db):
    return GroqEngine(db)

# Create global instance for ultimate controller
hybrid_groq = None
def init_hybrid(db):
    global hybrid_groq
    hybrid_groq = create_groq_engine(db)
    return hybrid_groq

def register_routes(db, get_current_user, require_admin):
    router = APIRouter(tags=["Groq"])
    engine = create_groq_engine(db)
    
    @router.get("/capabilities")
    async def get_capabilities():
        return engine.get_capabilities()
    
    @router.post("/chat")
    async def chat(request: ChatRequest):
        return await engine.chat(request)
    
    return router
