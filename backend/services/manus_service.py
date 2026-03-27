import os
import asyncio
import logging
import aiohttp
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

ROOT_DIR = Path(__file__).parent.parent
load_dotenv(ROOT_DIR / '.env')

MANUS_API_KEY = os.environ.get('MANUS_API_KEY', '')
MANUS_BASE_URL = "https://api.manus.ai/v1"

logger = logging.getLogger(__name__)

class ManusAIService:
    """Service for integrating Manus AI autonomous agents"""
    
    def __init__(self):
        self.api_key = MANUS_API_KEY
        self.base_url = MANUS_BASE_URL
    
    async def create_task(self, task_description: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create a new autonomous task for Manus AI to execute"""
        if not self.api_key or self.api_key == "manus_demo_key_placeholder":
            logger.warning("Manus API key not configured - returning mock response")
            return {
                "task_id": f"mock_task_{datetime.now().timestamp()}",
                "status": "queued",
                "description": task_description,
                "mocked": True
            }
        
        headers = {
            "API_KEY": self.api_key,
            "Content-Type": "application/json"
        }
        
        payload = {
            "task": task_description,
            "context": context or {},
            "priority": "normal",
            "auto_execute": True
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/tasks",
                    headers=headers,
                    json=payload
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.info(f"Manus task created: {data.get('task_id')}")
                        return data
                    else:
                        error = await response.text()
                        logger.error(f"Manus API error: {error}")
                        return {"error": error, "status": "failed"}
        except Exception as e:
            logger.error(f"Manus API request failed: {str(e)}")
            return {"error": str(e), "status": "failed"}
    
    async def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get status of a Manus AI task"""
        if not self.api_key or self.api_key == "manus_demo_key_placeholder":
            return {
                "task_id": task_id,
                "status": "completed",
                "result": "Mock result - Manus API key not configured",
                "mocked": True
            }
        
        headers = {"API_KEY": self.api_key}
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/tasks/{task_id}",
                    headers=headers
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        return {"error": "Task not found", "status": "failed"}
        except Exception as e:
            logger.error(f"Failed to get task status: {str(e)}")
            return {"error": str(e), "status": "failed"}
    
    async def analyze_platform_metrics(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Use Manus AI to analyze platform metrics and suggest improvements"""
        task_description = f"""
        Analyze the following NEXUS marketplace metrics and provide actionable insights:
        - Total Users: {metrics.get('users', 0)}
        - Total Products: {metrics.get('products', 0)}
        - Total Revenue: ${metrics.get('revenue', 0)}
        - Conversion Rate: {metrics.get('conversion_rate', 0)}%
        
        Provide:
        1. Top 3 growth opportunities
        2. Revenue optimization strategies
        3. User engagement recommendations
        4. Competitive positioning advice
        """
        
        return await self.create_task(task_description, {"type": "platform_analysis", "metrics": metrics})
    
    async def discover_integration_tools(self, category: str) -> Dict[str, Any]:
        """Use Manus AI to research and recommend tools for integration"""
        task_description = f"""
        Research and recommend the top 5 tools/APIs for {category} that would benefit an AI marketplace platform.
        
        For each tool, provide:
        1. Name and official API documentation URL
        2. Key features and benefits
        3. Pricing model
        4. Integration complexity (easy/medium/hard)
        5. ROI potential for a marketplace platform
        
        Focus on tools with robust APIs, good documentation, and proven track records.
        """
        
        return await self.create_task(task_description, {"type": "tool_discovery", "category": category})
    
    async def generate_marketing_content(self, campaign_type: str, target_audience: str) -> Dict[str, Any]:
        """Use Manus AI to create marketing campaigns"""
        task_description = f"""
        Create a {campaign_type} marketing campaign for NEXUS AI marketplace targeting {target_audience}.
        
        Include:
        1. Campaign headline and tagline
        2. 3 social media posts (Twitter, LinkedIn, Instagram)
        3. Email marketing copy
        4. Call-to-action strategies
        5. Success metrics to track
        """
        
        return await self.create_task(task_description, {"type": "marketing", "campaign": campaign_type})
    
    async def find_investors(self, company_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Use Manus AI to research and identify potential investors"""
        task_description = f"""
        Research and identify 20 potential investors/VCs for NEXUS, an AI-powered marketplace platform.
        
        Company metrics:
        - Users: {company_profile.get('users', 0)}
        - Revenue: ${company_profile.get('revenue', 0)}
        - Growth Rate: {company_profile.get('growth_rate', 0)}%
        - Stage: {company_profile.get('stage', 'Seed')}
        
        For each investor, provide:
        1. Name and firm
        2. Email/contact info (if publicly available)
        3. Investment focus and typical check size
        4. Portfolio companies (especially AI/marketplace)
        5. Why they're a good fit
        
        Prioritize investors who have funded AI marketplaces or creator economy platforms.
        """
        
        return await self.create_task(task_description, {"type": "investor_research", "profile": company_profile})

manus_service = ManusAIService()
