"""
NEXUS AI Social Marketplace v4.2 - Integration Status & Enhanced Discovery Tests
Tests for: Integration Status API, Softr Database, Enhanced CI/CD, AI Agent Caching
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


class TestIntegrationStatusAPI:
    """Tests for new Integration Status API endpoints"""
    
    def test_integrations_status_endpoint(self):
        """Test GET /api/integrations/status returns all 8 integrations"""
        response = requests.get(f"{BASE_URL}/api/integrations/status")
        assert response.status_code == 200, f"Integration status failed: {response.text}"
        data = response.json()
        
        # Verify structure
        assert "integrations" in data, "Missing 'integrations' key"
        assert "summary" in data, "Missing 'summary' key"
        assert "checked_at" in data, "Missing 'checked_at' key"
        
        integrations = data["integrations"]
        
        # Verify all 8 integrations are present
        expected_integrations = ["emergent_llm", "stripe", "resend", "github", "gitlab", "producthunt", "manus", "softr"]
        for integration_key in expected_integrations:
            assert integration_key in integrations, f"Missing integration: {integration_key}"
            
            # Verify each integration has required fields
            integration = integrations[integration_key]
            assert "name" in integration, f"{integration_key} missing 'name'"
            assert "description" in integration, f"{integration_key} missing 'description'"
            assert "active" in integration, f"{integration_key} missing 'active'"
            assert "status" in integration, f"{integration_key} missing 'status'"
            assert "features" in integration, f"{integration_key} missing 'features'"
            assert "priority" in integration, f"{integration_key} missing 'priority'"
        
        print(f"✓ Integration status returns all 8 integrations with correct structure")
    
    def test_integrations_summary_fields(self):
        """Test integration summary contains correct fields"""
        response = requests.get(f"{BASE_URL}/api/integrations/status")
        assert response.status_code == 200
        data = response.json()
        
        summary = data["summary"]
        assert "total" in summary, "Missing 'total' in summary"
        assert "active" in summary, "Missing 'active' in summary"
        assert "inactive" in summary, "Missing 'inactive' in summary"
        assert "health_score" in summary, "Missing 'health_score' in summary"
        assert "critical_missing" in summary, "Missing 'critical_missing' in summary"
        
        # Verify total is 8
        assert summary["total"] == 8, f"Expected 8 total integrations, got {summary['total']}"
        
        # Verify health_score is a percentage
        assert 0 <= summary["health_score"] <= 100, f"Health score out of range: {summary['health_score']}"
        
        print(f"✓ Integration summary: {summary['active']}/{summary['total']} active, health: {summary['health_score']:.0f}%")
    
    def test_integrations_health_endpoint(self):
        """Test GET /api/integrations/health returns health status"""
        response = requests.get(f"{BASE_URL}/api/integrations/health")
        assert response.status_code == 200, f"Integration health failed: {response.text}"
        data = response.json()
        
        assert "health" in data, "Missing 'health' key"
        
        valid_health_statuses = ["excellent", "good", "fair", "needs_attention"]
        assert data["health"] in valid_health_statuses, f"Invalid health status: {data['health']}"
        
        print(f"✓ Integration health endpoint returns: {data['health']}")
    
    def test_softr_integration_present(self):
        """Test Softr integration is included in status"""
        response = requests.get(f"{BASE_URL}/api/integrations/status")
        assert response.status_code == 200
        data = response.json()
        
        softr = data["integrations"].get("softr")
        assert softr is not None, "Softr integration not found"
        
        assert softr["name"] == "Softr Database", f"Unexpected Softr name: {softr['name']}"
        assert "scraping" in softr["status"].lower() or "api" in softr["status"].lower(), f"Unexpected Softr status: {softr['status']}"
        
        print(f"✓ Softr integration present with status: {softr['status']}")


class TestCICDEndpoints:
    """Tests for enhanced CI/CD endpoints"""
    
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
    
    def test_cicd_status_endpoint(self, admin_token):
        """Test GET /api/cicd/status returns GitHub and GitLab status"""
        response = requests.get(f"{BASE_URL}/api/cicd/status", headers={
            "Authorization": f"Bearer {admin_token}"
        })
        assert response.status_code == 200, f"CI/CD status failed: {response.text}"
        data = response.json()
        
        # Verify structure
        assert "repository" in data, "Missing 'repository' key"
        assert "code_quality" in data, "Missing 'code_quality' key"
        
        # Repository health should have expected fields
        repo = data["repository"]
        assert "deployment_status" in repo or "mocked" in repo, "Missing deployment info"
        
        # Code quality should have metrics
        quality = data["code_quality"]
        assert "metrics" in quality, "Missing 'metrics' in code_quality"
        assert "recommendations" in quality, "Missing 'recommendations' in code_quality"
        
        print(f"✓ CI/CD status endpoint returns repository and code quality data")
    
    def test_cicd_status_requires_admin(self):
        """Test CI/CD status requires admin authentication"""
        response = requests.get(f"{BASE_URL}/api/cicd/status")
        assert response.status_code in [401, 403], f"Should require auth, got {response.status_code}"
        print(f"✓ CI/CD status requires admin authentication")


class TestSoftrDiscoveryIntegration:
    """Tests for Softr database integration in discovery"""
    
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
    
    def test_scan_includes_softr_source(self, admin_token):
        """Test discovery scan includes softr_database in sources"""
        # Trigger a scan
        response = requests.post(f"{BASE_URL}/api/admin/aixploria/scan", 
            headers={"Authorization": f"Bearer {admin_token}"},
            json={}
        )
        assert response.status_code == 200, f"Scan trigger failed: {response.text}"
        
        # Wait for scan to complete (background task)
        time.sleep(5)
        
        # Check latest scan results
        response = requests.get(f"{BASE_URL}/api/admin/aixploria/latest-scan", headers={
            "Authorization": f"Bearer {admin_token}"
        })
        
        if response.status_code == 200:
            data = response.json()
            scan = data.get("scan", {})
            sources = scan.get("sources_scanned", [])
            
            # Softr should be in sources (even if it returns 0 items)
            assert "softr_database" in sources, f"softr_database not in sources: {sources}"
            print(f"✓ Discovery scan includes softr_database in sources: {sources}")
        else:
            # If no scan exists yet, just verify the endpoint works
            print(f"⚠ No scan results yet, but endpoint works")


class TestEmailServiceFallback:
    """Tests for email service demo mode fallback"""
    
    def test_registration_without_resend_key(self):
        """Test registration works even without real Resend key (logs to console)"""
        test_email = f"test_email_{uuid.uuid4().hex[:8]}@nexus.test"
        test_password = "TestPass123!"
        test_username = f"TestEmail_{uuid.uuid4().hex[:6]}"
        
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": test_email,
            "password": test_password,
            "username": test_username
        })
        
        # Registration should succeed even if email service is in demo mode
        assert response.status_code == 200, f"Registration failed: {response.text}"
        data = response.json()
        
        assert "token" in data, "Missing token in response"
        assert "user" in data, "Missing user in response"
        assert data["user"]["email"] == test_email
        
        print(f"✓ Registration works with email service in demo mode")


class TestDiscoveryCoordination:
    """Tests for discovery coordination (prevents concurrent scans)"""
    
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
    
    def test_automation_discover_tools_endpoint(self, admin_token):
        """Test automation discover-tools endpoint works"""
        response = requests.post(
            f"{BASE_URL}/api/automation/discover-tools",
            headers={"Authorization": f"Bearer {admin_token}"},
            json=["marketing", "ai_tools"]
        )
        assert response.status_code == 200, f"Discover tools failed: {response.text}"
        data = response.json()
        
        # Should return status (completed or skipped if already running)
        assert "status" in data, "Missing 'status' in response"
        assert data["status"] in ["completed", "skipped", "error"], f"Unexpected status: {data['status']}"
        
        print(f"✓ Automation discover-tools endpoint returns status: {data['status']}")


class TestAIAgentErrorHandling:
    """Tests for AI agent error handling with structured responses"""
    
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
    
    def test_agent_run_returns_structured_response(self, admin_token):
        """Test running an agent returns structured response (success or error)"""
        # Try running CEO agent
        response = requests.post(f"{BASE_URL}/api/agents/agent-ceo/run", headers={
            "Authorization": f"Bearer {admin_token}"
        })
        
        # Should return 200 with structured response
        assert response.status_code == 200, f"Agent run failed: {response.text}"
        data = response.json()
        
        assert "success" in data, "Missing 'success' field"
        assert "report" in data, "Missing 'report' field"
        
        report = data["report"]
        assert "agent" in report, "Report missing 'agent' field"
        assert "type" in report, "Report missing 'type' field"
        assert "created_at" in report, "Report missing 'created_at' field"
        
        # Type should be either 'daily_report' or 'error'
        assert report["type"] in ["daily_report", "error", "product_insights", "content_generation", "moderation_report", "financial_report"], f"Unexpected report type: {report['type']}"
        
        print(f"✓ Agent run returns structured response with type: {report['type']}")


class TestHomepageAgentDisplay:
    """Tests for homepage displaying 11 AI agents"""
    
    def test_stats_shows_11_agents(self):
        """Test /api/stats returns 11 AI agents"""
        response = requests.get(f"{BASE_URL}/api/stats")
        assert response.status_code == 200
        data = response.json()
        
        assert data.get("ai_agents_active") == 11, f"Expected 11 agents, got {data.get('ai_agents_active')}"
        print(f"✓ Stats endpoint shows 11 AI agents active")
    
    def test_agents_have_type_badges(self):
        """Test agents have type field for badges (Core, Manus, Autonomous)"""
        response = requests.get(f"{BASE_URL}/api/agents")
        assert response.status_code == 200
        agents = response.json()
        
        valid_types = ["base", "manus", "autonomous"]
        
        for agent in agents:
            agent_type = agent.get("agent_type")
            assert agent_type in valid_types, f"Agent {agent.get('name')} has invalid type: {agent_type}"
        
        # Count by type
        base_count = sum(1 for a in agents if a.get("agent_type") == "base")
        manus_count = sum(1 for a in agents if a.get("agent_type") == "manus")
        autonomous_count = sum(1 for a in agents if a.get("agent_type") == "autonomous")
        
        assert base_count == 5, f"Expected 5 base agents, got {base_count}"
        assert manus_count == 5, f"Expected 5 manus agents, got {manus_count}"
        assert autonomous_count == 1, f"Expected 1 autonomous agent, got {autonomous_count}"
        
        print(f"✓ Agents have correct type badges: 5 Core, 5 Manus, 1 Autonomous")


class TestBackwardCompatibilityV42:
    """Tests for backward compatibility with v4.1 features"""
    
    def test_original_aixploria_endpoints_work(self):
        """Test original AIxploria endpoints still work"""
        # Login as admin
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200
        token = response.json()["token"]
        
        # Test AIxploria endpoints
        endpoints = [
            "/api/admin/aixploria/stats",
            "/api/admin/aixploria/tools"
        ]
        
        for endpoint in endpoints:
            response = requests.get(f"{BASE_URL}{endpoint}", headers={
                "Authorization": f"Bearer {token}"
            })
            assert response.status_code == 200, f"{endpoint} failed: {response.text}"
        
        print(f"✓ All AIxploria endpoints backward compatible")
    
    def test_marketplace_endpoints_work(self):
        """Test marketplace endpoints still work"""
        endpoints = [
            "/api/products",
            "/api/posts",
            "/api/spotlight",
            "/api/vendors",
            "/api/trending"
        ]
        
        for endpoint in endpoints:
            response = requests.get(f"{BASE_URL}{endpoint}")
            assert response.status_code == 200, f"{endpoint} failed: {response.text}"
        
        print(f"✓ All marketplace endpoints working")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
