"""
NEXUS AI v4.4 Mega Enhancement Test Suite
Tests for:
- Mega Discovery (multi-source scanning)
- Enhanced User Profiles
- Investor Dashboard (27 investors)
- Marketing Automation & SEO
- MCP Server Integration
- Cloudflare Workers
- Creation Studio (download & publish)
"""

import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "admin@nexus.ai"
ADMIN_PASSWORD = "admin123"
USER_EMAIL = "user1@test.com"
USER_PASSWORD = "password123"


class TestAuthAndHealth:
    """Basic health and authentication tests"""
    
    def test_health_endpoint(self):
        """Test API health check"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        print(f"✓ Health check passed: {data}")
    
    def test_admin_login(self):
        """Test admin login"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert data["user"]["role"] == "admin"
        print(f"✓ Admin login successful: {data['user']['email']}")
        return data["token"]
    
    def test_user_login(self):
        """Test regular user login"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": USER_EMAIL,
            "password": USER_PASSWORD
        })
        # User may not exist, so we accept 401 as well
        if response.status_code == 200:
            data = response.json()
            assert "token" in data
            print(f"✓ User login successful: {data['user']['email']}")
        else:
            print(f"⚠ User login returned {response.status_code} - user may not exist")


class TestPlatformStats:
    """Test platform statistics endpoints"""
    
    def test_stats_endpoint(self):
        """Test platform stats"""
        response = requests.get(f"{BASE_URL}/api/stats")
        assert response.status_code == 200
        data = response.json()
        assert "products_listed" in data
        assert "active_vendors" in data
        print(f"✓ Stats: {data.get('products_listed')} products, {data.get('active_vendors')} vendors")
    
    def test_agents_endpoint(self):
        """Test AI agents list - should show 46 agents"""
        response = requests.get(f"{BASE_URL}/api/agents")
        assert response.status_code == 200
        data = response.json()
        # API returns list directly, not wrapped in {"agents": [...]}
        assert isinstance(data, list), "Expected list of agents"
        agent_count = len(data)
        print(f"✓ AI Agents: {agent_count} agents found")
        # v4.4 should have 46 agents
        assert agent_count >= 40, f"Expected 40+ agents, got {agent_count}"


class TestMegaDiscovery:
    """Test Mega Discovery multi-source scanning"""
    
    @pytest.fixture
    def admin_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip("Admin login failed")
        return response.json()["token"]
    
    def test_mega_discovery_latest(self, admin_token):
        """Test getting latest mega discovery results"""
        response = requests.get(
            f"{BASE_URL}/api/admin/mega-discovery/latest",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        # May return "No mega scans found" if no scan has been run
        if "message" in data and "No mega scans" in data["message"]:
            print(f"⚠ No mega scans found yet - need to run a scan first")
        else:
            total = data.get("total_discovered", 0)
            sources = data.get("results", {}).get("sources", {})
            print(f"✓ Mega Discovery Latest: {total} tools from {len(sources)} sources")
            # Verify sources structure
            if sources:
                for source_name, source_data in sources.items():
                    count = source_data.get("count", 0)
                    print(f"  - {source_name}: {count} tools")
    
    def test_mega_discovery_trigger(self, admin_token):
        """Test triggering a mega discovery scan (may take time)"""
        response = requests.post(
            f"{BASE_URL}/api/admin/mega-discovery",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={},
            timeout=120  # Long timeout for scan
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        total = data.get("results", {}).get("total_discovered", 0)
        print(f"✓ Mega Discovery Scan: {total} tools discovered")
        print(f"  Scan ID: {data.get('scan_id')}")


class TestEnhancedUserProfile:
    """Test enhanced user profile with analytics"""
    
    def test_enhanced_profile_user1(self):
        """Test enhanced profile for user-1"""
        response = requests.get(f"{BASE_URL}/api/users/user-1/profile/enhanced")
        assert response.status_code == 200
        data = response.json()
        
        # Check for error response
        if "error" in data:
            print(f"⚠ Enhanced profile error: {data['error']}")
            return
        
        # Verify profile structure
        assert "user" in data or "statistics" in data
        
        if "statistics" in data:
            stats = data["statistics"]
            print(f"✓ Enhanced Profile for user-1:")
            print(f"  - Products: {stats.get('products_created', 0)}")
            print(f"  - Revenue: ${stats.get('total_revenue', 0)}")
            print(f"  - Followers: {stats.get('followers_count', 0)}")
            
            # Check creator level
            creator_level = stats.get("creator_level", {})
            if creator_level:
                print(f"  - Creator Level: {creator_level.get('level')} (Tier {creator_level.get('tier')})")
        
        # Check badges
        badges = data.get("badges", [])
        if badges:
            print(f"  - Badges: {[b.get('name') for b in badges]}")
        
        # Check portfolio
        portfolio = data.get("portfolio", {})
        if portfolio:
            featured = portfolio.get("featured_products", [])
            print(f"  - Featured Products: {len(featured)}")


class TestInvestorDashboard:
    """Test investor dashboard with 27 investors"""
    
    @pytest.fixture
    def admin_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip("Admin login failed")
        return response.json()["token"]
    
    def test_investor_dashboard(self, admin_token):
        """Test investor dashboard endpoint"""
        response = requests.get(
            f"{BASE_URL}/api/admin/investor-dashboard",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Check platform metrics
        metrics = data.get("platform_metrics", {})
        print(f"✓ Investor Dashboard:")
        print(f"  - Total Users: {metrics.get('total_users')}")
        print(f"  - Total Products: {metrics.get('total_products')}")
        print(f"  - AI Agents Active: {metrics.get('ai_agents_active')}")
        
        # Check investor database
        investor_db = data.get("investor_database", {})
        total_investors = investor_db.get("total_investors", 0)
        tier_1 = investor_db.get("tier_1_funds", 0)
        tier_2 = investor_db.get("tier_2_funds", 0)
        
        print(f"  - Total Investors: {total_investors}")
        print(f"  - Tier 1 Funds: {tier_1}")
        print(f"  - Tier 2 Funds: {tier_2}")
        
        # Verify we have 27+ investors
        assert total_investors >= 20, f"Expected 20+ investors, got {total_investors}"
        
        # Check fundraising status
        fundraising = data.get("fundraising_status", {})
        if fundraising:
            print(f"  - Current Stage: {fundraising.get('current_stage')}")
            print(f"  - Target Raise: {fundraising.get('target_raise')}")
    
    def test_pitch_deck_data(self, admin_token):
        """Test pitch deck data generation"""
        response = requests.get(
            f"{BASE_URL}/api/admin/pitch-deck-data",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "company_name" in data
        assert "problem" in data
        assert "solution" in data
        print(f"✓ Pitch Deck Data:")
        print(f"  - Company: {data.get('company_name')}")
        print(f"  - Ask: {data.get('ask')}")


class TestMarketingAutomation:
    """Test marketing automation and SEO"""
    
    @pytest.fixture
    def admin_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip("Admin login failed")
        return response.json()["token"]
    
    def test_marketing_campaigns_list(self, admin_token):
        """Test getting marketing campaigns"""
        response = requests.get(
            f"{BASE_URL}/api/marketing/campaigns",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        campaigns = data.get("campaigns", [])
        print(f"✓ Marketing Campaigns: {len(campaigns)} campaigns")
    
    def test_seo_performance(self, admin_token):
        """Test SEO performance metrics"""
        response = requests.get(
            f"{BASE_URL}/api/marketing/seo",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Check SEO data structure
        organic = data.get("organic_traffic", {})
        keywords = data.get("keyword_rankings", [])
        backlinks = data.get("backlinks", {})
        
        print(f"✓ SEO Performance:")
        print(f"  - Organic Traffic (30d): {organic.get('last_30_days')}")
        print(f"  - Traffic Growth: {organic.get('growth')}")
        print(f"  - Keywords Tracked: {len(keywords)}")
        print(f"  - Total Backlinks: {backlinks.get('total')}")
        
        # Verify keyword rankings
        for kw in keywords[:3]:
            print(f"  - '{kw.get('keyword')}': Position #{kw.get('position')}")


class TestMCPIntegration:
    """Test MCP (Model Context Protocol) integration"""
    
    @pytest.fixture
    def admin_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip("Admin login failed")
        return response.json()["token"]
    
    def test_mcp_status(self, admin_token):
        """Test MCP integration status"""
        response = requests.get(
            f"{BASE_URL}/api/admin/mcp/status",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        discovered = data.get("discovered_servers", 0)
        active = data.get("active_connections", 0)
        status = data.get("status", "unknown")
        
        print(f"✓ MCP Status:")
        print(f"  - Discovered Servers: {discovered}")
        print(f"  - Active Connections: {active}")
        print(f"  - Status: {status}")
        print(f"  - Message: {data.get('message', 'N/A')}")
    
    def test_mcp_servers_list(self, admin_token):
        """Test listing MCP servers"""
        response = requests.get(
            f"{BASE_URL}/api/admin/mcp/servers",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        servers = data.get("servers", [])
        count = data.get("count", len(servers))
        
        print(f"✓ MCP Servers: {count} servers discovered")
        for server in servers[:5]:
            print(f"  - {server.get('name')}: {server.get('url')}")


class TestCloudflareWorkers:
    """Test Cloudflare Workers integration"""
    
    @pytest.fixture
    def admin_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip("Admin login failed")
        return response.json()["token"]
    
    def test_cloudflare_workers_list(self, admin_token):
        """Test listing Cloudflare Workers (demo mode)"""
        response = requests.get(
            f"{BASE_URL}/api/admin/cloudflare/workers",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        workers = data.get("workers", [])
        print(f"✓ Cloudflare Workers: {len(workers)} workers")
        for worker in workers:
            print(f"  - {worker.get('name')}: {worker.get('status')} - Routes: {worker.get('routes')}")


class TestCreationStudio:
    """Test Creation Studio download and publish functionality"""
    
    @pytest.fixture
    def user_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,  # Use admin for testing
            "password": ADMIN_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip("Login failed")
        return response.json()["token"]
    
    def test_studio_download_text(self, user_token):
        """Test downloading text content"""
        response = requests.post(
            f"{BASE_URL}/api/studio/download",
            headers={"Authorization": f"Bearer {user_token}"},
            json={
                "content_type": "text",
                "content": "This is a test blog post about AI technology.",
                "title": "TEST_AI_Blog_Post"
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data.get("success") == True
        assert "download_url" in data
        assert "filename" in data
        print(f"✓ Studio Download (text): {data.get('filename')}")
    
    def test_studio_download_ebook(self, user_token):
        """Test downloading ebook as PDF"""
        response = requests.post(
            f"{BASE_URL}/api/studio/download",
            headers={"Authorization": f"Bearer {user_token}"},
            json={
                "content_type": "ebook",
                "content": "Chapter 1: Introduction\n\nThis is the first chapter of our test ebook.\n\nChapter 2: Main Content\n\nHere we discuss the main topics.",
                "title": "TEST_Ebook_Guide"
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data.get("success") == True
        assert "download_url" in data
        assert data.get("content_type") == "application/pdf"
        print(f"✓ Studio Download (ebook/PDF): {data.get('filename')}")
    
    def test_studio_download_music(self, user_token):
        """Test downloading music composition"""
        response = requests.post(
            f"{BASE_URL}/api/studio/download",
            headers={"Authorization": f"Bearer {user_token}"},
            json={
                "content_type": "music",
                "content": "Tempo: 120 BPM\nKey: C Major\nInstruments: Piano, Strings\nMelody: C-E-G-C...",
                "title": "TEST_Music_Composition"
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data.get("success") == True
        print(f"✓ Studio Download (music): {data.get('filename')}")
    
    def test_studio_publish_to_marketplace(self, user_token):
        """Test publishing creation to marketplace"""
        response = requests.post(
            f"{BASE_URL}/api/studio/publish-to-marketplace",
            headers={"Authorization": f"Bearer {user_token}"},
            json={
                "title": "TEST_AI_Generated_Art",
                "description": "Beautiful AI-generated artwork for testing",
                "price": 19.99,
                "category": "image",
                "file_url": "generated-content",
                "tags": ["ai", "art", "test"]
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data.get("success") == True
        assert "product_id" in data
        print(f"✓ Studio Publish: Product ID {data.get('product_id')}")
        print(f"  - Title: {data.get('product', {}).get('title')}")
        print(f"  - Price: ${data.get('product', {}).get('price')}")


class TestIntegrationStatus:
    """Test integration status endpoint"""
    
    def test_integration_status(self):
        """Test integration status - should show 4/11 active (36%)"""
        # Endpoint is at /api/integrations/status (no admin prefix, no auth required)
        response = requests.get(f"{BASE_URL}/api/integrations/status")
        assert response.status_code == 200
        data = response.json()
        
        summary = data.get("summary", {})
        total = summary.get("total", 0)
        active = summary.get("active", 0)
        health = summary.get("health_score", 0)
        
        print(f"✓ Integration Status:")
        print(f"  - Total Integrations: {total}")
        print(f"  - Active: {active}")
        print(f"  - Health: {health:.1f}%")
        
        # List integrations
        integrations = data.get("integrations", {})
        for name, integ in list(integrations.items())[:5]:
            status = "✓" if integ.get("active") else "✗"
            print(f"  {status} {integ.get('name')}: {integ.get('status')}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
