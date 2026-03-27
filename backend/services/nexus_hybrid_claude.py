"""
NEXUS Claude Opus Integration
Advanced AI reasoning and analysis using Claude Opus 4
"""

import logging
import os
from typing import Dict, List, Optional
from datetime import datetime, timezone
from dotenv import load_dotenv
from emergentintegrations.llm.chat import LlmChat, UserMessage

load_dotenv()

logger = logging.getLogger(__name__)

class ClaudeOpusEngine:
    """Claude Opus 4 - Advanced AI Reasoning"""
    
    def __init__(self, db=None):
        self.db = db
        self.conversations_collection = db.claude_conversations if db is not None else None
        self.api_key = os.getenv('EMERGENT_LLM_KEY')
        
        # Claude Opus 4 model
        self.model = "claude-opus-4-6"
        self.provider = "anthropic"
        
        logger.info(f"🧠 Claude Opus Engine initialized (model: {self.model})")
    
    async def chat(self, message: str, session_id: str, system_prompt: Optional[str] = None) -> Dict:
        """Chat with Claude Opus"""
        try:
            # Initialize chat
            chat = LlmChat(
                api_key=self.api_key,
                session_id=session_id,
                system_message=system_prompt or "You are Claude Opus, an advanced AI assistant integrated into the NEXUS AI platform. Provide detailed, thoughtful responses."
            ).with_model(self.provider, self.model)
            
            # Create user message
            user_message = UserMessage(text=message)
            
            # Get response
            response = await chat.send_message(user_message)
            
            # Store in database
            conversation_record = {
                "session_id": session_id,
                "user_message": message,
                "assistant_response": response,
                "model": self.model,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            if self.conversations_collection is not None:
                await self.conversations_collection.insert_one(conversation_record)
            
            return {
                "success": True,
                "response": response,
                "model": self.model,
                "session_id": session_id
            }
        except Exception as e:
            logger.error(f"Claude chat failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def advanced_reasoning(self, problem: str, context: Optional[Dict] = None) -> Dict:
        """Use Claude Opus for advanced reasoning tasks"""
        try:
            system_prompt = """You are Claude Opus, specialized in advanced reasoning and analysis.
Break down complex problems step-by-step.
Provide detailed logical reasoning.
Consider multiple perspectives.
Identify potential issues and edge cases."""
            
            # Add context if provided
            full_prompt = problem
            if context:
                full_prompt = f"Context: {context}\n\nProblem: {problem}"
            
            chat = LlmChat(
                api_key=self.api_key,
                session_id=f"reasoning_{int(datetime.now(timezone.utc).timestamp())}",
                system_message=system_prompt
            ).with_model(self.provider, self.model)
            
            response = await chat.send_message(UserMessage(text=full_prompt))
            
            return {
                "success": True,
                "problem": problem,
                "reasoning": response,
                "model": self.model,
                "context_used": context is not None
            }
        except Exception as e:
            logger.error(f"Reasoning failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def code_review(self, code: str, language: str) -> Dict:
        """Use Claude Opus for code review"""
        try:
            system_prompt = f"""You are a senior software engineer using Claude Opus.
Review {language} code for:
- Bugs and potential errors
- Performance issues
- Security vulnerabilities
- Best practices
- Code quality

Provide specific, actionable feedback."""
            
            chat = LlmChat(
                api_key=self.api_key,
                session_id=f"code_review_{int(datetime.now(timezone.utc).timestamp())}",
                system_message=system_prompt
            ).with_model(self.provider, self.model)
            
            response = await chat.send_message(UserMessage(text=f"Review this {language} code:\n\n```{language}\n{code}\n```"))
            
            return {
                "success": True,
                "language": language,
                "review": response,
                "model": self.model
            }
        except Exception as e:
            logger.error(f"Code review failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def content_generation(self, topic: str, style: str, length: str) -> Dict:
        """Generate content with Claude Opus"""
        try:
            system_prompt = f"You are a {style} content writer using Claude Opus. Create {length} content that is engaging, well-structured, and high-quality."
            
            chat = LlmChat(
                api_key=self.api_key,
                session_id=f"content_{int(datetime.now(timezone.utc).timestamp())}",
                system_message=system_prompt
            ).with_model(self.provider, self.model)
            
            prompt = f"Write {length} content about: {topic}"
            response = await chat.send_message(UserMessage(text=prompt))
            
            return {
                "success": True,
                "topic": topic,
                "content": response,
                "style": style,
                "length": length,
                "model": self.model
            }
        except Exception as e:
            logger.error(f"Content generation failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def data_analysis(self, data: Dict, analysis_type: str) -> Dict:
        """Analyze data with Claude Opus"""
        try:
            system_prompt = """You are a data analyst using Claude Opus.
Analyze data thoroughly and provide:
- Key insights
- Patterns and trends
- Anomalies
- Recommendations"""
            
            chat = LlmChat(
                api_key=self.api_key,
                session_id=f"analysis_{int(datetime.now(timezone.utc).timestamp())}",
                system_message=system_prompt
            ).with_model(self.provider, self.model)
            
            prompt = f"Analyze this {analysis_type} data:\n\n{data}"
            response = await chat.send_message(UserMessage(text=prompt))
            
            return {
                "success": True,
                "analysis": response,
                "type": analysis_type,
                "model": self.model
            }
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_conversation_history(self, session_id: str, limit: int = 20) -> Dict:
        """Get conversation history"""
        try:
            if self.conversations_collection is not None:
                history = await self.conversations_collection.find(
                    {"session_id": session_id},
                    {"_id": 0}
                ).sort("timestamp", -1).limit(limit).to_list(limit)
                
                return {
                    "success": True,
                    "session_id": session_id,
                    "messages": history,
                    "total": len(history)
                }
            
            return {"success": False, "error": "Database not configured"}
        except Exception as e:
            logger.error(f"History fetch failed: {e}")
            return {"success": False, "error": str(e)}
    
    def get_capabilities(self) -> Dict:
        return {
            "name": "Claude Opus Hybrid",
            "version": "1.0.0",
            "provider": "anthropic",
            "model": self.model,
            "features": {
                "chat": True,
                "advanced_reasoning": True,
                "code_review": True,
                "content_generation": True,
                "data_analysis": True,
                "conversation_history": True
            },
            "context_window": "200K tokens",
            "capabilities": [
                "Long-form reasoning",
                "Complex problem solving",
                "Code analysis",
                "Research and analysis",
                "Creative writing",
                "Data interpretation"
            ],
            "use_cases": [
                "Strategic planning",
                "Technical documentation",
                "Code reviews",
                "Research synthesis",
                "Content creation"
            ]
        }

# Global instance
hybrid_claude = ClaudeOpusEngine(db=None)

def create_claude_engine(db):
    """Factory function"""
    global hybrid_claude
    hybrid_claude = ClaudeOpusEngine(db)
    return hybrid_claude

def register_routes(db, get_current_user, require_admin):
    """Self-registration function for dynamic router"""
    from fastapi import APIRouter, Depends
    
    router = APIRouter()
    engine = create_claude_engine(db)
    
    @router.get("/capabilities")
    async def get_capabilities():
        """Get Claude capabilities"""
        return engine.get_capabilities()
    
    return router

