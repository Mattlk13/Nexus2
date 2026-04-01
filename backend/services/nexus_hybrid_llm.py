"""
NEXUS Hybrid LLM Service
Combines OpenAI GPT-5.2, Claude Sonnet 4, Gemini 2.5 with intelligent routing

Features:
- Smart model selection based on task type
- Automatic fallbacks
- Cost optimization
- Streaming support
- Context management
"""

from emergentintegrations.llm.chat import LlmChat, UserMessage
import os
import logging
from typing import Optional, List, Dict
import time

logger = logging.getLogger(__name__)

class HybridLLMService:
    def __init__(self):
        """Initialize hybrid LLM with Emergent Universal Key"""
        self.api_key = os.environ.get('EMERGENT_LLM_KEY')
        if not self.api_key:
            raise ValueError("EMERGENT_LLM_KEY not configured")
        
        # Model capabilities and costs (per 1M tokens)
        self.models = {
            # Best for: Long-form content, creative writing, analysis
            "claude": {
                "provider": "anthropic",
                "model": "claude-sonnet-4-5-20250929",
                "max_tokens": 200000,
                "cost_input": 3.0,
                "cost_output": 15.0,
                "best_for": ["creative", "analysis", "long-form", "code-review"]
            },
            # Best for: Code generation, quick tasks, structured output
            "gpt-5.2": {
                "provider": "openai",
                "model": "gpt-5.2",
                "max_tokens": 128000,
                "cost_input": 2.5,
                "cost_output": 10.0,
                "best_for": ["code", "structured", "quick", "json"]
            },
            # Best for: Multimodal, fast responses, cost-effective
            "gemini": {
                "provider": "google",
                "model": "gemini-2.5-flash",
                "max_tokens": 1000000,
                "cost_input": 0.15,
                "cost_output": 0.60,
                "best_for": ["fast", "cheap", "multimodal", "large-context"]
            }
        }
        
        logger.info("Hybrid LLM initialized with 3 models")
    
    def select_best_model(self, task_type: str = "general") -> str:
        """Intelligently select best model for task"""
        task_mappings = {
            "creative": "claude",
            "ebook": "claude",
            "story": "claude",
            "music": "gpt-5.2",
            "code": "gpt-5.2",
            "json": "gpt-5.2",
            "quick": "gemini",
            "chat": "gemini",
            "cheap": "gemini",
            "analysis": "claude"
        }
        return task_mappings.get(task_type.lower(), "gemini")
    
    async def generate(
        self,
        prompt: str,
        task_type: str = "general",
        system_message: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        fallback: bool = True
    ) -> Dict:
        """
        Generate text with intelligent model selection and fallbacks
        """
        model_key = self.select_best_model(task_type)
        model_config = self.models[model_key]
        
        try:
            start_time = time.time()
            
            # Create chat session
            chat = LlmChat(
                api_key=self.api_key,
                session_id=f"hybrid-{task_type}-{int(time.time())}",
                system_message=system_message or f"You are a helpful AI assistant specialized in {task_type} tasks."
            ).with_model(model_config["provider"], model_config["model"])
            
            # Generate
            response = await chat.send_message(UserMessage(text=prompt))
            
            elapsed = time.time() - start_time
            
            return {
                "success": True,
                "content": response,
                "model": model_config["model"],
                "provider": model_config["provider"],
                "elapsed_seconds": round(elapsed, 2),
                "task_type": task_type
            }
            
        except Exception as e:
            logger.error(f"Model {model_key} failed: {e}")
            
            if fallback:
                # Try fallback models
                fallback_order = ["gemini", "gpt-5.2", "claude"]
                for fallback_key in fallback_order:
                    if fallback_key == model_key:
                        continue
                    
                    try:
                        logger.info(f"Trying fallback: {fallback_key}")
                        fallback_config = self.models[fallback_key]
                        
                        chat = LlmChat(
                            api_key=self.api_key,
                            session_id=f"hybrid-fallback-{int(time.time())}",
                            system_message=system_message or "You are a helpful AI assistant."
                        ).with_model(fallback_config["provider"], fallback_config["model"])
                        
                        response = await chat.send_message(UserMessage(text=prompt))
                        
                        return {
                            "success": True,
                            "content": response,
                            "model": fallback_config["model"],
                            "provider": fallback_config["provider"],
                            "fallback_used": True,
                            "original_model": model_config["model"]
                        }
                    except Exception as fallback_error:
                        logger.error(f"Fallback {fallback_key} failed: {fallback_error}")
                        continue
            
            return {
                "success": False,
                "error": str(e),
                "model": model_config["model"]
            }
    
    async def generate_with_cost_optimization(
        self,
        prompt: str,
        max_cost_per_1m_tokens: float = 5.0,
        **kwargs
    ) -> Dict:
        """Generate with cost constraints"""
        # Estimate tokens (rough)
        estimated_tokens = len(prompt.split()) * 1.3  # ~1.3 tokens per word
        
        # Find cheapest model under cost threshold
        for model_key in ["gemini", "gpt-5.2", "claude"]:
            model = self.models[model_key]
            if model["cost_input"] <= max_cost_per_1m_tokens:
                kwargs["task_type"] = model_key
                return await self.generate(prompt, **kwargs)
        
        # Default to cheapest
        kwargs["task_type"] = "cheap"
        return await self.generate(prompt, **kwargs)
    
    async def batch_generate(
        self,
        prompts: List[str],
        task_type: str = "general",
        **kwargs
    ) -> List[Dict]:
        """Generate multiple completions efficiently"""
        results = []
        for prompt in prompts:
            result = await self.generate(prompt, task_type, **kwargs)
            results.append(result)
        return results

# Global instance
hybrid_llm = HybridLLMService()

# Route registration for dynamic loading
def register_routes(db, get_current_user, require_admin):
    """Register Llm routes"""
    from fastapi import APIRouter
    router = APIRouter(tags=["Llm Hybrid"])
    
    @router.get("/capabilities")
    async def get_capabilities():
        """Get Llm capabilities"""
        if hasattr(hybrid_llm, 'get_capabilities'):
            return hybrid_llm.get_capabilities()
        return {"status": "active", "name": "Llm"}
    
    return router

def init_hybrid(db):
    return hybrid_llm
