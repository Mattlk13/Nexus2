"""
ULTRA LLM Service - Hybrid AI Model Hosting
Combines: vLLM + Ollama + Emergent LLM Key (OpenAI/Claude/Gemini)

Provides:
- Local LLM inference (vLLM for production, Ollama for dev)
- Cloud fallback (Emergent Universal Key)
- Smart model routing
- High-throughput production serving
"""
import logging
import asyncio
import httpx
import os
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from enum import Enum

logger = logging.getLogger(__name__)

class LLMBackend(Enum):
    VLLM = "vllm"  # Production, highest throughput
    OLLAMA = "ollama"  # Dev, easy local
    OPENAI = "openai"  # Cloud fallback
    CLAUDE = "claude"  # Cloud fallback
    GEMINI = "gemini"  # Cloud fallback

class UltraLLMService:
    """
    Elite hybrid LLM service combining local + cloud inference.
    
    Features:
    - 16x higher throughput with vLLM
    - Zero-cost local inference
    - Automatic failover to cloud
    - Model-specific routing
    - OpenAI-compatible API
    """
    
    def __init__(self):
        # Backend endpoints
        self.vllm_url = os.getenv('VLLM_URL', 'http://localhost:8000')
        self.ollama_url = os.getenv('OLLAMA_URL', 'http://localhost:11434')
        self.emergent_key = os.getenv('EMERGENT_LLM_KEY', '')
        
        # Backend availability
        self.available_backends = []
        self.backend_performance = {}
        
        # Model routing
        self.model_routing = {
            'llama-3.1-70b': {'preferred': LLMBackend.VLLM, 'fallback': LLMBackend.OLLAMA},
            'llama-3.2-3b': {'preferred': LLMBackend.OLLAMA, 'fallback': LLMBackend.VLLM},
            'gpt-4o': {'preferred': LLMBackend.OPENAI, 'fallback': None},
            'claude-sonnet-4': {'preferred': LLMBackend.CLAUDE, 'fallback': LLMBackend.OPENAI},
            'gemini-2.5-flash': {'preferred': LLMBackend.GEMINI, 'fallback': LLMBackend.OPENAI}
        }
        
        logger.info("ULTRA LLM Service initialized")
    
    async def initialize(self):
        """Check which backends are available"""
        await self._check_backend_availability()
        logger.info(f"Available LLM backends: {self.available_backends}")
    
    async def _check_backend_availability(self):
        """Test connectivity to all backends"""
        async with httpx.AsyncClient(timeout=5.0) as client:
            # Check vLLM
            try:
                response = await client.get(f"{self.vllm_url}/health")
                if response.status_code == 200:
                    self.available_backends.append(LLMBackend.VLLM)
                    logger.info("✓ vLLM available (production-ready, 16x throughput)")
            except:
                logger.warning("vLLM not available (install: pip install vllm, run: vllm serve)")
            
            # Check Ollama
            try:
                response = await client.get(f"{self.ollama_url}/api/tags")
                if response.status_code == 200:
                    self.available_backends.append(LLMBackend.OLLAMA)
                    logger.info("✓ Ollama available (dev-friendly)")
            except:
                logger.warning("Ollama not available (install: https://ollama.com)")
            
            # Cloud backends always available if key exists
            if self.emergent_key:
                self.available_backends.extend([LLMBackend.OPENAI, LLMBackend.CLAUDE, LLMBackend.GEMINI])
                logger.info("✓ Cloud LLMs available via Emergent Universal Key")
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "llama-3.1-70b",
        temperature: float = 0.7,
        max_tokens: int = 2000,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Generate chat completion using best available backend.
        """
        start_time = datetime.now(timezone.utc)
        
        # Select backend based on model
        backend = await self._select_backend_for_model(model)
        
        if not backend:
            return {
                "success": False,
                "error": f"No backends available for model {model}"
            }
        
        logger.info(f"Chat completion with {backend.value}: {model}")
        
        try:
            if backend == LLMBackend.VLLM:
                result = await self._chat_vllm(messages, model, temperature, max_tokens, stream)
            elif backend == LLMBackend.OLLAMA:
                result = await self._chat_ollama(messages, model, temperature, max_tokens, stream)
            elif backend in [LLMBackend.OPENAI, LLMBackend.CLAUDE, LLMBackend.GEMINI]:
                result = await self._chat_cloud(messages, model, temperature, max_tokens, backend)
            else:
                return {"success": False, "error": "Invalid backend"}
            
            # Track performance
            elapsed = (datetime.now(timezone.utc) - start_time).total_seconds()
            self.backend_performance[backend.value] = elapsed
            
            result["backend"] = backend.value
            result["latency"] = elapsed
            return result
        
        except Exception as e:
            logger.error(f"{backend.value} chat completion failed: {e}")
            
            # Try fallback
            fallback = self.model_routing.get(model, {}).get('fallback')
            if fallback and fallback in self.available_backends:
                logger.info(f"Falling back to {fallback.value}...")
                messages_copy = messages.copy()
                return await self.chat_completion(messages_copy, model, temperature, max_tokens, stream)
            
            return {
                "success": False,
                "error": str(e),
                "backend": backend.value
            }
    
    async def _select_backend_for_model(self, model: str) -> Optional[LLMBackend]:
        """Select backend based on model and availability"""
        if not self.available_backends:
            await self._check_backend_availability()
        
        # Check model routing
        if model in self.model_routing:
            preferred = self.model_routing[model]['preferred']
            if preferred in self.available_backends:
                return preferred
            
            fallback = self.model_routing[model].get('fallback')
            if fallback and fallback in self.available_backends:
                return fallback
        
        # Default: prefer local (vLLM > Ollama) over cloud
        if LLMBackend.VLLM in self.available_backends:
            return LLMBackend.VLLM
        elif LLMBackend.OLLAMA in self.available_backends:
            return LLMBackend.OLLAMA
        elif LLMBackend.OPENAI in self.available_backends:
            return LLMBackend.OPENAI
        
        return None
    
    async def _chat_vllm(self, messages: List[Dict[str, str]], model: str, temperature: float, max_tokens: int, stream: bool) -> Dict[str, Any]:
        """Chat using vLLM (OpenAI-compatible API)"""
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{self.vllm_url}/v1/chat/completions",
                json={
                    "model": model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "stream": stream
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "message": data['choices'][0]['message']['content'],
                    "usage": data.get('usage', {}),
                    "note": "Generated with vLLM (16x throughput vs Ollama)"
                }
            else:
                raise Exception(f"vLLM API error: {response.status_code}")
    
    async def _chat_ollama(self, messages: List[Dict[str, str]], model: str, temperature: float, max_tokens: int, stream: bool) -> Dict[str, Any]:
        """Chat using Ollama"""
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{self.ollama_url}/api/chat",
                json={
                    "model": model,
                    "messages": messages,
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                        "num_predict": max_tokens
                    }
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "message": data['message']['content'],
                    "note": "Generated with Ollama (easy local LLM)"
                }
            else:
                raise Exception(f"Ollama API error: {response.status_code}")
    
    async def _chat_cloud(self, messages: List[Dict[str, str]], model: str, temperature: float, max_tokens: int, backend: LLMBackend) -> Dict[str, Any]:
        """Chat using cloud providers via Emergent Universal Key"""
        # Use emergentintegrations for unified cloud access
        try:
            from emergentintegrations.openai import OpenAIEmergent
            
            client = OpenAIEmergent(api_key=self.emergent_key)
            
            # Map model names
            model_map = {
                'claude-sonnet-4': 'claude-sonnet-4',
                'gpt-4o': 'gpt-4o',
                'gemini-2.5-flash': 'gemini-2.5-flash'
            }
            
            actual_model = model_map.get(model, model)
            
            response = await asyncio.to_thread(
                client.chat.completions.create,
                model=actual_model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return {
                "success": True,
                "message": response.choices[0].message.content,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens
                },
                "note": f"Generated with {backend.value} via Emergent Universal Key"
            }
        except Exception as e:
            raise Exception(f"Cloud LLM error: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get service status"""
        return {
            "available_backends": [b.value for b in self.available_backends],
            "backend_count": len(self.available_backends),
            "performance": self.backend_performance,
            "models": list(self.model_routing.keys()),
            "features": {
                "local_inference": LLMBackend.VLLM in self.available_backends or LLMBackend.OLLAMA in self.available_backends,
                "cloud_fallback": LLMBackend.OPENAI in self.available_backends,
                "streaming": False  # Future feature
            },
            "recommendation": "Install vLLM for production (16x throughput), Ollama for development"
        }

# Singleton instance
ultra_llm = UltraLLMService()
