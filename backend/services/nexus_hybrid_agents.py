"""
NEXUS Hybrid AI Agents Orchestrator
Consolidates 11 AI agent services into unified multi-agent system

Combined Services:
1. advanced_agents.py - Multi-agent coordination
2. multi_agent_service.py - Agent collaboration
3. crewai_service.py - CrewAI integration
4. aixploria_service.py - AI exploration
5. manus_service.py - Manual agent tasks
6. openclaw_service.py - Web scraping agent
7. yolo_service.py - Vision detection agent
8. ultra_llm_service.py - Advanced LLM agent
9. ultra_voice_service.py - Voice agent
10. ultra_image_video_generator.py - Media generation agent
11. llm_finetuning_service.py - Model training agent

Features:
- Multi-agent task orchestration
- Intelligent agent selection
- Parallel agent execution
- Agent collaboration & handoff
- Memory & context sharing
"""

import os
import logging
from typing import List, Dict, Optional
import asyncio
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

class HybridAgentsOrchestrator:
    def __init__(self):
        """Initialize all AI agents"""
        self.api_key = os.environ.get('EMERGENT_LLM_KEY')
        
        # Agent registry
        self.agents = {
            "researcher": {
                "name": "Research Agent",
                "capabilities": ["web_search", "data_analysis", "summarization"],
                "model": "claude",  # Best for research
                "active": True
            },
            "coder": {
                "name": "Code Generator Agent",
                "capabilities": ["code_generation", "debugging", "code_review"],
                "model": "gpt-5.2",  # Best for code
                "active": True
            },
            "writer": {
                "name": "Content Writer Agent",
                "capabilities": ["writing", "editing", "creative"],
                "model": "claude",  # Best for creative
                "active": True
            },
            "analyst": {
                "name": "Data Analyst Agent",
                "capabilities": ["data_analysis", "visualization", "insights"],
                "model": "gemini",  # Fast for analysis
                "active": True
            },
            "designer": {
                "name": "Design Agent",
                "capabilities": ["ui_design", "ux_analysis", "visual_design"],
                "model": "gpt-5.2",
                "active": True
            },
            "tester": {
                "name": "QA Testing Agent",
                "capabilities": ["testing", "bug_detection", "quality_assurance"],
                "model": "gpt-5.2",
                "active": True
            },
            "marketer": {
                "name": "Marketing Agent",
                "capabilities": ["marketing", "copywriting", "seo"],
                "model": "claude",
                "active": True
            },
            "scraper": {
                "name": "Web Scraper Agent",
                "capabilities": ["web_scraping", "data_extraction"],
                "model": "gemini",  # Fast
                "active": True
            },
            "vision": {
                "name": "Computer Vision Agent",
                "capabilities": ["image_analysis", "object_detection", "ocr"],
                "model": "gemini",  # Multimodal
                "active": True
            },
            "voice": {
                "name": "Voice Agent",
                "capabilities": ["speech_recognition", "tts", "voice_analysis"],
                "model": "openai",
                "active": True
            },
            "coordinator": {
                "name": "Task Coordinator",
                "capabilities": ["task_breakdown", "agent_coordination", "workflow"],
                "model": "claude",  # Best for complex reasoning
                "active": True
            }
        }
        
        logger.info(f"Hybrid Agents initialized: {len(self.agents)} agents available")
    
    def select_best_agent(self, task: str, capability_required: Optional[str] = None) -> str:
        """Select best agent for task"""
        if capability_required:
            # Find agent with capability
            for agent_id, agent in self.agents.items():
                if capability_required in agent["capabilities"] and agent["active"]:
                    return agent_id
        
        # Auto-select based on task keywords
        task_lower = task.lower()
        if any(word in task_lower for word in ["research", "analyze", "find"]):
            return "researcher"
        elif any(word in task_lower for word in ["code", "program", "function"]):
            return "coder"
        elif any(word in task_lower for word in ["write", "content", "blog"]):
            return "writer"
        elif any(word in task_lower for word in ["data", "metrics", "stats"]):
            return "analyst"
        elif any(word in task_lower for word in ["design", "ui", "ux"]):
            return "designer"
        elif any(word in task_lower for word in ["test", "qa", "bug"]):
            return "tester"
        elif any(word in task_lower for word in ["market", "seo", "promote"]):
            return "marketer"
        elif any(word in task_lower for word in ["scrape", "extract"]):
            return "scraper"
        elif any(word in task_lower for word in ["image", "vision", "detect"]):
            return "vision"
        elif any(word in task_lower for word in ["voice", "speech", "audio"]):
            return "voice"
        else:
            return "coordinator"  # Default to coordinator for complex tasks
    
    async def execute_agent_task(
        self,
        task: str,
        agent_id: Optional[str] = None,
        context: Optional[Dict] = None
    ) -> Dict:
        """Execute task with specified or auto-selected agent"""
        # Select agent
        if not agent_id:
            agent_id = self.select_best_agent(task)
        
        agent = self.agents.get(agent_id)
        if not agent or not agent["active"]:
            return {
                "success": False,
                "error": f"Agent {agent_id} not available"
            }
        
        try:
            from services.nexus_hybrid_llm import hybrid_llm
            
            # Build agent prompt
            agent_prompt = f"""You are {agent['name']} with capabilities: {', '.join(agent['capabilities'])}.

Task: {task}

Context: {context or 'None provided'}

Execute this task using your specialized capabilities. Provide detailed, actionable results."""
            
            # Use hybrid LLM with agent's preferred model
            result = await hybrid_llm.generate(
                prompt=agent_prompt,
                task_type=agent_id,
                max_tokens=4096
            )
            
            return {
                "success": True,
                "agent": agent['name'],
                "agent_id": agent_id,
                "result": result['content'],
                "model_used": result.get('model'),
                "elapsed": result.get('elapsed_seconds')
            }
            
        except Exception as e:
            logger.error(f"Agent {agent_id} failed: {e}")
            return {
                "success": False,
                "agent": agent['name'],
                "error": str(e)
            }
    
    async def execute_multi_agent_workflow(
        self,
        task: str,
        agents: List[str],
        sequential: bool = True
    ) -> Dict:
        """Execute task with multiple agents (sequential or parallel)"""
        results = []
        
        if sequential:
            # Sequential execution with context passing
            context = {}
            for agent_id in agents:
                result = await self.execute_agent_task(task, agent_id, context)
                results.append(result)
                # Pass result to next agent
                if result["success"]:
                    context[agent_id] = result["result"]
        else:
            # Parallel execution
            tasks = [self.execute_agent_task(task, agent_id) for agent_id in agents]
            results = await asyncio.gather(*tasks)
        
        return {
            "success": all(r.get("success") for r in results),
            "workflow_type": "sequential" if sequential else "parallel",
            "agents_used": len(agents),
            "results": results
        }
    
    async def intelligent_task_breakdown(
        self,
        complex_task: str
    ) -> Dict:
        """Break down complex task and assign to multiple agents"""
        # Use coordinator agent to break down task
        breakdown_prompt = f"""Break down this complex task into subtasks and assign to specialized agents:

Task: {complex_task}

Available agents:
{chr(10).join([f"- {a['name']}: {', '.join(a['capabilities'])}" for a in self.agents.values()])}

Provide:
1. List of subtasks
2. Recommended agent for each subtask
3. Execution order (sequential or parallel)"""
        
        try:
            from services.nexus_hybrid_llm import hybrid_llm
            
            result = await hybrid_llm.generate(
                prompt=breakdown_prompt,
                task_type="analysis",
                max_tokens=2048
            )
            
            return {
                "success": True,
                "breakdown": result['content'],
                "next_step": "Execute with execute_multi_agent_workflow"
            }
            
        except Exception as e:
            logger.error(f"Task breakdown failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_agent_status(self) -> Dict:
        """Get status of all agents"""
        return {
            "total_agents": len(self.agents),
            "active_agents": sum(1 for a in self.agents.values() if a["active"]),
            "agents": self.agents
        }
    
    async def agent_collaboration(
        self,
        task: str,
        primary_agent: str,
        support_agents: List[str]
    ) -> Dict:
        """Primary agent leads, support agents assist"""
        # Primary agent starts
        primary_result = await self.execute_agent_task(task, primary_agent)
        
        if not primary_result["success"]:
            return primary_result
        
        # Support agents provide feedback/improvements
        support_results = []
        for agent_id in support_agents:
            support_task = f"Review and improve this result: {primary_result['result'][:500]}..."
            support_result = await self.execute_agent_task(support_task, agent_id)
            support_results.append(support_result)
        
        return {
            "success": True,
            "collaboration_type": "primary_with_support",
            "primary_agent": primary_agent,
            "primary_result": primary_result,
            "support_feedback": support_results,
            "agents_involved": 1 + len(support_agents)
        }

# Global instance
hybrid_agents = HybridAgentsOrchestrator()

# Route registration for dynamic loading
def register_routes(db, get_current_user, require_admin):
    """Register Agents routes"""
    from fastapi import APIRouter
    router = APIRouter(tags=["Agents Hybrid"])
    
    @router.get("/capabilities")
    async def get_capabilities():
        """Get Agents capabilities"""
        if hasattr(hybrid_agents, 'get_capabilities'):
            return hybrid_agents.get_capabilities()
        return {"status": "active", "name": "Agents"}
    
    return router

def init_hybrid(db):
    return hybrid_agents
