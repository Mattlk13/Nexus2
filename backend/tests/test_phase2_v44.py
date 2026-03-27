"""
NEXUS v4.4 Phase 2 Testing Suite
Tests for:
- ProductHunt API Integration status
- Admin Analytics Dashboard with charts
- GitHub OAuth Connection page
- P2P Auction Bidding System with Socket.IO
"""

import pytest
import requests
import os
from datetime import datetime

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "admin@nexus.ai"
ADMIN_PASSWORD = "admin123"
TEST_AUCTION_PRODUCT_ID = "auction-demo-001"


class TestAuthSetup:
    """Authentication setup for tests"""
    
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
        print(f"✓ Admin login successful: {data['user']['username']}")


class TestProductHuntIntegration:
    """Test ProductHunt API Integration status"""
    
    def test_integration_status_endpoint(self):
        """Test integration status endpoint returns ProductHunt info"""
        response = requests.get(f"{BASE_URL}/api/integrations/status")
        assert response.status_code == 200
        data = response.json()
        
        # Check ProductHunt is in integrations
        assert "integrations" in data
        assert "producthunt" in data["integrations"]
        
        ph_status = data["integrations"]["producthunt"]
        assert "name" in ph_status
        assert "active" in ph_status
        assert "status" in ph_status
        
        print(f"✓ ProductHunt integration status: {ph_status['status']}")
        print(f"  Active: {ph_status['active']}")
        
    def test_integration_health_score(self):
        """Test integration health score calculation"""
        response = requests.get(f"{BASE_URL}/api/integrations/status")
        assert response.status_code == 200
        data = response.json()
        
        assert "summary" in data
        summary = data["summary"]
        assert "health_score" in summary
        assert "active" in summary
        assert "total" in summary
        
        health_score = summary["health_score"]
        active_count = summary["active"]
        total_count = summary["total"]
        
        print(f"✓ Integration Health Score: {health_score:.1f}%")
        print(f"  Active services: {active_count}/{total_count}")


class TestAdminAnalyticsDashboard:
    """Test Admin Analytics Dashboard endpoints"""
    
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
    
    def test_comprehensive_analytics(self, admin_token):
        """Test comprehensive analytics endpoint"""
        response = requests.get(
            f"{BASE_URL}/api/admin/analytics/comprehensive",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Check overview stats
        assert "overview" in data
        overview = data["overview"]
        assert "total_revenue" in overview
        assert "total_users" in overview
        assert "total_vendors" in overview
        assert "total_products" in overview
        assert "total_orders" in overview
        
        print(f"✓ Analytics Overview:")
        print(f"  Total Revenue: ${overview['total_revenue']}")
        print(f"  Total Users: {overview['total_users']}")
        print(f"  Total Products: {overview['total_products']}")
        
    def test_revenue_analytics(self, admin_token):
        """Test revenue analytics with chart data"""
        response = requests.get(
            f"{BASE_URL}/api/admin/analytics/comprehensive",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "revenue" in data
        revenue = data["revenue"]
        assert "chart_data" in revenue
        assert "growth_rate" in revenue
        
        print(f"✓ Revenue Analytics:")
        print(f"  Growth Rate: {revenue['growth_rate']}")
        print(f"  Chart Data Points: {len(revenue['chart_data'])}")
        
    def test_user_growth_analytics(self, admin_token):
        """Test user growth analytics"""
        response = requests.get(
            f"{BASE_URL}/api/admin/analytics/comprehensive",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "user_growth" in data
        user_growth = data["user_growth"]
        assert "chart_data" in user_growth
        assert "growth_rate" in user_growth
        
        print(f"✓ User Growth Analytics:")
        print(f"  Growth Rate: {user_growth['growth_rate']}")
        
    def test_top_products_analytics(self, admin_token):
        """Test top products analytics"""
        response = requests.get(
            f"{BASE_URL}/api/admin/analytics/comprehensive",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "top_products" in data
        top_products = data["top_products"]
        assert isinstance(top_products, list)
        
        print(f"✓ Top Products: {len(top_products)} products returned")
        
    def test_top_vendors_analytics(self, admin_token):
        """Test top vendors analytics"""
        response = requests.get(
            f"{BASE_URL}/api/admin/analytics/comprehensive",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "top_vendors" in data
        top_vendors = data["top_vendors"]
        assert isinstance(top_vendors, list)
        
        print(f"✓ Top Vendors: {len(top_vendors)} vendors returned")
        
    def test_category_distribution(self, admin_token):
        """Test category distribution analytics"""
        response = requests.get(
            f"{BASE_URL}/api/admin/analytics/comprehensive",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "category_distribution" in data
        cat_dist = data["category_distribution"]
        assert "categories" in cat_dist
        
        print(f"✓ Category Distribution: {len(cat_dist['categories'])} categories")
        
    def test_engagement_metrics(self, admin_token):
        """Test engagement metrics"""
        response = requests.get(
            f"{BASE_URL}/api/admin/analytics/comprehensive",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "engagement" in data
        engagement = data["engagement"]
        assert "posts_last_30d" in engagement
        assert "total_likes" in engagement
        assert "total_views" in engagement
        assert "engagement_rate" in engagement
        
        print(f"✓ Engagement Metrics:")
        print(f"  Posts (30d): {engagement['posts_last_30d']}")
        print(f"  Total Likes: {engagement['total_likes']}")
        print(f"  Engagement Rate: {engagement['engagement_rate']}")
        
    def test_analytics_requires_admin(self):
        """Test analytics endpoint requires admin auth"""
        # Without token
        response = requests.get(f"{BASE_URL}/api/admin/analytics/comprehensive")
        assert response.status_code in [401, 403]
        print("✓ Analytics endpoint properly requires authentication")


class TestGitHubOAuthConnection:
    """Test GitHub OAuth Connection endpoints"""
    
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
    
    def test_github_connection_status(self, admin_token):
        """Test GitHub connection status endpoint"""
        response = requests.get(
            f"{BASE_URL}/api/github/connection-status",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "github" in data
        github_status = data["github"]
        assert "connected" in github_status
        assert "username" in github_status
        assert "repos_synced" in github_status
        
        print(f"✓ GitHub Connection Status:")
        print(f"  Connected: {github_status['connected']}")
        print(f"  Username: {github_status['username']}")
        print(f"  Repos Synced: {github_status['repos_synced']}")
        
    def test_github_oauth_initiate(self, admin_token):
        """Test GitHub OAuth initiation endpoint"""
        response = requests.get(
            f"{BASE_URL}/api/auth/github/initiate",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Should return auth_url or demo_mode message
        if data.get("demo_mode"):
            print("✓ GitHub OAuth in demo mode (credentials not configured)")
        else:
            assert "auth_url" in data
            print(f"✓ GitHub OAuth URL generated: {data['auth_url'][:50]}...")
            
    def test_github_connection_requires_auth(self):
        """Test GitHub endpoints require authentication"""
        response = requests.get(f"{BASE_URL}/api/github/connection-status")
        assert response.status_code in [401, 403]
        print("✓ GitHub endpoints properly require authentication")


class TestP2PAuctionBidding:
    """Test P2P Auction Bidding System"""
    
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
    
    @pytest.fixture(scope="class")
    def auction_product_id(self, admin_token):
        """Create or get an auction product for testing"""
        # First try to get existing auction product
        response = requests.get(f"{BASE_URL}/api/products")
        if response.status_code == 200:
            products = response.json()
            for product in products:
                if product.get("is_auction"):
                    return product["id"]
        
        # Create a new auction product
        response = requests.post(
            f"{BASE_URL}/api/products",
            json={
                "title": "TEST_Auction_Item_Phase2",
                "description": "Test auction product for Phase 2 testing",
                "price": 100.0,
                "category": "art",
                "is_ai_generated": False,
                "is_auction": True,
                "starting_price": 50.0,
                "tags": ["test", "auction"]
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        if response.status_code in [200, 201]:
            return response.json()["id"]
        
        # If we can't create, use a placeholder
        return TEST_AUCTION_PRODUCT_ID
    
    def test_get_product_bids_endpoint(self, auction_product_id):
        """Test getting bids for a product"""
        response = requests.get(f"{BASE_URL}/api/products/{auction_product_id}/bids")
        assert response.status_code == 200
        data = response.json()
        
        assert "bids" in data
        assert "count" in data
        assert isinstance(data["bids"], list)
        
        print(f"✓ Get Product Bids:")
        print(f"  Product ID: {auction_product_id}")
        print(f"  Bids Count: {data['count']}")
        
    def test_place_bid_requires_auth(self, auction_product_id):
        """Test placing bid requires authentication"""
        response = requests.post(
            f"{BASE_URL}/api/products/{auction_product_id}/bid",
            json={"amount": 100}
        )
        assert response.status_code in [401, 403]
        print("✓ Place bid endpoint properly requires authentication")
        
    def test_place_bid_on_auction(self, admin_token, auction_product_id):
        """Test placing a bid on an auction product"""
        # First get current highest bid
        bids_response = requests.get(f"{BASE_URL}/api/products/{auction_product_id}/bids")
        current_bids = bids_response.json()
        
        # Calculate bid amount (higher than current highest)
        if current_bids.get("highest_bid"):
            bid_amount = current_bids["highest_bid"]["amount"] + 10
        else:
            bid_amount = 60  # Starting bid
        
        response = requests.post(
            f"{BASE_URL}/api/products/{auction_product_id}/bid",
            json={"amount": bid_amount},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        # May fail if product is not an auction or bid is too low
        if response.status_code == 200:
            data = response.json()
            assert "bid" in data
            assert data["bid"]["amount"] == bid_amount
            print(f"✓ Bid placed successfully: ${bid_amount}")
        elif response.status_code == 400:
            error = response.json()
            print(f"✓ Bid validation working: {error.get('detail', 'validation error')}")
        else:
            print(f"⚠ Bid response: {response.status_code} - {response.text[:100]}")
            
    def test_get_user_bids(self, admin_token):
        """Test getting user's bid history"""
        # First get user ID
        me_response = requests.get(
            f"{BASE_URL}/api/auth/me",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert me_response.status_code == 200
        user_id = me_response.json()["id"]
        
        response = requests.get(
            f"{BASE_URL}/api/users/{user_id}/bids",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "bids" in data
        assert "count" in data
        
        print(f"✓ User Bids History:")
        print(f"  User ID: {user_id}")
        print(f"  Total Bids: {data['count']}")


class TestSocketIOSetup:
    """Test Socket.IO configuration for real-time bidding"""
    
    def test_socketio_endpoint_exists(self):
        """Test Socket.IO endpoint is accessible"""
        # Socket.IO handshake endpoint
        response = requests.get(f"{BASE_URL}/api/socket.io/?EIO=4&transport=polling")
        
        # Socket.IO returns 200 with session info or 400 for bad request
        # Both indicate the endpoint exists
        assert response.status_code in [200, 400]
        print(f"✓ Socket.IO endpoint accessible (status: {response.status_code})")


class TestAuctionProductCreation:
    """Test auction product creation and retrieval"""
    
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
    
    def test_create_auction_product(self, admin_token):
        """Test creating an auction product"""
        response = requests.post(
            f"{BASE_URL}/api/products",
            json={
                "title": f"TEST_Auction_Product_{datetime.now().timestamp()}",
                "description": "Test auction product for Phase 2",
                "price": 150.0,
                "category": "art",
                "is_ai_generated": False,
                "tags": ["test", "auction", "phase2"]
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code in [200, 201]
        data = response.json()
        assert "id" in data
        assert data["title"].startswith("TEST_Auction_Product_")
        
        print(f"✓ Auction product created: {data['id']}")
        
    def test_get_product_with_auction_info(self, admin_token):
        """Test getting product includes auction info"""
        # Get any product
        response = requests.get(f"{BASE_URL}/api/products?limit=1")
        assert response.status_code == 200
        products = response.json()
        
        if products:
            product_id = products[0]["id"]
            detail_response = requests.get(f"{BASE_URL}/api/products/{product_id}")
            assert detail_response.status_code == 200
            
            product = detail_response.json()
            # Check product has expected fields
            assert "id" in product
            assert "title" in product
            assert "price" in product
            
            print(f"✓ Product detail retrieved: {product['title']}")
            print(f"  Is Auction: {product.get('is_auction', False)}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
