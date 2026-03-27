"""
NEXUS AI v4.3 Backend Tests
Tests for new features:
- OpenClaw integration endpoints
- Deep AIxploria comprehensive scan (65 categories)
- Integration status with 11 integrations
- ElevenLabs service demo mode
- Fal.ai service demo mode
- Softr Playwright scraping
"""

import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "admin@nexus.ai"
ADMIN_PASSWORD = "admin123"


class TestAuth:
    """Authentication tests"""
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        """Get admin authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code == 200:
            return response.json().get("token")
        pytest.skip("Admin authentication failed")
    
    def test_admin_login(self):
        """Test admin login works"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert "user" in data
        assert data["user"]["role"] == "admin"
        print(f"✓ Admin login successful")


class TestOpenClawEndpoints:
    """OpenClaw autonomous agent endpoint tests"""
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        """Get admin authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code == 200:
            return response.json().get("token")
        pytest.skip("Admin authentication failed")
    
    def test_openclaw_status_endpoint(self, admin_token):
        """Test GET /api/admin/openclaw/status returns valid status"""
        response = requests.get(
            f"{BASE_URL}/api/admin/openclaw/status",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify required fields
        assert "status" in data
        assert "message" in data
        assert "installed" in data
        assert "running" in data
        
        # Status should be one of expected values
        valid_statuses = ["not_installed", "dependencies_missing", "not_built", "ready", "running", "error"]
        assert data["status"] in valid_statuses
        
        print(f"✓ OpenClaw status: {data['status']} - {data['message']}")
    
    def test_openclaw_analysis_endpoint(self, admin_token):
        """Test GET /api/admin/openclaw/analysis returns suggestions"""
        response = requests.get(
            f"{BASE_URL}/api/admin/openclaw/analysis",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify required fields
        assert "timestamp" in data
        assert "suggestions" in data
        assert "overall_health" in data
        assert "platform_score" in data
        
        # Verify suggestions structure
        assert isinstance(data["suggestions"], list)
        assert len(data["suggestions"]) > 0
        
        for suggestion in data["suggestions"]:
            assert "type" in suggestion
            assert "priority" in suggestion
            assert "title" in suggestion
            assert "description" in suggestion
        
        print(f"✓ OpenClaw analysis: {len(data['suggestions'])} suggestions, score: {data['platform_score']}")
    
    def test_openclaw_requires_admin(self):
        """Test OpenClaw endpoints require admin authentication"""
        # Without token
        response = requests.get(f"{BASE_URL}/api/admin/openclaw/status")
        assert response.status_code in [401, 403]
        
        # With invalid token
        response = requests.get(
            f"{BASE_URL}/api/admin/openclaw/status",
            headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code in [401, 403]
        
        print("✓ OpenClaw endpoints properly require admin auth")


class TestIntegrationStatus:
    """Integration status tests - verifying 11 integrations"""
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        """Get admin authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code == 200:
            return response.json().get("token")
        pytest.skip("Admin authentication failed")
    
    def test_integration_status_returns_11_integrations(self, admin_token):
        """Test /api/integrations/status returns all 11 integrations"""
        response = requests.get(
            f"{BASE_URL}/api/integrations/status",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify structure
        assert "integrations" in data
        assert "summary" in data
        
        integrations = data["integrations"]
        
        # v4.3 should have 11 integrations (was 8 in v4.2)
        expected_integrations = [
            "emergent_llm", "stripe", "resend", "github", "gitlab",
            "producthunt", "manus", "softr", "elevenlabs", "fal_ai", "openclaw"
        ]
        
        for integration_key in expected_integrations:
            assert integration_key in integrations, f"Missing integration: {integration_key}"
            integration = integrations[integration_key]
            assert "name" in integration
            assert "status" in integration
            assert "active" in integration
        
        # Verify summary
        summary = data["summary"]
        assert summary["total"] == 11, f"Expected 11 integrations, got {summary['total']}"
        assert "health_score" in summary
        assert "active" in summary
        
        print(f"✓ Integration status: {summary['total']} integrations, {summary['active']} active, health: {summary['health_score']:.1f}%")
    
    def test_elevenlabs_integration_present(self, admin_token):
        """Test ElevenLabs integration is in status"""
        response = requests.get(
            f"{BASE_URL}/api/integrations/status",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "elevenlabs" in data["integrations"]
        elevenlabs = data["integrations"]["elevenlabs"]
        
        assert elevenlabs["name"] == "ElevenLabs Voice"
        assert "Voice generation" in elevenlabs["features"]
        
        print(f"✓ ElevenLabs integration: status={elevenlabs['status']}, active={elevenlabs['active']}")
    
    def test_fal_ai_integration_present(self, admin_token):
        """Test Fal.ai integration is in status"""
        response = requests.get(
            f"{BASE_URL}/api/integrations/status",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "fal_ai" in data["integrations"]
        fal_ai = data["integrations"]["fal_ai"]
        
        assert fal_ai["name"] == "Fal.ai Images"
        assert "FLUX image generation" in fal_ai["features"]
        
        print(f"✓ Fal.ai integration: status={fal_ai['status']}, active={fal_ai['active']}")
    
    def test_openclaw_integration_present(self, admin_token):
        """Test OpenClaw integration is in status"""
        response = requests.get(
            f"{BASE_URL}/api/integrations/status",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "openclaw" in data["integrations"]
        openclaw = data["integrations"]["openclaw"]
        
        assert openclaw["name"] == "OpenClaw Agent"
        assert "Code analysis" in openclaw["features"]
        
        print(f"✓ OpenClaw integration: status={openclaw['status']}, active={openclaw['active']}")
    
    def test_integration_health_endpoint(self, admin_token):
        """Test /api/integrations/health returns health status"""
        response = requests.get(
            f"{BASE_URL}/api/integrations/health",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "health" in data
        valid_health = ["excellent", "good", "fair", "needs_attention"]
        assert data["health"] in valid_health
        
        print(f"✓ Integration health: {data['health']}")


class TestAIxploriaDeepScan:
    """AIxploria deep scan tests - 65 categories"""
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        """Get admin authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code == 200:
            return response.json().get("token")
        pytest.skip("Admin authentication failed")
    
    def test_aixploria_scan_endpoint_exists(self, admin_token):
        """Test AIxploria scan endpoint accepts comprehensive parameter"""
        # Test standard scan (don't actually run, just verify endpoint)
        response = requests.post(
            f"{BASE_URL}/api/admin/aixploria/scan",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "status" in data
        assert data["status"] == "scan_started"
        assert "estimated_time" in data
        
        print(f"✓ AIxploria scan endpoint working: {data['message']}")
    
    def test_aixploria_comprehensive_scan_parameter(self, admin_token):
        """Test comprehensive scan parameter is accepted"""
        response = requests.post(
            f"{BASE_URL}/api/admin/aixploria/scan?comprehensive=true",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Comprehensive scan should mention all categories
        assert "comprehensive" in data.get("message", "").lower() or "50+" in data.get("message", "")
        
        print(f"✓ Comprehensive scan accepted: {data['estimated_time']}")
    
    def test_aixploria_tools_endpoint(self, admin_token):
        """Test GET /api/admin/aixploria/tools returns discovered tools"""
        response = requests.get(
            f"{BASE_URL}/api/admin/aixploria/tools",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "tools" in data
        assert "total" in data
        
        # If tools exist, verify structure
        if data["tools"]:
            tool = data["tools"][0]
            # Tools should have these fields from categorization
            expected_fields = ["name", "nexus_score", "benefit_level"]
            for field in expected_fields:
                assert field in tool, f"Tool missing field: {field}"
        
        print(f"✓ AIxploria tools: {data['total']} tools discovered")
    
    def test_aixploria_stats_endpoint(self, admin_token):
        """Test GET /api/admin/aixploria/stats returns scan statistics"""
        response = requests.get(
            f"{BASE_URL}/api/admin/aixploria/stats",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "total_scans" in data
        assert "tools_discovered" in data or "total_scans" in data
        
        print(f"✓ AIxploria stats: {data.get('total_scans', 0)} scans, {data.get('tools_discovered', 0)} tools")


class TestElevenLabsDemoMode:
    """ElevenLabs service demo mode tests"""
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        """Get admin authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code == 200:
            return response.json().get("token")
        pytest.skip("Admin authentication failed")
    
    def test_voice_generation_endpoint(self, admin_token):
        """Test voice generation endpoint returns demo response without API key"""
        response = requests.post(
            f"{BASE_URL}/api/ai/generate",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "prompt": "Hello, this is a test of the voice generation system.",
                "content_type": "voice"
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        # Should return response (either success or demo mode)
        assert "content_type" in data
        assert data["content_type"] == "voice"
        
        # In demo mode, should indicate mocked
        if data.get("mocked"):
            print(f"✓ ElevenLabs in demo mode: {data.get('message', 'API key required')}")
        else:
            print(f"✓ ElevenLabs active: audio generated")


class TestFalAIDemoMode:
    """Fal.ai service demo mode tests"""
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        """Get admin authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code == 200:
            return response.json().get("token")
        pytest.skip("Admin authentication failed")
    
    def test_image_generation_endpoint(self, admin_token):
        """Test image generation endpoint works (fal.ai or fallback)"""
        response = requests.post(
            f"{BASE_URL}/api/ai/generate",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "prompt": "A beautiful sunset over mountains",
                "content_type": "image"
            },
            timeout=60  # Image generation can take time
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "content_type" in data
        assert data["content_type"] == "image"
        
        # Should have provider info
        if "provider" in data:
            print(f"✓ Image generation via: {data['provider']}")
        else:
            print(f"✓ Image generation working")


class TestExistingFeaturesNoRegression:
    """Regression tests for existing v4.2 features"""
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        """Get admin authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code == 200:
            return response.json().get("token")
        pytest.skip("Admin authentication failed")
    
    def test_products_endpoint(self):
        """Test products endpoint still works"""
        response = requests.get(f"{BASE_URL}/api/products")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Products endpoint: {len(data)} products")
    
    def test_posts_endpoint(self):
        """Test posts endpoint still works"""
        response = requests.get(f"{BASE_URL}/api/posts")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Posts endpoint: {len(data)} posts")
    
    def test_agents_endpoint(self):
        """Test agents endpoint returns 11 agents"""
        response = requests.get(f"{BASE_URL}/api/agents")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 11, f"Expected 11 agents, got {len(data)}"
        
        # Verify agent types
        agent_types = [a.get("agent_type") or a.get("type") for a in data]
        assert "base" in agent_types
        assert "manus" in agent_types
        assert "autonomous" in agent_types
        
        print(f"✓ Agents endpoint: {len(data)} agents")
    
    def test_stats_endpoint(self):
        """Test stats endpoint returns correct agent count"""
        response = requests.get(f"{BASE_URL}/api/stats")
        assert response.status_code == 200
        data = response.json()
        
        assert "ai_agents_active" in data
        assert data["ai_agents_active"] == 11
        
        print(f"✓ Stats endpoint: {data['ai_agents_active']} AI agents active")
    
    def test_admin_dashboard(self, admin_token):
        """Test admin dashboard endpoint"""
        response = requests.get(
            f"{BASE_URL}/api/admin/dashboard",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "stats" in data
        assert "recent_users" in data
        
        print(f"✓ Admin dashboard working")
    
    def test_cicd_status(self, admin_token):
        """Test CI/CD status endpoint"""
        response = requests.get(
            f"{BASE_URL}/api/cicd/status",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "repository" in data or "code_quality" in data
        
        print(f"✓ CI/CD status endpoint working")


class TestSoftrIntegration:
    """Softr database integration tests"""
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        """Get admin authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code == 200:
            return response.json().get("token")
        pytest.skip("Admin authentication failed")
    
    def test_softr_in_integration_status(self, admin_token):
        """Test Softr is present in integration status"""
        response = requests.get(
            f"{BASE_URL}/api/integrations/status",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "softr" in data["integrations"]
        softr = data["integrations"]["softr"]
        
        assert softr["name"] == "Softr Database"
        # Softr should work in scraping mode without API key
        assert softr["status"] in ["scraping_mode", "api_mode"]
        
        print(f"✓ Softr integration: status={softr['status']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
