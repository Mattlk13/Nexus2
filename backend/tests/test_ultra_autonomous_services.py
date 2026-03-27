"""
Test Suite for ULTRA Hybrid Services and Autonomous Integration Engine
Tests all new endpoints added in the latest implementation:
- Autonomous Integration Engine: /api/autonomous/*
- ULTRA Image Generator: /api/ultra/image/*
- ULTRA Voice Service: /api/ultra/voice/*
- ULTRA LLM Service: /api/ultra/llm/*
- ULTRA Video Conferencing: /api/ultra/video/*
- Combined ULTRA Status: /api/ultra/status
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "admin@nexus.ai"
ADMIN_PASSWORD = "admin123"


class TestAuthSetup:
    """Authentication setup for tests"""
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        """Get admin authentication token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        data = response.json()
        assert "token" in data, "No token in login response"
        return data["token"]
    
    @pytest.fixture(scope="class")
    def auth_headers(self, admin_token):
        """Get authorization headers"""
        return {"Authorization": f"Bearer {admin_token}"}


class TestAutonomousEngineStatus(TestAuthSetup):
    """Test Autonomous Integration Engine status endpoint"""
    
    def test_autonomous_status_requires_auth(self):
        """Test that autonomous status requires authentication"""
        response = requests.get(f"{BASE_URL}/api/autonomous/status")
        assert response.status_code == 401 or response.status_code == 403
        print("✓ Autonomous status requires authentication")
    
    def test_autonomous_status_with_auth(self, auth_headers):
        """Test autonomous engine status with admin auth"""
        response = requests.get(
            f"{BASE_URL}/api/autonomous/status",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Status failed: {response.text}"
        data = response.json()
        
        # Verify expected fields
        assert "integrations_count" in data, "Missing integrations_count"
        assert "queue_size" in data, "Missing queue_size"
        assert "auto_update_enabled" in data, "Missing auto_update_enabled"
        assert "discovery_sources" in data, "Missing discovery_sources"
        assert "description" in data, "Missing description"
        
        # Verify values
        assert data["integrations_count"] == 8, f"Expected 8 integrations, got {data['integrations_count']}"
        assert data["discovery_sources"] == 10, f"Expected 10 discovery sources, got {data['discovery_sources']}"
        
        print(f"✓ Autonomous Engine Status: {data['integrations_count']} integrations, {data['discovery_sources']} sources")


class TestAutonomousDiscovery(TestAuthSetup):
    """Test Autonomous Integration Engine discovery endpoint"""
    
    def test_discover_integrations(self, auth_headers):
        """Test discovering new integrations"""
        response = requests.post(
            f"{BASE_URL}/api/autonomous/discover",
            headers=auth_headers,
            json={"category": None, "limit": 10}
        )
        assert response.status_code == 200, f"Discovery failed: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "success" in data, "Missing success field"
        assert data["success"] == True, "Discovery not successful"
        assert "discovered_count" in data, "Missing discovered_count"
        assert "integrations" in data, "Missing integrations list"
        assert "sources" in data, "Missing sources list"
        
        # Verify sources include expected platforms
        expected_sources = ["GitHub", "PyPI"]
        for source in expected_sources:
            assert source in data["sources"], f"Missing source: {source}"
        
        print(f"✓ Discovery: Found {data['discovered_count']} integrations from {len(data['sources'])} sources")


class TestAutonomousQueue(TestAuthSetup):
    """Test Autonomous Integration Engine queue endpoint"""
    
    def test_get_integration_queue(self, auth_headers):
        """Test getting the integration queue"""
        response = requests.get(
            f"{BASE_URL}/api/autonomous/queue",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Queue fetch failed: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "queue" in data, "Missing queue field"
        assert "count" in data, "Missing count field"
        assert isinstance(data["queue"], list), "Queue should be a list"
        assert data["count"] == len(data["queue"]), "Count mismatch"
        
        print(f"✓ Integration Queue: {data['count']} items pending")


class TestAutonomousIntegrations(TestAuthSetup):
    """Test Autonomous Integration Engine integrations endpoint"""
    
    def test_get_current_integrations(self, auth_headers):
        """Test getting current NEXUS integrations"""
        response = requests.get(
            f"{BASE_URL}/api/autonomous/integrations",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Integrations fetch failed: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "integrations" in data, "Missing integrations field"
        assert "count" in data, "Missing count field"
        
        # Verify expected integrations exist
        integrations = data["integrations"]
        expected_integrations = ["hypermessenger", "omnipay", "cloudstack", "crewai"]
        for integration in expected_integrations:
            assert integration in integrations, f"Missing integration: {integration}"
        
        print(f"✓ Current Integrations: {data['count']} active")


class TestUltraImageStatus(TestAuthSetup):
    """Test ULTRA Image Generator status endpoint"""
    
    def test_image_status_requires_auth(self):
        """Test that image status requires authentication"""
        response = requests.get(f"{BASE_URL}/api/ultra/image/status")
        assert response.status_code == 401 or response.status_code == 403
        print("✓ ULTRA Image status requires authentication")
    
    def test_image_status_with_auth(self, auth_headers):
        """Test ULTRA image generator status with auth"""
        response = requests.get(
            f"{BASE_URL}/api/ultra/image/status",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Image status failed: {response.text}"
        data = response.json()
        
        # Verify expected fields
        assert "available_backends" in data, "Missing available_backends"
        assert "backend_count" in data, "Missing backend_count"
        assert "models" in data, "Missing models"
        assert "recommendation" in data, "Missing recommendation"
        
        # Verify models include expected ones
        expected_models = ["sd_xl", "flux_dev", "sd_15"]
        for model in expected_models:
            assert model in data["models"], f"Missing model: {model}"
        
        print(f"✓ ULTRA Image Status: {data['backend_count']} backends, {len(data['models'])} models")


class TestUltraVoiceStatus(TestAuthSetup):
    """Test ULTRA Voice Service status endpoint"""
    
    def test_voice_status_requires_auth(self):
        """Test that voice status requires authentication"""
        response = requests.get(f"{BASE_URL}/api/ultra/voice/status")
        assert response.status_code == 401 or response.status_code == 403
        print("✓ ULTRA Voice status requires authentication")
    
    def test_voice_status_with_auth(self, auth_headers):
        """Test ULTRA voice service status with auth"""
        response = requests.get(
            f"{BASE_URL}/api/ultra/voice/status",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Voice status failed: {response.text}"
        data = response.json()
        
        # Verify expected fields
        assert "available_backends" in data, "Missing available_backends"
        assert "backend_count" in data, "Missing backend_count"
        assert "voices" in data, "Missing voices"
        assert "features" in data, "Missing features"
        assert "recommendation" in data, "Missing recommendation"
        
        # Verify features structure
        features = data["features"]
        assert "voice_cloning" in features, "Missing voice_cloning feature"
        assert "multilingual" in features, "Missing multilingual feature"
        
        print(f"✓ ULTRA Voice Status: {data['backend_count']} backends, {len(data['voices'])} voices")


class TestUltraLLMStatus(TestAuthSetup):
    """Test ULTRA LLM Service status endpoint"""
    
    def test_llm_status_requires_auth(self):
        """Test that LLM status requires authentication"""
        response = requests.get(f"{BASE_URL}/api/ultra/llm/status")
        assert response.status_code == 401 or response.status_code == 403
        print("✓ ULTRA LLM status requires authentication")
    
    def test_llm_status_with_auth(self, auth_headers):
        """Test ULTRA LLM service status with auth"""
        response = requests.get(
            f"{BASE_URL}/api/ultra/llm/status",
            headers=auth_headers
        )
        assert response.status_code == 200, f"LLM status failed: {response.text}"
        data = response.json()
        
        # Verify expected fields
        assert "available_backends" in data, "Missing available_backends"
        assert "backend_count" in data, "Missing backend_count"
        assert "models" in data, "Missing models"
        assert "features" in data, "Missing features"
        assert "recommendation" in data, "Missing recommendation"
        
        # Verify features structure
        features = data["features"]
        assert "local_inference" in features, "Missing local_inference feature"
        assert "cloud_fallback" in features, "Missing cloud_fallback feature"
        
        # Verify models include expected ones
        expected_models = ["llama-3.1-70b", "gpt-4o", "claude-sonnet-4"]
        for model in expected_models:
            assert model in data["models"], f"Missing model: {model}"
        
        print(f"✓ ULTRA LLM Status: {data['backend_count']} backends, {len(data['models'])} models")


class TestUltraVideoStatus(TestAuthSetup):
    """Test ULTRA Video Conferencing status endpoint"""
    
    def test_video_status_requires_auth(self):
        """Test that video status requires authentication"""
        response = requests.get(f"{BASE_URL}/api/ultra/video/status")
        assert response.status_code == 401 or response.status_code == 403
        print("✓ ULTRA Video status requires authentication")
    
    def test_video_status_with_auth(self, auth_headers):
        """Test ULTRA video conferencing status with auth"""
        response = requests.get(
            f"{BASE_URL}/api/ultra/video/status",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Video status failed: {response.text}"
        data = response.json()
        
        # Verify expected fields
        assert "available_backends" in data, "Missing available_backends"
        assert "backend_count" in data, "Missing backend_count"
        assert "active_rooms" in data, "Missing active_rooms"
        assert "features" in data, "Missing features"
        assert "recommendation" in data, "Missing recommendation"
        
        # Verify features structure
        features = data["features"]
        assert "sfu_scalability" in features, "Missing sfu_scalability feature"
        assert "self_hosted" in features, "Missing self_hosted feature"
        assert "p2p_fallback" in features, "Missing p2p_fallback feature"
        
        # P2P WebRTC should always be available
        assert "webrtc_p2p" in data["available_backends"], "P2P WebRTC should always be available"
        
        print(f"✓ ULTRA Video Status: {data['backend_count']} backends, {data['active_rooms']} active rooms")


class TestUltraCombinedStatus(TestAuthSetup):
    """Test combined ULTRA services status endpoint"""
    
    def test_combined_status_requires_auth(self):
        """Test that combined status requires authentication"""
        response = requests.get(f"{BASE_URL}/api/ultra/status")
        assert response.status_code == 401 or response.status_code == 403
        print("✓ ULTRA combined status requires authentication")
    
    def test_combined_status_with_auth(self, auth_headers):
        """Test combined ULTRA services status with auth"""
        response = requests.get(
            f"{BASE_URL}/api/ultra/status",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Combined status failed: {response.text}"
        data = response.json()
        
        # Verify all services are present
        assert "image_video_generator" in data, "Missing image_video_generator"
        assert "voice_service" in data, "Missing voice_service"
        assert "llm_service" in data, "Missing llm_service"
        assert "video_conferencing" in data, "Missing video_conferencing"
        assert "total_services" in data, "Missing total_services"
        assert "philosophy" in data, "Missing philosophy"
        
        # Verify total services count
        assert data["total_services"] == 4, f"Expected 4 services, got {data['total_services']}"
        
        # Verify each service has expected structure
        for service_name in ["image_video_generator", "voice_service", "llm_service"]:
            service = data[service_name]
            assert "available_backends" in service, f"{service_name} missing available_backends"
            assert "backend_count" in service, f"{service_name} missing backend_count"
        
        # Video conferencing may have error or backend_count
        video_conf = data["video_conferencing"]
        video_backends = video_conf.get("backend_count", 0)
        
        print(f"✓ ULTRA Combined Status: {data['total_services']} services active")
        print(f"  - Image/Video: {data['image_video_generator']['backend_count']} backends")
        print(f"  - Voice: {data['voice_service']['backend_count']} backends")
        print(f"  - LLM: {data['llm_service']['backend_count']} backends")
        print(f"  - Video Conf: {video_backends} backends")


class TestUltraVideoRooms(TestAuthSetup):
    """Test ULTRA Video Conferencing room operations"""
    
    def test_get_active_rooms(self, auth_headers):
        """Test getting active video rooms"""
        response = requests.get(
            f"{BASE_URL}/api/ultra/video/rooms",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Get rooms failed: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "rooms" in data, "Missing rooms field"
        assert "count" in data, "Missing count field"
        assert isinstance(data["rooms"], list), "Rooms should be a list"
        
        print(f"✓ Active Video Rooms: {data['count']} rooms")
    
    def test_create_video_room(self, auth_headers):
        """Test creating a video conference room"""
        room_name = f"test_room_{int(time.time())}"
        response = requests.post(
            f"{BASE_URL}/api/ultra/video/create-room",
            headers=auth_headers,
            json={
                "room_name": room_name,
                "max_participants": 5,
                "enable_recording": False
            }
        )
        assert response.status_code == 200, f"Create room failed: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "success" in data, "Missing success field"
        assert data["success"] == True, "Room creation not successful"
        assert "room_name" in data, "Missing room_name"
        assert "backend" in data, "Missing backend"
        
        # Backend should be one of the available options (jitsi for medium rooms, webrtc_p2p for small)
        valid_backends = ["webrtc_p2p", "jitsi", "livekit"]
        assert data["backend"] in valid_backends, f"Unexpected backend: {data['backend']}"
        
        print(f"✓ Created Video Room: {room_name} using {data['backend']}")
        
        # Clean up - leave the room
        leave_response = requests.delete(
            f"{BASE_URL}/api/ultra/video/leave-room/{room_name}",
            headers=auth_headers
        )
        assert leave_response.status_code == 200, f"Leave room failed: {leave_response.text}"
        print(f"✓ Left Video Room: {room_name}")


class TestBackendHealth:
    """Test that backend is healthy and all routers are loaded"""
    
    def test_health_endpoint(self):
        """Test health endpoint"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200, f"Health check failed: {response.text}"
        print("✓ Backend health check passed")
    
    def test_stats_endpoint(self):
        """Test stats endpoint (public)"""
        response = requests.get(f"{BASE_URL}/api/stats")
        assert response.status_code == 200, f"Stats failed: {response.text}"
        data = response.json()
        # Check for actual field names in stats
        assert "products_listed" in data or "total_products" in data, "Missing products count in stats"
        products = data.get("products_listed", data.get("total_products", 0))
        print(f"✓ Stats endpoint working: {products} products")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
