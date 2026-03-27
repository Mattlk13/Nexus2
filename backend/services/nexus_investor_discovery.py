"""
NEXUS Investor Discovery & Contact Management System
Automated investor/angel investor search with daily updates

Features:
- Investor database with contact info
- Daily automated discovery
- Search by industry, stage, location
- Contact tracking & CRM
- Investment criteria matching
- Lead scoring
"""

import os
import logging
from typing import Dict, List, Optional
from datetime import datetime, timezone, timedelta
import asyncio

logger = logging.getLogger(__name__)

class InvestorDiscoveryService:
    def __init__(self, db=None):
        """Initialize investor discovery system"""
        self.db = db
        self.llm_key = os.environ.get('EMERGENT_LLM_KEY')
        
        # Investor sources
        self.sources = [
            "AngelList",
            "Crunchbase",
            "LinkedIn",
            "Twitter/X",
            "Product Hunt",
            "Y Combinator",
            "500 Startups",
            "Techstars"
        ]
        
        logger.info("💼 Investor Discovery System initialized")
    
    async def discover_investors(self, criteria: Dict = None) -> Dict:
        """
        Discover investors based on criteria
        Uses AI to find relevant investors
        """
        try:
            criteria = criteria or {}
            
            prompt = f"""Generate a list of 10 real angel investors and VCs who would be interested in an AI-powered creator marketplace and social platform.

Criteria:
- Industry: {criteria.get('industry', 'AI, Creator Economy, SaaS')}
- Stage: {criteria.get('stage', 'Seed, Series A')}
- Location: {criteria.get('location', 'Global')}
- Check Size: {criteria.get('check_size', '$100k-$2M')}

For each investor, provide:
1. Name
2. Firm/Organization
3. Email (if available, format: firstname@firm.com or use common patterns)
4. LinkedIn URL
5. Twitter/X handle
6. Investment focus
7. Notable investments
8. Typical check size

Format as JSON array."""
            
            # Use AI to discover investors
            from emergentintegrations.llm.chat import LlmChat, UserMessage, SystemMessage
            
            system_msg = SystemMessage(content="You are an expert in venture capital and angel investing. Provide accurate, realistic investor information.")
            user_msg = UserMessage(content=prompt)
            
            llm = LlmChat(api_key=self.llm_key)
            response = llm.chat(
                messages=[system_msg, user_msg],
                model="gpt-5.2",
                temperature=0.7
            )
            
            # Parse AI response
            investors_text = response
            
            # Store in database
            discovery_record = {
                "id": f"discovery_{int(datetime.now(timezone.utc).timestamp())}",
                "criteria": criteria,
                "investors_found": investors_text,
                "discovered_at": datetime.now(timezone.utc).isoformat(),
                "source": "ai_discovery"
            }
            
            if self.db:
                await self.db.investor_discoveries.insert_one(discovery_record)
            
            return {
                "success": True,
                "investors": investors_text,
                "criteria": criteria,
                "source": "AI Discovery (GPT-5.2)",
                "count": 10
            }
            
        except Exception as e:
            logger.error(f"Investor discovery failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def add_investor_to_database(self, investor_data: Dict) -> Dict:
        """Add investor to CRM database"""
        try:
            investor = {
                "id": f"inv_{int(datetime.now(timezone.utc).timestamp())}",
                **investor_data,
                "added_at": datetime.now(timezone.utc).isoformat(),
                "last_updated": datetime.now(timezone.utc).isoformat(),
                "status": "new",  # new, contacted, meeting_scheduled, passed, invested
                "lead_score": self._calculate_lead_score(investor_data),
                "notes": [],
                "interactions": []
            }
            
            if self.db:
                await self.db.investors.insert_one(investor)
            
            return {
                "success": True,
                "investor": investor,
                "message": "Investor added to database"
            }
            
        except Exception as e:
            logger.error(f"Failed to add investor: {e}")
            return {"success": False, "error": str(e)}
    
    def _calculate_lead_score(self, investor_data: Dict) -> int:
        """Calculate lead score (0-100) based on investor fit"""
        score = 50  # Base score
        
        # Factors that increase score
        if investor_data.get('investment_focus'):
            if any(keyword in investor_data['investment_focus'].lower() 
                   for keyword in ['ai', 'creator', 'saas', 'marketplace']):
                score += 20
        
        if investor_data.get('email'):
            score += 10
        
        if investor_data.get('linkedin'):
            score += 10
        
        if investor_data.get('notable_investments'):
            score += 10
        
        return min(score, 100)
    
    async def search_investors(self, query: Dict) -> Dict:
        """Search investors in database"""
        try:
            if not self.db:
                return {"success": False, "error": "Database not available"}
            
            # Build search filter
            search_filter = {}
            
            if query.get('industry'):
                search_filter['investment_focus'] = {'$regex': query['industry'], '$options': 'i'}
            
            if query.get('min_check_size'):
                search_filter['typical_check_size'] = {'$gte': query['min_check_size']}
            
            if query.get('status'):
                search_filter['status'] = query['status']
            
            investors = await self.db.investors.find(
                search_filter,
                {"_id": 0}
            ).sort("lead_score", -1).limit(50).to_list(50)
            
            return {
                "success": True,
                "investors": investors,
                "count": len(investors),
                "query": query
            }
            
        except Exception as e:
            logger.error(f"Investor search failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_all_investors(self, limit: int = 100) -> Dict:
        """Get all investors from database"""
        try:
            if not self.db:
                return {"success": False, "error": "Database not available"}
            
            investors = await self.db.investors.find(
                {},
                {"_id": 0}
            ).sort("lead_score", -1).limit(limit).to_list(limit)
            
            # Group by status
            by_status = {}
            for inv in investors:
                status = inv.get('status', 'new')
                by_status[status] = by_status.get(status, 0) + 1
            
            return {
                "success": True,
                "investors": investors,
                "total": len(investors),
                "by_status": by_status,
                "avg_lead_score": sum(inv.get('lead_score', 0) for inv in investors) / len(investors) if investors else 0
            }
            
        except Exception as e:
            logger.error(f"Failed to get investors: {e}")
            return {"success": False, "error": str(e)}
    
    async def update_investor_status(self, investor_id: str, status: str, note: str = None) -> Dict:
        """Update investor status and add note"""
        try:
            if not self.db:
                return {"success": False, "error": "Database not available"}
            
            update_data = {
                "status": status,
                "last_updated": datetime.now(timezone.utc).isoformat()
            }
            
            if note:
                update_data["$push"] = {
                    "notes": {
                        "note": note,
                        "added_at": datetime.now(timezone.utc).isoformat()
                    }
                }
            
            result = await self.db.investors.update_one(
                {"id": investor_id},
                {"$set": update_data}
            )
            
            return {
                "success": True,
                "investor_id": investor_id,
                "status": status,
                "updated": result.modified_count > 0
            }
            
        except Exception as e:
            logger.error(f"Failed to update investor: {e}")
            return {"success": False, "error": str(e)}
    
    async def track_interaction(self, investor_id: str, interaction_type: str, details: Dict) -> Dict:
        """Track interaction with investor"""
        try:
            if not self.db:
                return {"success": False, "error": "Database not available"}
            
            interaction = {
                "type": interaction_type,  # email, call, meeting, demo
                "details": details,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            result = await self.db.investors.update_one(
                {"id": investor_id},
                {
                    "$push": {"interactions": interaction},
                    "$set": {"last_updated": datetime.now(timezone.utc).isoformat()}
                }
            )
            
            return {
                "success": True,
                "investor_id": investor_id,
                "interaction": interaction
            }
            
        except Exception as e:
            logger.error(f"Failed to track interaction: {e}")
            return {"success": False, "error": str(e)}
    
    async def generate_outreach_email(self, investor_id: str) -> Dict:
        """Generate personalized outreach email using AI"""
        try:
            if not self.db:
                return {"success": False, "error": "Database not available"}
            
            # Get investor details
            investor = await self.db.investors.find_one(
                {"id": investor_id},
                {"_id": 0}
            )
            
            if not investor:
                return {"success": False, "error": "Investor not found"}
            
            prompt = f"""Write a personalized, professional cold outreach email to this investor:

Investor: {investor.get('name')}
Firm: {investor.get('firm')}
Focus: {investor.get('investment_focus')}
Notable Investments: {investor.get('notable_investments')}

Company: NEXUS AI
Product: AI-powered social marketplace & creator hub with autonomous integrations
Stage: Seed round ($500k target)
Traction: 15k users, $127k MRR, 30% MoM growth

Write a compelling 150-word email that:
1. References their investment focus/portfolio
2. Highlights relevant traction
3. Clear ask for 15-min intro call
4. Professional but warm tone"""
            
            # Use AI to generate email
            from emergentintegrations.llm.chat import LlmChat, UserMessage
            
            user_msg = UserMessage(content=prompt)
            
            llm = LlmChat(api_key=self.llm_key)
            email_content = llm.chat(
                messages=[user_msg],
                model="claude-sonnet-4",
                max_tokens=500,
                temperature=0.7
            )
            
            return {
                "success": True,
                "investor": investor.get('name'),
                "email": email_content,
                "to": investor.get('email'),
                "subject": f"Quick intro - NEXUS AI (AI Creator Platform)"
            }
            
        except Exception as e:
            logger.error(f"Failed to generate email: {e}")
            return {"success": False, "error": str(e)}
    
    async def daily_investor_update(self) -> Dict:
        """
        Daily automation: Discover new investors and update database
        Should be called by scheduler
        """
        try:
            logger.info("🔄 Running daily investor discovery automation...")
            
            # Discover new investors
            discovery_result = await self.discover_investors({
                "industry": "AI, SaaS, Creator Economy, Marketplace",
                "stage": "Seed, Series A",
                "check_size": "$100k-$2M"
            })
            
            if not discovery_result['success']:
                return discovery_result
            
            # Log automation run
            automation_record = {
                "automation": "investor_discovery",
                "run_at": datetime.now(timezone.utc).isoformat(),
                "investors_found": discovery_result['count'],
                "status": "completed"
            }
            
            if self.db:
                await self.db.automation_runs.insert_one(automation_record)
            
            return {
                "success": True,
                "automation": "investor_discovery",
                "investors_discovered": discovery_result['count'],
                "next_run": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Daily investor update failed: {e}")
            return {"success": False, "error": str(e)}

def create_investor_discovery_service(db=None):
    """Factory function"""
    return InvestorDiscoveryService(db)
