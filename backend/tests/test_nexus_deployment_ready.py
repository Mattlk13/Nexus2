"""
NEXUS AI Social Marketplace - Pre-Deployment Testing
Tests: Health, ADK Integration, Core APIs, Frontend Routes
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://model-exchange-2.preview.emergentagent.com')

class TestHealthEndpoints:
    """Health and status endpoint tests"""
    
    def test_health_endpoint(self):
        """Test /api/health returns healthy status"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        print(f"✓ Health endpoint working: {data}")
    
    def test_stats_endpoint(self):
        """Test /api/stats returns platform statistics"""
        response = requests.get(f"{BASE_URL}/api/stats")
        assert response.status_code == 200
        data = response.json()
        print(f"✓ Stats endpoint working: {data}")


class TestADKIntegration:
    """DigitalOcean ADK integration tests"""
    
    def test_adk_status_endpoint(self):
        """Test /api/adk/status returns ADK status"""
        response = requests.get(f"{BASE_URL}/api/adk/status")
        assert response.status_code == 200
        data = response.json()
        
        # Verify expected fields
        assert "adk_available" in data
        assert "workspace_root" in data
        assert "gradient_key_configured" in data
        assert "do_token_configured" in data
        assert "status" in data
        
        print(f"✓ ADK Status: {data}")
        
        # Note: ADK may not be installed in preview environment
        if not data["adk_available"]:
            print("  Note: ADK not installed (expected in preview environment)")
    
    def test_adk_agents_list(self):
        """Test /api/adk/agents returns agent list"""
        response = requests.get(f"{BASE_URL}/api/adk/agents")
        assert response.status_code == 200
        data = response.json()
        
        assert "agents" in data
        assert "count" in data
        assert isinstance(data["agents"], list)
        
        print(f"✓ ADK Agents list: {data['count']} agents")
    
    def test_adk_models_list(self):
        """Test /api/adk/models returns available models"""
        response = requests.get(f"{BASE_URL}/api/adk/models")
        assert response.status_code == 200
        data = response.json()
        
        assert "models" in data
        assert len(data["models"]) > 0
        
        # Verify model structure
        for model in data["models"]:
            assert "id" in model
            assert "name" in model
            assert "provider" in model
        
        print(f"✓ ADK Models available: {len(data['models'])} models")


class TestCoreAPIs:
    """Core marketplace API tests"""
    
    def test_products_endpoint(self):
        """Test /api/products returns product list"""
        response = requests.get(f"{BASE_URL}/api/products")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Products endpoint: {len(data)} products")
    
    def test_posts_endpoint(self):
        """Test /api/posts returns social posts"""
        response = requests.get(f"{BASE_URL}/api/posts")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Posts endpoint: {len(data)} posts")
    
    def test_trending_endpoint(self):
        """Test /api/trending returns trending items"""
        response = requests.get(f"{BASE_URL}/api/trending")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Trending endpoint: {len(data)} items")
    
    def test_categories_endpoint(self):
        """Test /api/categories returns categories"""
        response = requests.get(f"{BASE_URL}/api/categories")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Categories endpoint: {len(data)} categories")
    
    def test_spotlight_endpoint(self):
        """Test /api/spotlight returns featured items"""
        response = requests.get(f"{BASE_URL}/api/spotlight")
        assert response.status_code == 200
        data = response.json()
        print(f"✓ Spotlight endpoint working")


class TestAuthEndpoints:
    """Authentication endpoint tests"""
    
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials returns 401"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "invalid@test.com",
            "password": "wrongpassword"
        })
        assert response.status_code == 401
        print("✓ Login rejects invalid credentials")
    
    def test_register_missing_fields(self):
        """Test register with missing fields returns 422"""
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": "test@test.com"
            # Missing password and username
        })
        assert response.status_code == 422
        print("✓ Register validates required fields")


class TestHybridServices:
    """Hybrid AI services tests"""
    
    def test_hybrid_ultimate_controller(self):
        """Test ultimate controller status"""
        response = requests.get(f"{BASE_URL}/api/v2/hybrid/ultimate-controller/status")
        assert response.status_code == 200
        data = response.json()
        
        assert "total_hybrids" in data
        assert "active_hybrids" in data
        assert "categories" in data
        
        print(f"✓ Ultimate Controller: {data['total_hybrids']} hybrids, {data['active_hybrids']} active")
    
    def test_hybrid_groq_capabilities(self):
        """Test Groq hybrid capabilities"""
        response = requests.get(f"{BASE_URL}/api/v2/hybrid/groq/capabilities")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        print(f"✓ Groq hybrid: {data.get('name', 'working')}")
    
    def test_hybrid_elevenlabs_capabilities(self):
        """Test ElevenLabs hybrid capabilities"""
        response = requests.get(f"{BASE_URL}/api/v2/hybrid/elevenlabs/capabilities")
        assert response.status_code == 200
        data = response.json()
        print(f"✓ ElevenLabs hybrid working")
    
    def test_hybrid_sora_video_capabilities(self):
        """Test Sora Video hybrid capabilities"""
        response = requests.get(f"{BASE_URL}/api/v2/hybrid/sora_video/capabilities")
        assert response.status_code == 200
        data = response.json()
        print(f"✓ Sora Video hybrid working")


class TestSocialRoutes:
    """Social network API tests"""
    
    def test_social_users_search(self):
        """Test social user search"""
        response = requests.get(f"{BASE_URL}/api/social/users/search/test")
        assert response.status_code == 200
        print("✓ Social user search working")


class TestWebSocketInfrastructure:
    """WebSocket infrastructure tests (basic connectivity)"""
    
    def test_socket_io_endpoint_exists(self):
        """Test Socket.IO endpoint is accessible"""
        # Socket.IO uses HTTP for initial handshake
        response = requests.get(f"{BASE_URL}/socket.io/?EIO=4&transport=polling")
        # Socket.IO returns 200 with session info or 400 for bad request
        assert response.status_code in [200, 400]
        print(f"✓ Socket.IO endpoint accessible (status: {response.status_code})")


class TestAgentEndpoints:
    """AI Agent system tests"""
    
    def test_agents_list(self):
        """Test agents list endpoint"""
        response = requests.get(f"{BASE_URL}/api/agents")
        assert response.status_code == 200
        data = response.json()
        print(f"✓ Agents endpoint working")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
