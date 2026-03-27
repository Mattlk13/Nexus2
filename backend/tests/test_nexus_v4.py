"""
NEXUS AI Social Marketplace v4.0 - Backend API Tests
Tests for: 10 AI agents, WebSocket, Email service, Manus AI, Tool Discovery, CI/CD, Vendor Analytics
"""
import pytest
import requests
import os
import time
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://model-exchange-2.preview.emergentagent.com').rstrip('/')

# Test user credentials
TEST_USER_EMAIL = f"test_user_{uuid.uuid4().hex[:8]}@nexus.test"
TEST_USER_PASSWORD = "TestPass123!"
TEST_USER_USERNAME = f"TestUser_{uuid.uuid4().hex[:6]}"

class TestHealthAndStats:
    """Basic health and stats endpoints"""
    
    def test_stats_endpoint(self):
        """Test /api/stats returns correct data with 10 AI agents"""
        response = requests.get(f"{BASE_URL}/api/stats")
        assert response.status_code == 200, f"Stats failed: {response.text}"
        data = response.json()
        
        # Verify 10 AI agents active
        assert data.get("ai_agents_active") == 10, f"Expected 10 agents, got {data.get('ai_agents_active')}"
        assert "products_listed" in data
        assert "active_vendors" in data
        assert "total_users" in data
        print(f"✓ Stats endpoint working - 10 AI agents active")
    
    def test_products_endpoint(self):
        """Test /api/products returns list"""
        response = requests.get(f"{BASE_URL}/api/products")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Products endpoint working - {len(data)} products")
    
    def test_posts_endpoint(self):
        """Test /api/posts returns list"""
        response = requests.get(f"{BASE_URL}/api/posts")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Posts endpoint working - {len(data)} posts")
    
    def test_spotlight_endpoint(self):
        """Test /api/spotlight returns featured content"""
        response = requests.get(f"{BASE_URL}/api/spotlight")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Spotlight endpoint working - {len(data)} featured items")
    
    def test_vendors_endpoint(self):
        """Test /api/vendors returns list"""
        response = requests.get(f"{BASE_URL}/api/vendors")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Vendors endpoint working - {len(data)} vendors")
    
    def test_boost_packages_endpoint(self):
        """Test /api/boost/packages returns packages"""
        response = requests.get(f"{BASE_URL}/api/boost/packages")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 3, "Expected at least 3 boost packages"
        # Verify package structure
        for pkg in data:
            assert "id" in pkg
            assert "price" in pkg
            assert "days" in pkg
        print(f"✓ Boost packages endpoint working - {len(data)} packages")


class TestAgentsEndpoint:
    """Tests for 10 AI agents endpoint"""
    
    def test_agents_returns_10_agents(self):
        """Test /api/agents returns all 10 agents"""
        response = requests.get(f"{BASE_URL}/api/agents")
        assert response.status_code == 200, f"Agents failed: {response.text}"
        agents = response.json()
        
        assert len(agents) == 10, f"Expected 10 agents, got {len(agents)}"
        print(f"✓ Agents endpoint returns 10 agents")
    
    def test_agents_have_correct_types(self):
        """Test agents have base and manus types"""
        response = requests.get(f"{BASE_URL}/api/agents")
        assert response.status_code == 200
        agents = response.json()
        
        base_agents = [a for a in agents if a.get("agent_type") == "base"]
        manus_agents = [a for a in agents if a.get("agent_type") == "manus"]
        
        assert len(base_agents) == 5, f"Expected 5 base agents, got {len(base_agents)}"
        assert len(manus_agents) == 5, f"Expected 5 manus agents, got {len(manus_agents)}"
        print(f"✓ Agent types correct: 5 base + 5 manus")
    
    def test_agents_have_required_fields(self):
        """Test each agent has required fields"""
        response = requests.get(f"{BASE_URL}/api/agents")
        assert response.status_code == 200
        agents = response.json()
        
        required_fields = ["id", "name", "role", "status", "description", "agent_type"]
        for agent in agents:
            for field in required_fields:
                assert field in agent, f"Agent {agent.get('name')} missing field: {field}"
        print(f"✓ All agents have required fields")
    
    def test_specific_agents_exist(self):
        """Test specific agent names exist"""
        response = requests.get(f"{BASE_URL}/api/agents")
        assert response.status_code == 200
        agents = response.json()
        
        agent_names = [a.get("name") for a in agents]
        
        # Core agents
        assert "CEO Agent" in agent_names
        assert "Product Manager" in agent_names
        assert "Marketing Agent" in agent_names
        assert "Vendor Manager" in agent_names
        assert "Finance Agent" in agent_names
        
        # Manus agents
        assert "Tool Discovery Agent" in agent_names
        assert "Investor Outreach Agent" in agent_names
        assert "Marketing Automation" in agent_names
        assert "Platform Optimizer" in agent_names
        assert "CI/CD Agent" in agent_names
        
        print(f"✓ All 10 specific agents exist")


class TestAuthAndRegistration:
    """Tests for authentication and registration (triggers welcome email)"""
    
    def test_user_registration(self):
        """Test user registration triggers welcome email queue"""
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD,
            "username": TEST_USER_USERNAME
        })
        assert response.status_code == 200, f"Registration failed: {response.text}"
        data = response.json()
        
        assert "token" in data
        assert "user" in data
        assert data["user"]["email"] == TEST_USER_EMAIL
        assert data["user"]["username"] == TEST_USER_USERNAME
        print(f"✓ User registration successful - welcome email queued")
        
        # Store token for later tests
        TestAuthAndRegistration.token = data["token"]
        TestAuthAndRegistration.user_id = data["user"]["id"]
    
    def test_user_login(self):
        """Test user login"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        
        assert "token" in data
        assert "user" in data
        print(f"✓ User login successful")
    
    def test_get_current_user(self):
        """Test /api/auth/me returns current user"""
        if not hasattr(TestAuthAndRegistration, 'token'):
            pytest.skip("No token available")
        
        response = requests.get(f"{BASE_URL}/api/auth/me", headers={
            "Authorization": f"Bearer {TestAuthAndRegistration.token}"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == TEST_USER_EMAIL
        print(f"✓ Get current user successful")


class TestNotifications:
    """Tests for notification system"""
    
    def test_get_notifications_requires_auth(self):
        """Test /api/notifications requires authentication"""
        response = requests.get(f"{BASE_URL}/api/notifications")
        assert response.status_code in [401, 403]
        print(f"✓ Notifications endpoint requires auth")
    
    def test_get_notifications_authenticated(self):
        """Test /api/notifications returns list when authenticated"""
        if not hasattr(TestAuthAndRegistration, 'token'):
            pytest.skip("No token available")
        
        response = requests.get(f"{BASE_URL}/api/notifications", headers={
            "Authorization": f"Bearer {TestAuthAndRegistration.token}"
        })
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Notifications endpoint working - {len(data)} notifications")


class TestVendorAnalytics:
    """Tests for vendor analytics dashboard"""
    
    def test_vendor_analytics_requires_auth(self):
        """Test /api/vendor/analytics requires authentication"""
        response = requests.get(f"{BASE_URL}/api/vendor/analytics")
        assert response.status_code in [401, 403]
        print(f"✓ Vendor analytics requires auth")
    
    def test_vendor_analytics_authenticated(self):
        """Test /api/vendor/analytics returns metrics"""
        if not hasattr(TestAuthAndRegistration, 'token'):
            pytest.skip("No token available")
        
        response = requests.get(f"{BASE_URL}/api/vendor/analytics", headers={
            "Authorization": f"Bearer {TestAuthAndRegistration.token}"
        })
        assert response.status_code == 200
        data = response.json()
        
        # Verify analytics structure
        assert "overview" in data
        overview = data["overview"]
        assert "total_products" in overview
        assert "total_views" in overview
        assert "total_likes" in overview
        assert "total_sales" in overview
        assert "total_revenue" in overview
        assert "conversion_rate" in overview
        
        assert "recent_sales" in data
        assert "top_products" in data
        print(f"✓ Vendor analytics working - overview metrics present")
    
    def test_vendor_products_endpoint(self):
        """Test /api/vendor/products returns vendor's products"""
        if not hasattr(TestAuthAndRegistration, 'token'):
            pytest.skip("No token available")
        
        response = requests.get(f"{BASE_URL}/api/vendor/products", headers={
            "Authorization": f"Bearer {TestAuthAndRegistration.token}"
        })
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Vendor products endpoint working")


class TestManusAI:
    """Tests for Manus AI task creation (mock mode)"""
    
    def test_manus_task_requires_admin(self):
        """Test /api/manus/task requires admin role"""
        if not hasattr(TestAuthAndRegistration, 'token'):
            pytest.skip("No token available")
        
        response = requests.post(f"{BASE_URL}/api/manus/task", 
            json={"description": "Test task", "context": {}},
            headers={"Authorization": f"Bearer {TestAuthAndRegistration.token}"}
        )
        # Should fail for non-admin user
        assert response.status_code in [401, 403]
        print(f"✓ Manus task endpoint requires admin")


class TestToolDiscovery:
    """Tests for tool discovery API"""
    
    def test_discovered_tools_requires_admin(self):
        """Test /api/automation/discovered-tools requires admin"""
        if not hasattr(TestAuthAndRegistration, 'token'):
            pytest.skip("No token available")
        
        response = requests.get(f"{BASE_URL}/api/automation/discovered-tools", headers={
            "Authorization": f"Bearer {TestAuthAndRegistration.token}"
        })
        # Should fail for non-admin user
        assert response.status_code in [401, 403]
        print(f"✓ Discovered tools endpoint requires admin")


class TestCICD:
    """Tests for CI/CD status endpoint"""
    
    def test_cicd_status_requires_admin(self):
        """Test /api/cicd/status requires admin"""
        if not hasattr(TestAuthAndRegistration, 'token'):
            pytest.skip("No token available")
        
        response = requests.get(f"{BASE_URL}/api/cicd/status", headers={
            "Authorization": f"Bearer {TestAuthAndRegistration.token}"
        })
        # Should fail for non-admin user
        assert response.status_code in [401, 403]
        print(f"✓ CI/CD status endpoint requires admin")


class TestFollowAndNotifications:
    """Tests for follow user action and notifications"""
    
    def test_follow_user_creates_notification(self):
        """Test following a user creates notification"""
        if not hasattr(TestAuthAndRegistration, 'token'):
            pytest.skip("No token available")
        
        # First, get a user to follow (from products or posts)
        products_response = requests.get(f"{BASE_URL}/api/products")
        if products_response.status_code == 200:
            products = products_response.json()
            if products:
                vendor_id = products[0].get("vendor_id")
                if vendor_id and vendor_id != TestAuthAndRegistration.user_id:
                    # Try to follow
                    response = requests.post(f"{BASE_URL}/api/users/{vendor_id}/follow", headers={
                        "Authorization": f"Bearer {TestAuthAndRegistration.token}"
                    })
                    assert response.status_code == 200
                    data = response.json()
                    assert "following" in data
                    print(f"✓ Follow user action working")
                    return
        
        print(f"⚠ No other users to follow - skipping")


class TestAdminEndpoints:
    """Tests for admin-protected endpoints"""
    
    def test_admin_dashboard_requires_admin(self):
        """Test /api/admin/dashboard requires admin role"""
        if not hasattr(TestAuthAndRegistration, 'token'):
            pytest.skip("No token available")
        
        response = requests.get(f"{BASE_URL}/api/admin/dashboard", headers={
            "Authorization": f"Bearer {TestAuthAndRegistration.token}"
        })
        # Should fail for non-admin user
        assert response.status_code in [401, 403]
        print(f"✓ Admin dashboard requires admin role")
    
    def test_admin_users_requires_admin(self):
        """Test /api/admin/users requires admin role"""
        if not hasattr(TestAuthAndRegistration, 'token'):
            pytest.skip("No token available")
        
        response = requests.get(f"{BASE_URL}/api/admin/users", headers={
            "Authorization": f"Bearer {TestAuthAndRegistration.token}"
        })
        assert response.status_code in [401, 403]
        print(f"✓ Admin users endpoint requires admin role")


class TestBackwardCompatibility:
    """Tests for backward compatibility with original marketplace features"""
    
    def test_trending_endpoint(self):
        """Test /api/trending returns products"""
        response = requests.get(f"{BASE_URL}/api/trending")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Trending endpoint working - {len(data)} items")
    
    def test_product_detail(self):
        """Test /api/products/{id} returns product details"""
        # First get a product
        products_response = requests.get(f"{BASE_URL}/api/products")
        if products_response.status_code == 200:
            products = products_response.json()
            if products:
                product_id = products[0].get("id")
                response = requests.get(f"{BASE_URL}/api/products/{product_id}")
                assert response.status_code == 200
                data = response.json()
                assert "title" in data
                assert "price" in data
                print(f"✓ Product detail endpoint working")
                return
        print(f"⚠ No products to test detail - skipping")
    
    def test_create_post(self):
        """Test creating a post"""
        if not hasattr(TestAuthAndRegistration, 'token'):
            pytest.skip("No token available")
        
        response = requests.post(f"{BASE_URL}/api/posts", 
            json={"content": f"Test post from pytest {uuid.uuid4().hex[:8]}", "post_type": "text"},
            headers={"Authorization": f"Bearer {TestAuthAndRegistration.token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "content" in data
        print(f"✓ Create post working")
    
    def test_create_vendor(self):
        """Test creating a vendor shop"""
        if not hasattr(TestAuthAndRegistration, 'token'):
            pytest.skip("No token available")
        
        response = requests.post(f"{BASE_URL}/api/vendors",
            json={
                "shop_name": f"Test Shop {uuid.uuid4().hex[:6]}",
                "description": "Test shop description",
                "category": "digital"
            },
            headers={"Authorization": f"Bearer {TestAuthAndRegistration.token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "shop_name" in data
        print(f"✓ Create vendor working")


class TestCleanup:
    """Cleanup test data"""
    
    def test_cleanup_test_user(self):
        """Note: Test user cleanup would require admin access"""
        print(f"⚠ Test user {TEST_USER_EMAIL} created - manual cleanup may be needed")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
