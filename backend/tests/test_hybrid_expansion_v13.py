"""
NEXUS Hybrid Services Test Suite - Iteration 13
Tests 13 NEW Hybrid Services (Platform expansion from 19 to 32 hybrids)

New Hybrids Tested:
1. Privacy Hybrid - Security & data protection tools
2. Social Impact Hybrid - Social good projects
3. Accessibility Hybrid - Web accessibility tools
4. DevTools Hybrid - Developer tools (Sentry, Jenkins, Gitpod)
5. Editors Hybrid - Text editors (VSCode, Vim, Neovim)
6. Pixel Art Hybrid - Pixel art creation tools
7. SDR Hybrid - Software Defined Radio tools
8. Web Games Hybrid - Browser-based games
9. Open Source Tools Hybrid - OSS management tools
10. AI Model Zoos Hybrid - Pre-trained model repositories
11. Probot Hybrid - GitHub automation apps
12. PHP Quality Hybrid - PHP code quality tools
13. JS State Hybrid - JavaScript state management libraries
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestUltimateControllerExpansion:
    """Tests for Ultimate Controller - now manages 32 hybrid systems"""
    
    def test_controller_status_shows_32_hybrids(self):
        """Verify Ultimate Controller shows 32 active hybrids (expanded from 19)"""
        response = requests.get(f"{BASE_URL}/api/hybrid/controller/status")
        assert response.status_code == 200
        data = response.json()
        
        assert data["total_hybrids"] == 32, f"Expected 32 hybrids, got {data['total_hybrids']}"
        assert data["active_hybrids"] == 32, f"Expected 32 active hybrids, got {data['active_hybrids']}"
        assert data["status"] == "operational"
        
        # Verify new categories are present
        categories = data["by_category"]
        assert "security" in categories, "Security category missing"
        assert "community" in categories, "Community category missing"
        assert "inclusive" in categories, "Inclusive category missing"
        assert "development" in categories, "Development category missing"
        assert "creative" in categories, "Creative category missing"
        assert "hardware" in categories, "Hardware category missing"
        assert "gaming" in categories, "Gaming category missing"
        assert "automation" in categories, "Automation category missing"
        assert "frontend" in categories, "Frontend category missing"
        
        # Verify new hybrids are registered
        security_hybrids = [h["id"] for h in categories.get("security", [])]
        assert "privacy" in security_hybrids, "Privacy hybrid missing from security"
        
        development_hybrids = [h["id"] for h in categories.get("development", [])]
        assert "devtools" in development_hybrids, "DevTools hybrid missing"
        assert "editors" in development_hybrids, "Editors hybrid missing"
        assert "php_quality" in development_hybrids, "PHP Quality hybrid missing"


class TestPrivacyHybrid:
    """Tests for Privacy & Data Protection Hybrid"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup authentication"""
        login_response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "admin@nexus.ai", "password": "admin123"}
        )
        if login_response.status_code == 200:
            self.token = login_response.json()["token"]
        else:
            pytest.skip("Could not authenticate")
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_privacy_capabilities(self):
        """Test Privacy capabilities endpoint"""
        response = requests.get(f"{BASE_URL}/api/hybrid/privacy/capabilities")
        assert response.status_code == 200
        data = response.json()
        
        assert data["name"] == "Privacy & Data Protection Hybrid"
        assert "tools" in data
        assert "git-secrets" in data["tools"]
        assert "SoftU2F" in data["tools"]
    
    def test_scan_secrets(self):
        """Test secret scanning endpoint"""
        response = requests.post(
            f"{BASE_URL}/api/hybrid/privacy/scan-secrets?repo_url=https://github.com/test/repo",
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] == True
        assert "secrets_found" in data
        assert "files_scanned" in data
    
    def test_u2f_setup(self):
        """Test U2F authentication setup"""
        response = requests.post(
            f"{BASE_URL}/api/hybrid/privacy/u2f-setup",
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] == True
        assert data["u2f_enabled"] == True


class TestSocialImpactHybrid:
    """Tests for Social Impact Hybrid"""
    
    def test_social_impact_capabilities(self):
        """Test Social Impact capabilities endpoint"""
        response = requests.get(f"{BASE_URL}/api/hybrid/social-impact/capabilities")
        assert response.status_code == 200
        data = response.json()
        
        assert data["name"] == "Social Impact Hybrid"
    
    def test_list_projects(self):
        """Test listing social impact projects"""
        response = requests.get(f"{BASE_URL}/api/hybrid/social-impact/projects")
        assert response.status_code == 200
        data = response.json()
        
        assert "projects" in data
        assert len(data["projects"]) > 0
    
    def test_analyze_project_impact(self):
        """Test project impact analysis"""
        response = requests.get(f"{BASE_URL}/api/hybrid/social-impact/analyze/project1")
        assert response.status_code == 200
        data = response.json()
        
        assert "impact_score" in data
        assert data["impact_score"] > 0


class TestAccessibilityHybrid:
    """Tests for Web Accessibility Hybrid"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup authentication"""
        login_response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "admin@nexus.ai", "password": "admin123"}
        )
        if login_response.status_code == 200:
            self.token = login_response.json()["token"]
        else:
            pytest.skip("Could not authenticate")
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_accessibility_capabilities(self):
        """Test Accessibility capabilities endpoint"""
        response = requests.get(f"{BASE_URL}/api/hybrid/accessibility/capabilities")
        assert response.status_code == 200
        data = response.json()
        
        assert data["name"] == "Web Accessibility Hybrid"
    
    def test_audit_page(self):
        """Test page accessibility audit"""
        response = requests.post(
            f"{BASE_URL}/api/hybrid/accessibility/audit?url=https://example.com",
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] == True
        assert "issues" in data
    
    def test_contrast_check(self):
        """Test color contrast checking"""
        response = requests.post(
            f"{BASE_URL}/api/hybrid/accessibility/contrast-check?foreground=%23000000&background=%23FFFFFF"
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "ratio" in data
        assert "7.5" in data["ratio"] or float(data["ratio"].replace(":1", "")) >= 7


class TestDevToolsHybrid:
    """Tests for Dev Tools Hybrid (Sentry, Jenkins, Gitpod)"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup authentication"""
        login_response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "admin@nexus.ai", "password": "admin123"}
        )
        if login_response.status_code == 200:
            self.token = login_response.json()["token"]
        else:
            pytest.skip("Could not authenticate")
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_devtools_capabilities(self):
        """Test DevTools capabilities endpoint"""
        response = requests.get(f"{BASE_URL}/api/hybrid/devtools/capabilities")
        assert response.status_code == 200
        data = response.json()
        
        assert data["name"] == "Dev Tools Hybrid"
    
    def test_setup_error_tracking(self):
        """Test Sentry error tracking setup"""
        response = requests.post(
            f"{BASE_URL}/api/hybrid/devtools/error-tracking?project=test-project",
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] == True
        assert data["sentry_enabled"] == True
        assert "dsn" in data
    
    def test_create_ci_pipeline(self):
        """Test CI pipeline creation"""
        response = requests.post(
            f"{BASE_URL}/api/hybrid/devtools/ci-pipeline",
            headers=self.headers,
            json={"name": "test-pipeline", "stages": ["build", "test"]}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] == True
        assert "stages" in data


class TestEditorsHybrid:
    """Tests for Text Editors Hybrid"""
    
    def test_editors_capabilities(self):
        """Test Editors capabilities endpoint"""
        response = requests.get(f"{BASE_URL}/api/hybrid/editors/capabilities")
        assert response.status_code == 200
        data = response.json()
        
        assert data["name"] == "Text Editors Hybrid"
    
    def test_list_editors(self):
        """Test listing text editors"""
        response = requests.get(f"{BASE_URL}/api/hybrid/editors/list")
        assert response.status_code == 200
        data = response.json()
        
        assert "editors" in data
        assert len(data["editors"]) >= 3
    
    def test_compare_editors(self):
        """Test editor comparison"""
        response = requests.post(
            f"{BASE_URL}/api/hybrid/editors/compare",
            json=["vscode", "vim"]
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "comparison" in data


class TestPixelArtHybrid:
    """Tests for Pixel Art Tools Hybrid"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup authentication"""
        login_response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "admin@nexus.ai", "password": "admin123"}
        )
        if login_response.status_code == 200:
            self.token = login_response.json()["token"]
        else:
            pytest.skip("Could not authenticate")
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_pixelart_capabilities(self):
        """Test Pixel Art capabilities endpoint"""
        response = requests.get(f"{BASE_URL}/api/hybrid/pixelart/capabilities")
        assert response.status_code == 200
        data = response.json()
        
        assert data["name"] == "Pixel Art Tools Hybrid"
    
    def test_create_canvas(self):
        """Test pixel art canvas creation"""
        response = requests.post(
            f"{BASE_URL}/api/hybrid/pixelart/canvas?width=32&height=32",
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] == True
        assert "canvas_id" in data
    
    def test_export_sprite(self):
        """Test sprite export"""
        response = requests.post(
            f"{BASE_URL}/api/hybrid/pixelart/export?canvas_id=test123&format=png",
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] == True


class TestSDRHybrid:
    """Tests for Software Defined Radio Hybrid"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup authentication"""
        login_response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "admin@nexus.ai", "password": "admin123"}
        )
        if login_response.status_code == 200:
            self.token = login_response.json()["token"]
        else:
            pytest.skip("Could not authenticate")
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_sdr_capabilities(self):
        """Test SDR capabilities endpoint"""
        response = requests.get(f"{BASE_URL}/api/hybrid/sdr/capabilities")
        assert response.status_code == 200
        data = response.json()
        
        assert data["name"] == "Software Defined Radio Hybrid"
    
    def test_start_receiver(self):
        """Test SDR receiver start"""
        response = requests.post(
            f"{BASE_URL}/api/hybrid/sdr/receiver/start",
            headers=self.headers,
            json={"frequency": 100.0, "sample_rate": 2400000}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] == True
        assert data["status"] == "receiving"
    
    def test_analyze_signal(self):
        """Test signal analysis"""
        response = requests.post(
            f"{BASE_URL}/api/hybrid/sdr/signal/analyze",
            headers=self.headers,
            json={"signal_type": "FM", "frequency": 100.0}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] == True
        assert "strength" in data


class TestWebGamesHybrid:
    """Tests for Web Games Hybrid"""
    
    def test_webgames_capabilities(self):
        """Test Web Games capabilities endpoint"""
        response = requests.get(f"{BASE_URL}/api/hybrid/webgames/capabilities")
        assert response.status_code == 200
        data = response.json()
        
        assert data["name"] == "Web Games Hybrid"
    
    def test_list_games(self):
        """Test listing web games"""
        response = requests.get(f"{BASE_URL}/api/hybrid/webgames/list")
        assert response.status_code == 200
        data = response.json()
        
        assert "games" in data
        assert len(data["games"]) >= 3
    
    def test_get_game_embed(self):
        """Test getting game embed code"""
        response = requests.get(f"{BASE_URL}/api/hybrid/webgames/2048/embed")
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] == True
        assert "iframe_code" in data or "embed_url" in data


class TestOpenSourceToolsHybrid:
    """Tests for Open Source Tools Hybrid"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup authentication"""
        login_response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "admin@nexus.ai", "password": "admin123"}
        )
        if login_response.status_code == 200:
            self.token = login_response.json()["token"]
        else:
            pytest.skip("Could not authenticate")
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_opensource_tools_capabilities(self):
        """Test Open Source Tools capabilities endpoint"""
        response = requests.get(f"{BASE_URL}/api/hybrid/opensource-tools/capabilities")
        assert response.status_code == 200
        data = response.json()
        
        assert data["name"] == "Open Source Tools Hybrid"
    
    def test_list_tools(self):
        """Test listing open source tools"""
        response = requests.get(f"{BASE_URL}/api/hybrid/opensource-tools/list")
        assert response.status_code == 200
        data = response.json()
        
        assert "tools" in data
        assert len(data["tools"]) >= 5
    
    def test_automate_release(self):
        """Test release automation"""
        response = requests.post(
            f"{BASE_URL}/api/hybrid/opensource-tools/automate-release?repo=test/repo",
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] == True
    
    def test_manage_notifications(self):
        """Test GitHub notifications management"""
        response = requests.get(
            f"{BASE_URL}/api/hybrid/opensource-tools/notifications/user1",
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] == True
        assert "unread_count" in data
        assert "tool" in data


class TestAIModelZoosHybrid:
    """Tests for AI Model Zoos Hybrid"""
    
    def test_ai_model_zoos_capabilities(self):
        """Test AI Model Zoos capabilities endpoint"""
        response = requests.get(f"{BASE_URL}/api/hybrid/ai-model-zoos/capabilities")
        assert response.status_code == 200
        data = response.json()
        
        assert data["name"] == "AI Model Zoos Hybrid"
    
    def test_list_frameworks(self):
        """Test listing ML frameworks"""
        response = requests.get(f"{BASE_URL}/api/hybrid/ai-model-zoos/frameworks")
        assert response.status_code == 200
        data = response.json()
        
        assert "frameworks" in data
        assert len(data["frameworks"]) >= 5
        
        # Verify major frameworks are present
        framework_names = [f["name"] if isinstance(f, dict) else f for f in data["frameworks"]]
        assert any("tensorflow" in str(f).lower() for f in framework_names)
    
    def test_search_models(self):
        """Test model search"""
        response = requests.get(f"{BASE_URL}/api/hybrid/ai-model-zoos/search?query=resnet")
        assert response.status_code == 200
        data = response.json()
        
        assert "results" in data
        assert len(data["results"]) > 0
    
    def test_get_model_details(self):
        """Test getting model details"""
        response = requests.get(f"{BASE_URL}/api/hybrid/ai-model-zoos/tensorflow/resnet50")
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] == True
        assert data["framework"] == "tensorflow"
        assert data["model"] == "resnet50"


class TestProbotHybrid:
    """Tests for Probot Apps Hybrid"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup authentication"""
        login_response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "admin@nexus.ai", "password": "admin123"}
        )
        if login_response.status_code == 200:
            self.token = login_response.json()["token"]
        else:
            pytest.skip("Could not authenticate")
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_probot_capabilities(self):
        """Test Probot capabilities endpoint"""
        response = requests.get(f"{BASE_URL}/api/hybrid/probot/capabilities")
        assert response.status_code == 200
        data = response.json()
        
        assert data["name"] == "Probot Apps Hybrid"
    
    def test_list_apps(self):
        """Test listing Probot apps"""
        response = requests.get(f"{BASE_URL}/api/hybrid/probot/apps")
        assert response.status_code == 200
        data = response.json()
        
        assert "apps" in data
        assert len(data["apps"]) >= 5
    
    def test_install_app(self):
        """Test Probot app installation"""
        response = requests.post(
            f"{BASE_URL}/api/hybrid/probot/install?app_name=stale&repo=test/repo",
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] == True
    
    def test_configure_app(self):
        """Test Probot app configuration"""
        response = requests.post(
            f"{BASE_URL}/api/hybrid/probot/configure?app_name=stale",
            headers=self.headers,
            json={"days_until_stale": 60}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] == True


class TestPHPQualityHybrid:
    """Tests for PHP Code Quality Hybrid"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup authentication"""
        login_response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "admin@nexus.ai", "password": "admin123"}
        )
        if login_response.status_code == 200:
            self.token = login_response.json()["token"]
        else:
            pytest.skip("Could not authenticate")
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_php_quality_capabilities(self):
        """Test PHP Quality capabilities endpoint"""
        response = requests.get(f"{BASE_URL}/api/hybrid/php-quality/capabilities")
        assert response.status_code == 200
        data = response.json()
        
        assert data["name"] == "PHP Code Quality Hybrid"
    
    def test_analyze_code(self):
        """Test PHP code analysis"""
        response = requests.post(
            f"{BASE_URL}/api/hybrid/php-quality/analyze?project_path=/app&tool=phpstan",
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] == True
    
    def test_fix_code_style(self):
        """Test PHP code style fixing"""
        response = requests.post(
            f"{BASE_URL}/api/hybrid/php-quality/fix-style?project_path=/app",
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] == True
    
    def test_detect_duplicates(self):
        """Test code duplication detection"""
        response = requests.post(
            f"{BASE_URL}/api/hybrid/php-quality/detect-duplicates?project_path=/app",
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] == True


class TestJSStateHybrid:
    """Tests for JavaScript State Management Hybrid"""
    
    def test_js_state_capabilities(self):
        """Test JS State capabilities endpoint"""
        response = requests.get(f"{BASE_URL}/api/hybrid/js-state/capabilities")
        assert response.status_code == 200
        data = response.json()
        
        assert data["name"] == "JavaScript State Management Hybrid"
    
    def test_list_libraries(self):
        """Test listing state management libraries"""
        response = requests.get(f"{BASE_URL}/api/hybrid/js-state/libraries")
        assert response.status_code == 200
        data = response.json()
        
        assert "libraries" in data
        assert len(data["libraries"]) >= 5
    
    def test_compare_libraries(self):
        """Test library comparison"""
        response = requests.post(
            f"{BASE_URL}/api/hybrid/js-state/compare",
            json=["redux", "mobx"]
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "comparison" in data
    
    def test_generate_boilerplate(self):
        """Test boilerplate generation"""
        response = requests.post(
            f"{BASE_URL}/api/hybrid/js-state/boilerplate?library=redux&framework=react"
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] == True
        assert data["library"] == "redux"
        assert data["framework"] == "react"


class TestHealthAndBasics:
    """Basic health and connectivity tests"""
    
    def test_health_endpoint(self):
        """Test health endpoint"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
