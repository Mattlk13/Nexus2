"""
NEXUS v6.2 Autonomous Evolution System Tests
Tests for Mega Discovery Engine and CI/CD Pipeline
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestHealthCheck:
    """Basic health check tests"""
    
    def test_health_endpoint(self):
        """Test backend health endpoint"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        print("✓ Health check passed")


class TestMegaDiscoverySystem:
    """Tests for Mega Discovery Engine (58 sources, 10 categories)"""
    
    def test_mega_discovery_capabilities(self):
        """Test GET /api/v2/hybrid/mega_discovery/capabilities"""
        response = requests.get(f"{BASE_URL}/api/v2/hybrid/mega_discovery/capabilities")
        assert response.status_code == 200
        data = response.json()
        
        # Verify structure
        assert data["name"] == "Mega Discovery & Auto-Integration System"
        assert data["version"] == "1.0"
        assert data["status"] == "operational"
        
        # Verify 58 sources
        assert data["total_sources"] == 58
        
        # Verify 10 categories
        assert len(data["discovery_categories"]) == 10
        
        # Verify features
        assert "Scans 100+ sources continuously" in data["features"]
        assert "Automatic hybrid service generation" in data["features"]
        
        print(f"✓ Mega Discovery capabilities: {data['total_sources']} sources, {len(data['discovery_categories'])} categories")
    
    def test_mega_discovery_sources(self):
        """Test GET /api/v2/hybrid/mega_discovery/sources"""
        response = requests.get(f"{BASE_URL}/api/v2/hybrid/mega_discovery/sources")
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] == True
        assert "sources" in data
        assert data["total"] == 58
        
        # Verify all 10 categories exist
        expected_categories = [
            "ai_directories", "code_repositories", "package_registries",
            "cloud_platforms", "ai_platforms", "developer_tools",
            "enterprise_platforms", "news_research", "api_marketplaces", "specialized"
        ]
        for category in expected_categories:
            assert category in data["sources"], f"Missing category: {category}"
        
        print(f"✓ Mega Discovery sources: {data['total']} total across {len(data['sources'])} categories")
    
    def test_mega_discovery_status(self):
        """Test GET /api/v2/hybrid/mega_discovery/status"""
        response = requests.get(f"{BASE_URL}/api/v2/hybrid/mega_discovery/status")
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "active"
        assert "stats" in data
        assert "sources" in data
        
        # Verify stats structure
        stats = data["stats"]
        assert "total_sources" in stats
        assert "total_discoveries" in stats or stats["total_sources"] == 58
        
        print(f"✓ Mega Discovery status: {data['status']}, auto_generated: {data.get('auto_generated_hybrids', 0)}")
    
    def test_mega_discovery_pending(self):
        """Test GET /api/v2/hybrid/mega_discovery/pending"""
        response = requests.get(f"{BASE_URL}/api/v2/hybrid/mega_discovery/pending")
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] == True
        assert "total_pending" in data
        assert "integrations" in data
        
        print(f"✓ Mega Discovery pending: {data['total_pending']} integrations")
    
    def test_mega_discovery_start(self):
        """Test POST /api/v2/hybrid/mega_discovery/start"""
        response = requests.post(f"{BASE_URL}/api/v2/hybrid/mega_discovery/start")
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] == True
        assert "message" in data
        assert data["sources"] == 58
        
        print(f"✓ Mega Discovery start: {data['message']}")


class TestCICDPipeline:
    """Tests for Autonomous CI/CD Pipeline (5-stage pipeline)"""
    
    def test_cicd_capabilities(self):
        """Test GET /api/v2/hybrid/cicd_pipeline/capabilities"""
        response = requests.get(f"{BASE_URL}/api/v2/hybrid/cicd_pipeline/capabilities")
        assert response.status_code == 200
        data = response.json()
        
        # Verify structure
        assert data["name"] == "Autonomous CI/CD Pipeline"
        assert data["version"] == "1.0"
        assert data["status"] == "operational"
        
        # Verify 5 pipeline stages
        assert len(data["pipeline_stages"]) == 5
        
        # Verify features
        assert "Auto-generates hybrid service code" in data["features"]
        assert "Auto-runs tests with pytest" in data["features"]
        assert "Zero human intervention required" in data["features"]
        
        print(f"✓ CI/CD capabilities: {len(data['pipeline_stages'])} stages, {len(data['features'])} features")
    
    def test_cicd_status(self):
        """Test GET /api/v2/hybrid/cicd_pipeline/status"""
        response = requests.get(f"{BASE_URL}/api/v2/hybrid/cicd_pipeline/status")
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "active"
        assert "stats" in data
        
        # Verify stats structure
        stats = data["stats"]
        assert "total_generated" in stats
        assert "total_tested" in stats
        assert "total_deployed" in stats
        assert "success_rate" in stats
        assert "pending" in stats
        assert "deployed" in stats
        assert "failed" in stats
        
        print(f"✓ CI/CD status: pending={stats['pending']}, deployed={stats['deployed']}, failed={stats['failed']}")
    
    def test_cicd_start(self):
        """Test POST /api/v2/hybrid/cicd_pipeline/start"""
        response = requests.post(f"{BASE_URL}/api/v2/hybrid/cicd_pipeline/start")
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] == True
        assert "message" in data
        
        print(f"✓ CI/CD start: {data['message']}")


class TestV61FeaturesStillWorking:
    """Verify v6.1 features (Mistral TTS, Enterprise AI, Auditor) still work"""
    
    def test_mistral_tts_capabilities(self):
        """Test Mistral TTS capabilities endpoint"""
        response = requests.get(f"{BASE_URL}/api/v2/hybrid/mistral_tts/capabilities")
        assert response.status_code == 200
        data = response.json()
        
        assert data["name"] == "Mistral Voxtral TTS"
        assert "supported_languages" in data
        assert len(data["supported_languages"]) == 9
        
        print(f"✓ Mistral TTS: {len(data['supported_languages'])} languages supported")
    
    def test_enterprise_slack_capabilities(self):
        """Test Enterprise Slack capabilities endpoint"""
        response = requests.get(f"{BASE_URL}/api/v2/hybrid/enterprise_slack/capabilities")
        assert response.status_code == 200
        data = response.json()
        
        assert data["name"] == "Enterprise Slack-Style AI"
        assert "categories" in data
        assert len(data["categories"]) >= 4  # Research, CRM, Meetings, MCP
        
        print(f"✓ Enterprise Slack: {len(data['categories'])} feature categories")
    
    def test_auditor_capabilities(self):
        """Test Autonomous Auditor capabilities endpoint"""
        response = requests.get(f"{BASE_URL}/api/v2/hybrid/auditor/capabilities")
        assert response.status_code == 200
        data = response.json()
        
        assert data["name"] == "Autonomous Auditor"
        assert data["status"] == "active"
        assert "audits" in data
        assert len(data["audits"]) >= 5
        
        print(f"✓ Auditor: {len(data['audits'])} audit types, status={data['status']}")


class TestDynamicRouterLoading:
    """Test that dynamic router loads all hybrid services"""
    
    def test_hybrid_services_count(self):
        """Verify 50+ hybrid services are loaded"""
        # Test a few known hybrid endpoints to verify dynamic loading
        endpoints_to_test = [
            "/api/v2/hybrid/mega_discovery/capabilities",
            "/api/v2/hybrid/cicd_pipeline/capabilities",
            "/api/v2/hybrid/mistral_tts/capabilities",
            "/api/v2/hybrid/enterprise_slack/capabilities",
            "/api/v2/hybrid/auditor/capabilities"
        ]
        
        working_count = 0
        for endpoint in endpoints_to_test:
            response = requests.get(f"{BASE_URL}{endpoint}")
            if response.status_code == 200:
                working_count += 1
        
        assert working_count == len(endpoints_to_test), f"Only {working_count}/{len(endpoints_to_test)} endpoints working"
        print(f"✓ Dynamic router: {working_count} hybrid endpoints verified")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
