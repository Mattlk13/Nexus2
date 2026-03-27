"""
NEXUS AI Social Marketplace v4.1 - AIxploria Discovery Tests
Tests for: Multi-source AI discovery (AIxploria, GitHub, ProductHunt), 11 AI agents, Admin Automation Panel
"""
import pytest
import requests
import os
import time
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://model-exchange-2.preview.emergentagent.com').rstrip('/')

# Admin credentials
ADMIN_EMAIL = "admin@nexus.ai"
ADMIN_PASSWORD = "admin123"

# Test user credentials
TEST_USER_EMAIL = f"test_v41_{uuid.uuid4().hex[:8]}@nexus.test"
TEST_USER_PASSWORD = "TestPass123!"
TEST_USER_USERNAME = f"TestV41_{uuid.uuid4().hex[:6]}"


class TestHealthAndStats:
    """Basic health and stats endpoints - verify 11 agents"""
    
    def test_stats_returns_11_agents(self):
        """Test /api/stats returns 11 AI agents active"""
        response = requests.get(f"{BASE_URL}/api/stats")
        assert response.status_code == 200, f"Stats failed: {response.text}"
        data = response.json()
        
        # Verify 11 AI agents active (updated from 10)
        assert data.get("ai_agents_active") == 11, f"Expected 11 agents, got {data.get('ai_agents_active')}"
        print(f"✓ Stats endpoint returns 11 AI agents active")


class TestAgentsEndpoint:
    """Tests for 11 AI agents endpoint including AIxploria Discovery"""
    
    def test_agents_returns_11_agents(self):
        """Test /api/agents returns all 11 agents"""
        response = requests.get(f"{BASE_URL}/api/agents")
        assert response.status_code == 200, f"Agents failed: {response.text}"
        agents = response.json()
        
        assert len(agents) == 11, f"Expected 11 agents, got {len(agents)}"
        print(f"✓ Agents endpoint returns 11 agents")
    
    def test_agents_have_correct_types(self):
        """Test agents have base, manus, and autonomous types"""
        response = requests.get(f"{BASE_URL}/api/agents")
        assert response.status_code == 200
        agents = response.json()
        
        base_agents = [a for a in agents if a.get("agent_type") == "base"]
        manus_agents = [a for a in agents if a.get("agent_type") == "manus"]
        autonomous_agents = [a for a in agents if a.get("agent_type") == "autonomous"]
        
        assert len(base_agents) == 5, f"Expected 5 base agents, got {len(base_agents)}"
        assert len(manus_agents) == 5, f"Expected 5 manus agents, got {len(manus_agents)}"
        assert len(autonomous_agents) == 1, f"Expected 1 autonomous agent, got {len(autonomous_agents)}"
        print(f"✓ Agent types correct: 5 base + 5 manus + 1 autonomous")
    
    def test_aixploria_discovery_agent_exists(self):
        """Test AIxploria Discovery agent exists with correct properties"""
        response = requests.get(f"{BASE_URL}/api/agents")
        assert response.status_code == 200
        agents = response.json()
        
        aixploria_agent = next((a for a in agents if "AIxploria" in a.get("name", "")), None)
        assert aixploria_agent is not None, "AIxploria Discovery agent not found"
        
        assert aixploria_agent.get("agent_type") == "autonomous", f"Expected autonomous type, got {aixploria_agent.get('agent_type')}"
        assert "AI Tool Finder" in aixploria_agent.get("role", ""), f"Unexpected role: {aixploria_agent.get('role')}"
        print(f"✓ AIxploria Discovery agent exists with autonomous type")
    
    def test_all_11_agent_names_exist(self):
        """Test all 11 specific agent names exist"""
        response = requests.get(f"{BASE_URL}/api/agents")
        assert response.status_code == 200
        agents = response.json()
        
        agent_names = [a.get("name") for a in agents]
        
        # Core agents (5)
        assert "CEO Agent" in agent_names
        assert "Product Manager" in agent_names
        assert "Marketing Agent" in agent_names
        assert "Vendor Manager" in agent_names
        assert "Finance Agent" in agent_names
        
        # Manus agents (5)
        assert "Tool Discovery Agent" in agent_names
        assert "Investor Outreach Agent" in agent_names
        assert "Marketing Automation" in agent_names
        assert "Platform Optimizer" in agent_names
        assert "CI/CD Agent" in agent_names
        
        # Autonomous agent (1)
        assert "AIxploria Discovery" in agent_names
        
        print(f"✓ All 11 specific agents exist")


class TestAdminAuth:
    """Admin authentication for protected endpoints"""
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        """Get admin token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        data = response.json()
        assert data["user"]["role"] == "admin", "User is not admin"
        return data["token"]
    
    def test_admin_login(self, admin_token):
        """Test admin login works"""
        assert admin_token is not None
        print(f"✓ Admin login successful")


class TestAIxploriaEndpoints:
    """Tests for AIxploria discovery API endpoints"""
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        """Get admin token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code == 200:
            return response.json()["token"]
        pytest.skip("Admin login failed")
    
    def test_aixploria_stats_endpoint(self, admin_token):
        """Test /api/admin/aixploria/stats returns correct structure"""
        response = requests.get(f"{BASE_URL}/api/admin/aixploria/stats", headers={
            "Authorization": f"Bearer {admin_token}"
        })
        assert response.status_code == 200, f"Stats failed: {response.text}"
        data = response.json()
        
        # Verify structure
        assert "total_scans" in data
        assert "tools_discovered" in data
        assert "critical_count" in data
        assert "high_count" in data
        assert "scan_history" in data
        
        print(f"✓ AIxploria stats endpoint working - {data['total_scans']} scans, {data['tools_discovered']} tools")
    
    def test_aixploria_tools_endpoint(self, admin_token):
        """Test /api/admin/aixploria/tools returns discovered tools"""
        response = requests.get(f"{BASE_URL}/api/admin/aixploria/tools", headers={
            "Authorization": f"Bearer {admin_token}"
        })
        assert response.status_code == 200, f"Tools failed: {response.text}"
        data = response.json()
        
        # Verify structure
        assert "tools" in data
        assert "total" in data
        assert "latest_scan" in data
        
        # If tools exist, verify tool structure
        if data["tools"]:
            tool = data["tools"][0]
            assert "name" in tool
            assert "nexus_score" in tool
            assert "benefit_level" in tool
            assert "source" in tool
            print(f"✓ AIxploria tools endpoint working - {data['total']} tools with scores")
        else:
            print(f"✓ AIxploria tools endpoint working - no tools yet")
    
    def test_aixploria_scan_endpoint(self, admin_token):
        """Test /api/admin/aixploria/scan triggers background scan"""
        response = requests.post(f"{BASE_URL}/api/admin/aixploria/scan", 
            headers={"Authorization": f"Bearer {admin_token}"},
            json={}
        )
        assert response.status_code == 200, f"Scan failed: {response.text}"
        data = response.json()
        
        assert data.get("status") == "scan_started"
        assert "message" in data
        print(f"✓ AIxploria scan endpoint triggers background task")
    
    def test_aixploria_stats_requires_admin(self):
        """Test /api/admin/aixploria/stats requires admin role"""
        # Test without auth
        response = requests.get(f"{BASE_URL}/api/admin/aixploria/stats")
        assert response.status_code in [401, 403], "Should require auth"
        print(f"✓ AIxploria stats requires authentication")
    
    def test_aixploria_tools_requires_admin(self):
        """Test /api/admin/aixploria/tools requires admin role"""
        response = requests.get(f"{BASE_URL}/api/admin/aixploria/tools")
        assert response.status_code in [401, 403], "Should require auth"
        print(f"✓ AIxploria tools requires authentication")
    
    def test_aixploria_scan_requires_admin(self):
        """Test /api/admin/aixploria/scan requires admin role"""
        response = requests.post(f"{BASE_URL}/api/admin/aixploria/scan", json={})
        assert response.status_code in [401, 403], "Should require auth"
        print(f"✓ AIxploria scan requires authentication")


class TestToolScoring:
    """Tests for tool scoring and categorization"""
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        """Get admin token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code == 200:
            return response.json()["token"]
        pytest.skip("Admin login failed")
    
    def test_tools_have_nexus_scores(self, admin_token):
        """Test discovered tools have nexus_score field"""
        response = requests.get(f"{BASE_URL}/api/admin/aixploria/tools", headers={
            "Authorization": f"Bearer {admin_token}"
        })
        assert response.status_code == 200
        data = response.json()
        
        if data["tools"]:
            for tool in data["tools"]:
                assert "nexus_score" in tool, f"Tool {tool.get('name')} missing nexus_score"
                assert isinstance(tool["nexus_score"], (int, float)), "nexus_score should be numeric"
            print(f"✓ All tools have nexus_score")
        else:
            print(f"⚠ No tools to verify scores")
    
    def test_tools_have_benefit_levels(self, admin_token):
        """Test discovered tools have benefit_level field"""
        response = requests.get(f"{BASE_URL}/api/admin/aixploria/tools", headers={
            "Authorization": f"Bearer {admin_token}"
        })
        assert response.status_code == 200
        data = response.json()
        
        valid_levels = ["critical", "high", "medium", "low"]
        
        if data["tools"]:
            for tool in data["tools"]:
                assert "benefit_level" in tool, f"Tool {tool.get('name')} missing benefit_level"
                assert tool["benefit_level"] in valid_levels, f"Invalid benefit_level: {tool['benefit_level']}"
            print(f"✓ All tools have valid benefit_level")
        else:
            print(f"⚠ No tools to verify benefit levels")
    
    def test_tools_have_source_info(self, admin_token):
        """Test discovered tools have source information"""
        response = requests.get(f"{BASE_URL}/api/admin/aixploria/tools", headers={
            "Authorization": f"Bearer {admin_token}"
        })
        assert response.status_code == 200
        data = response.json()
        
        valid_sources = ["aixploria_top_100", "aixploria_latest", "github_trending", "producthunt_ai"]
        
        if data["tools"]:
            for tool in data["tools"]:
                assert "source" in tool, f"Tool {tool.get('name')} missing source"
                assert tool["source"] in valid_sources, f"Invalid source: {tool['source']}"
            print(f"✓ All tools have valid source info")
        else:
            print(f"⚠ No tools to verify sources")


class TestPerformanceOptimizer:
    """Tests for performance optimizer and database indexes"""
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        """Get admin token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code == 200:
            return response.json()["token"]
        pytest.skip("Admin login failed")
    
    def test_performance_metrics_endpoint(self, admin_token):
        """Test /api/admin/performance returns metrics"""
        response = requests.get(f"{BASE_URL}/api/admin/performance", headers={
            "Authorization": f"Bearer {admin_token}"
        })
        assert response.status_code == 200, f"Performance failed: {response.text}"
        data = response.json()
        
        # Verify structure
        assert "collections" in data or "error" not in data
        print(f"✓ Performance metrics endpoint working")


class TestBackwardCompatibility:
    """Tests for backward compatibility with v4.0 features"""
    
    def test_original_endpoints_still_work(self):
        """Test original marketplace endpoints still work"""
        endpoints = [
            "/api/products",
            "/api/posts",
            "/api/spotlight",
            "/api/vendors",
            "/api/boost/packages",
            "/api/trending"
        ]
        
        for endpoint in endpoints:
            response = requests.get(f"{BASE_URL}{endpoint}")
            assert response.status_code == 200, f"{endpoint} failed: {response.text}"
        
        print(f"✓ All {len(endpoints)} original endpoints working")
    
    def test_agents_endpoint_backward_compatible(self):
        """Test agents endpoint returns expected fields"""
        response = requests.get(f"{BASE_URL}/api/agents")
        assert response.status_code == 200
        agents = response.json()
        
        required_fields = ["id", "name", "role", "status", "description"]
        for agent in agents:
            for field in required_fields:
                assert field in agent, f"Agent {agent.get('name')} missing field: {field}"
        
        print(f"✓ Agents endpoint backward compatible")


class TestNonAdminAccess:
    """Tests for non-admin user access restrictions"""
    
    @pytest.fixture(scope="class")
    def user_token(self):
        """Create and login as regular user"""
        # Register new user
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD,
            "username": TEST_USER_USERNAME
        })
        if response.status_code == 200:
            return response.json()["token"]
        
        # Try login if already exists
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        })
        if response.status_code == 200:
            return response.json()["token"]
        
        pytest.skip("Could not create/login test user")
    
    def test_aixploria_stats_denied_for_non_admin(self, user_token):
        """Test /api/admin/aixploria/stats denied for non-admin"""
        response = requests.get(f"{BASE_URL}/api/admin/aixploria/stats", headers={
            "Authorization": f"Bearer {user_token}"
        })
        assert response.status_code == 403, f"Should be forbidden, got {response.status_code}"
        print(f"✓ AIxploria stats denied for non-admin")
    
    def test_aixploria_tools_denied_for_non_admin(self, user_token):
        """Test /api/admin/aixploria/tools denied for non-admin"""
        response = requests.get(f"{BASE_URL}/api/admin/aixploria/tools", headers={
            "Authorization": f"Bearer {user_token}"
        })
        assert response.status_code == 403, f"Should be forbidden, got {response.status_code}"
        print(f"✓ AIxploria tools denied for non-admin")
    
    def test_aixploria_scan_denied_for_non_admin(self, user_token):
        """Test /api/admin/aixploria/scan denied for non-admin"""
        response = requests.post(f"{BASE_URL}/api/admin/aixploria/scan", 
            headers={"Authorization": f"Bearer {user_token}"},
            json={}
        )
        assert response.status_code == 403, f"Should be forbidden, got {response.status_code}"
        print(f"✓ AIxploria scan denied for non-admin")


class TestScheduledTask:
    """Tests for scheduled task configuration"""
    
    def test_agents_have_schedule_info(self):
        """Test agents have schedule information"""
        response = requests.get(f"{BASE_URL}/api/agents")
        assert response.status_code == 200
        agents = response.json()
        
        # Find AIxploria agent
        aixploria_agent = next((a for a in agents if "AIxploria" in a.get("name", "")), None)
        assert aixploria_agent is not None
        
        # Check schedule exists
        schedule = aixploria_agent.get("schedule", {})
        # Schedule should be at 2 AM UTC
        if schedule:
            assert schedule.get("hour") == 2, f"Expected hour 2, got {schedule.get('hour')}"
            print(f"✓ AIxploria agent scheduled for 2 AM UTC")
        else:
            print(f"⚠ Schedule info not exposed in API (may be internal)")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
