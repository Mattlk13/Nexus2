"""
NEXUS Automated Testing System
Comprehensive test suite that runs on task completion

Tests all features:
- Storage backends
- Hybrid services
- API endpoints
- Dashboards
- Integrations
"""

import asyncio
import logging
from typing import Dict, List
from datetime import datetime, timezone
import aiohttp

logger = logging.getLogger(__name__)

class AutomatedTestSuite:
    def __init__(self, base_url: str, admin_token: str):
        """Initialize test suite"""
        self.base_url = base_url
        self.admin_token = admin_token
        self.results = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "tests": [],
            "summary": {}
        }
    
    async def test_endpoint(self, method: str, endpoint: str, data: dict = None) -> Dict:
        """Test a single API endpoint"""
        try:
            headers = {
                "Authorization": f"Bearer {self.admin_token}",
                "Content-Type": "application/json"
            }
            
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}{endpoint}"
                
                if method == "GET":
                    async with session.get(url, headers=headers) as response:
                        result = await response.json()
                        return {
                            "success": response.status == 200,
                            "status": response.status,
                            "result": result
                        }
                elif method == "POST":
                    async with session.post(url, headers=headers, json=data) as response:
                        result = await response.json()
                        return {
                            "success": response.status == 200,
                            "status": response.status,
                            "result": result
                        }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def run_storage_tests(self):
        """Test storage backends"""
        logger.info("🗄️ Testing storage backends...")
        
        test = await self.test_endpoint("GET", "/api/hybrid/storage/status")
        
        self.results['tests'].append({
            "category": "Storage",
            "name": "Storage Status",
            "success": test['success'],
            "details": test.get('result', {})
        })
    
    async def run_controller_tests(self):
        """Test Ultimate Controller"""
        logger.info("🎛️ Testing Ultimate Controller...")
        
        # Test 1: System Status
        test1 = await self.test_endpoint("GET", "/api/hybrid/controller/status")
        self.results['tests'].append({
            "category": "Controller",
            "name": "System Status",
            "success": test1['success'],
            "hybrids": test1.get('result', {}).get('total_hybrids', 0)
        })
        
        # Test 2: Execute Task
        test2 = await self.test_endpoint("POST", "/api/hybrid/controller/execute", {
            "task": "test task",
            "auto_route": True
        })
        self.results['tests'].append({
            "category": "Controller",
            "name": "Execute Task",
            "success": test2['success']
        })
    
    async def run_music_tests(self):
        """Test Music Hybrid"""
        logger.info("🎵 Testing Music Hybrid...")
        
        test = await self.test_endpoint("GET", "/api/hybrid/music/capabilities")
        self.results['tests'].append({
            "category": "Music",
            "name": "Get Capabilities",
            "success": test['success']
        })
    
    async def run_mcp_tests(self):
        """Test MCP Hybrid"""
        logger.info("🔌 Testing MCP Hybrid...")
        
        # Test 1: Discover MCP Servers
        test1 = await self.test_endpoint("GET", "/api/hybrid/mcp/discover")
        self.results['tests'].append({
            "category": "MCP",
            "name": "Discover Servers",
            "success": test1['success'],
            "servers": test1.get('result', {}).get('total_servers', 0)
        })
        
        # Test 2: Get Capabilities
        test2 = await self.test_endpoint("GET", "/api/hybrid/mcp/capabilities")
        self.results['tests'].append({
            "category": "MCP",
            "name": "Get Capabilities",
            "success": test2['success']
        })
    
    async def run_investor_tests(self):
        """Test Investor Dashboard & Discovery"""
        logger.info("💼 Testing Investor Dashboard...")
        
        tests = [
            ("Investor Overview", "GET", "/api/hybrid/investor/overview"),
            ("Revenue Breakdown", "GET", "/api/hybrid/investor/revenue"),
            ("User Analytics", "GET", "/api/hybrid/investor/users"),
            ("Investor Pipeline", "GET", "/api/hybrid/investor/pipeline"),
            ("Investor List", "GET", "/api/hybrid/investors/list")
        ]
        
        for name, method, endpoint in tests:
            test = await self.test_endpoint(method, endpoint)
            self.results['tests'].append({
                "category": "Investor",
                "name": name,
                "success": test['success']
            })
    
    async def run_marketing_tests(self):
        """Test Marketing Dashboard"""
        logger.info("📈 Testing Marketing Dashboard...")
        
        tests = [
            ("Campaigns", "GET", "/api/hybrid/marketing/campaigns"),
            ("Traffic", "GET", "/api/hybrid/marketing/traffic"),
            ("Funnel", "GET", "/api/hybrid/marketing/funnel"),
            ("SEO", "GET", "/api/hybrid/marketing/seo")
        ]
        
        for name, method, endpoint in tests:
            test = await self.test_endpoint(method, endpoint)
            self.results['tests'].append({
                "category": "Marketing",
                "name": name,
                "success": test['success']
            })
    
    async def run_core_features_tests(self):
        """Test core existing features"""
        logger.info("🎯 Testing core features...")
        
        tests = [
            ("Newsfeed", "GET", "/api/newsfeed/posts"),
            ("Marketplace", "GET", "/api/marketplace/products")
        ]
        
        for name, method, endpoint in tests:
            test = await self.test_endpoint(method, endpoint)
            self.results['tests'].append({
                "category": "Core",
                "name": name,
                "success": test['success']
            })
    
    async def run_all_tests(self):
        """Run complete test suite"""
        logger.info("🧪 Starting automated test suite...")
        
        # Run all test categories
        await self.run_storage_tests()
        await self.run_controller_tests()
        await self.run_music_tests()
        await self.run_mcp_tests()
        await self.run_investor_tests()
        await self.run_marketing_tests()
        await self.run_core_features_tests()
        
        # Calculate summary
        total = len(self.results['tests'])
        passed = sum(1 for test in self.results['tests'] if test['success'])
        failed = total - passed
        
        self.results['summary'] = {
            "total_tests": total,
            "passed": passed,
            "failed": failed,
            "pass_rate": round((passed / total * 100) if total > 0 else 0, 1)
        }
        
        logger.info(f"✅ Tests complete: {passed}/{total} passed ({self.results['summary']['pass_rate']}%)")
        
        return self.results

async def run_automated_tests(base_url: str, admin_token: str) -> Dict:
    """Run automated test suite"""
    suite = AutomatedTestSuite(base_url, admin_token)
    return await suite.run_all_tests()
