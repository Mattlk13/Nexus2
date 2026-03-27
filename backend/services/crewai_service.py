"""
CrewAI Multi-Agent Orchestration Service
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import os

try:
    from crewai import Agent, Task, Crew, Process
    from crewai.tools import tool
    CREWAI_AVAILABLE = True
except ImportError:
    CREWAI_AVAILABLE = False
    logging.warning("CrewAI not available. Install with: pip install crewai")

logger = logging.getLogger(__name__)

class CrewAIService:
    """CrewAI multi-agent orchestration for complex workflows"""
    
    def __init__(self):
        self.available = CREWAI_AVAILABLE
        self.crews = {}
        if self.available:
            self._initialize_default_crews()
    
    def _initialize_default_crews(self):
        """Initialize default agent crews"""
        try:
            # Research Crew
            researcher = Agent(
                role='Market Researcher',
                goal='Research and analyze AI tools and trends',
                backstory='Expert market analyst specializing in AI technologies',
                verbose=True,
                allow_delegation=False
            )
            
            analyst = Agent(
                role='Data Analyst',
                goal='Analyze data and provide insights',
                backstory='Data scientist with expertise in trend analysis',
                verbose=True,
                allow_delegation=False
            )
            
            self.crews['research'] = {
                'agents': [researcher, analyst],
                'description': 'AI tool research and analysis'
            }
            
            # Content Crew
            writer = Agent(
                role='Content Writer',
                goal='Create engaging content for products and posts',
                backstory='Professional writer specializing in tech content',
                verbose=True,
                allow_delegation=False
            )
            
            editor = Agent(
                role='Content Editor',
                goal='Review and improve content quality',
                backstory='Experienced editor with eye for detail',
                verbose=True,
                allow_delegation=False
            )
            
            self.crews['content'] = {
                'agents': [writer, editor],
                'description': 'Content creation and editing'
            }
            
            logger.info(f"✓ CrewAI initialized with {len(self.crews)} crews")
        except Exception as e:
            logger.error(f"CrewAI initialization failed: {e}")
            self.available = False
    
    async def run_crew(
        self,
        crew_name: str,
        tasks: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Run a crew with specified tasks"""
        if not self.available:
            return {
                "success": False,
                "error": "CrewAI not available"
            }
        
        if crew_name not in self.crews:
            return {
                "success": False,
                "error": f"Unknown crew: {crew_name}"
            }
        
        try:
            crew_data = self.crews[crew_name]
            agents = crew_data['agents']
            
            # Create tasks for agents
            crew_tasks = []
            for i, task_data in enumerate(tasks):
                task = Task(
                    description=task_data.get('description', ''),
                    agent=agents[i % len(agents)],
                    expected_output=task_data.get('expected_output', 'Detailed analysis')
                )
                crew_tasks.append(task)
            
            # Create and run crew
            crew = Crew(
                agents=agents,
                tasks=crew_tasks,
                process=Process.sequential,
                verbose=True
            )
            
            result = crew.kickoff()
            
            return {
                "success": True,
                "crew": crew_name,
                "result": str(result),
                "tasks_completed": len(crew_tasks),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            logger.error(f"CrewAI execution failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def research_tool(self, query: str) -> Dict[str, Any]:
        """Use research crew to analyze a topic"""
        tasks = [
            {
                "description": f"Research and gather information about: {query}",
                "expected_output": "Comprehensive research report"
            },
            {
                "description": f"Analyze the research findings and provide insights",
                "expected_output": "Detailed analysis with recommendations"
            }
        ]
        return await self.run_crew('research', tasks)
    
    async def create_content(self, topic: str, content_type: str = "article") -> Dict[str, Any]:
        """Use content crew to create content"""
        tasks = [
            {
                "description": f"Write a {content_type} about: {topic}",
                "expected_output": f"Well-written {content_type}"
            },
            {
                "description": f"Review and edit the {content_type} for quality",
                "expected_output": "Polished final content"
            }
        ]
        return await self.run_crew('content', tasks)
    
    def get_status(self) -> Dict[str, Any]:
        """Get CrewAI service status"""
        return {
            "available": self.available,
            "crews": list(self.crews.keys()),
            "crew_count": len(self.crews)
        }

crewai_service = CrewAIService()
