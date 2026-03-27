"""
NEXUS Hybrid Services Test Suite - Iteration 12
Tests ML Hybrid, Net Neutrality Hybrid, Ultimate Controller, and other hybrid services
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestUltimateController:
    """Tests for Ultimate Controller - manages 14 hybrid systems"""
    
    def test_controller_status_shows_14_hybrids(self):
        """Verify Ultimate Controller shows 14 active hybrids"""
        response = requests.get(f"{BASE_URL}/api/hybrid/controller/status")
        assert response.status_code == 200
        data = response.json()
        
        assert data["total_hybrids"] == 14, f"Expected 14 hybrids, got {data['total_hybrids']}"
        assert data["active_hybrids"] == 14, f"Expected 14 active hybrids, got {data['active_hybrids']}"
        assert data["status"] == "operational"
        
        # Verify all categories are present
        categories = data["by_category"]
        assert "ai" in categories
        assert "business" in categories
        assert "security" in categories
        assert "advocacy" in categories  # Net Neutrality
        
        # Verify ML and Net Neutrality are in the list
        ai_hybrids = [h["id"] for h in categories["ai"]]
        assert "ml" in ai_hybrids, "ML hybrid should be in AI category"
        
        advocacy_hybrids = [h["id"] for h in categories["advocacy"]]
        assert "netneutrality" in advocacy_hybrids, "Net Neutrality hybrid should be in advocacy category"


class TestMLHybrid:
    """Tests for Machine Learning Hybrid Service"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test fixtures"""
        # Register/login to get token
        register_response = requests.post(
            f"{BASE_URL}/api/auth/register",
            json={
                "email": f"test_ml_{time.time()}@nexus.ai",
                "password": "testpass123",
                "username": f"test_ml_{int(time.time())}",
                "name": "ML Test User"
            }
        )
        if register_response.status_code == 200:
            self.token = register_response.json()["token"]
        else:
            # Try login
            login_response = requests.post(
                f"{BASE_URL}/api/auth/login",
                json={"email": "admin@nexus.ai", "password": "admin123"}
            )
            if login_response.status_code == 200:
                self.token = login_response.json()["token"]
            else:
                pytest.skip("Could not authenticate")
        
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_ml_capabilities(self):
        """Test ML capabilities endpoint"""
        response = requests.get(f"{BASE_URL}/api/hybrid/ml/capabilities")
        assert response.status_code == 200
        data = response.json()
        
        assert data["name"] == "Machine Learning Hybrid"
        assert "frameworks" in data
        assert "tensorflow" in data["frameworks"]
        assert "pytorch" in data["frameworks"]
        assert "scikit-learn" in data["frameworks"]
        
        # Verify features
        assert data["features"]["model_training"]["automl"] == True
        assert data["features"]["marketplace"]["publish_models"] == True
    
    def test_pretrained_models(self):
        """Test pre-trained models listing"""
        response = requests.get(f"{BASE_URL}/api/hybrid/ml/pretrained-models")
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] == True
        assert "vision" in data["categories"]
        assert "nlp" in data["categories"]
        assert "audio" in data["categories"]
        assert data["total_models"] >= 10
        
        # Verify specific models
        assert "resnet50" in data["models"]["vision"]
        assert "bert-base" in data["models"]["nlp"]
    
    def test_pretrained_models_by_category(self):
        """Test pre-trained models filtered by category"""
        response = requests.get(f"{BASE_URL}/api/hybrid/ml/pretrained-models?category=vision")
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] == True
        assert data["category"] == "vision"
        assert "resnet50" in data["models"]
    
    def test_create_training_job(self):
        """Test ML training job creation"""
        response = requests.post(
            f"{BASE_URL}/api/hybrid/ml/training-job",
            headers=self.headers,
            json={
                "name": "TEST_Classification_Model",
                "task_type": "classification",
                "framework": "tensorflow"
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] == True
        assert "job" in data
        assert data["job"]["name"] == "TEST_Classification_Model"
        assert data["job"]["task_type"] == "classification"
        assert data["job"]["framework"] == "tensorflow"
        assert data["job"]["status"] == "created"
    
    def test_upload_dataset(self):
        """Test dataset upload"""
        response = requests.post(
            f"{BASE_URL}/api/hybrid/ml/dataset",
            headers=self.headers,
            json={
                "name": "TEST_Customer_Dataset",
                "task_type": "classification",
                "num_samples": 1000,
                "num_features": 10,
                "format": "csv"
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] == True
        assert "dataset" in data
        assert data["dataset"]["name"] == "TEST_Customer_Dataset"
        assert data["dataset"]["num_samples"] == 1000
    
    def test_automl(self):
        """Test AutoML endpoint"""
        response = requests.post(
            f"{BASE_URL}/api/hybrid/ml/automl?dataset_id=test_dataset&task_type=classification",
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] == True
        assert "automl_recommendation" in data
        assert "training_job" in data
    
    def test_marketplace_search(self):
        """Test ML marketplace search"""
        response = requests.post(
            f"{BASE_URL}/api/hybrid/ml/marketplace/search",
            json={"task_type": "classification"}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] == True
        assert "results" in data
        assert len(data["results"]) > 0
    
    def test_predict(self):
        """Test prediction endpoint"""
        response = requests.post(
            f"{BASE_URL}/api/hybrid/ml/predict/test_model",
            headers=self.headers,
            json={"features": [1.0, 2.0, 3.0, 4.0]}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] == True
        assert "prediction" in data
        assert "confidence" in data["prediction"]


class TestNetNeutralityHybrid:
    """Tests for Net Neutrality & Digital Rights Hybrid Service"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test fixtures"""
        # Register/login to get token
        register_response = requests.post(
            f"{BASE_URL}/api/auth/register",
            json={
                "email": f"test_nn_{time.time()}@nexus.ai",
                "password": "testpass123",
                "username": f"test_nn_{int(time.time())}",
                "name": "NN Test User",
                "role": "admin"
            }
        )
        if register_response.status_code == 200:
            self.token = register_response.json()["token"]
        else:
            # Try login
            login_response = requests.post(
                f"{BASE_URL}/api/auth/login",
                json={"email": "admin@nexus.ai", "password": "admin123"}
            )
            if login_response.status_code == 200:
                self.token = login_response.json()["token"]
            else:
                pytest.skip("Could not authenticate")
        
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_netneutrality_capabilities(self):
        """Test Net Neutrality capabilities endpoint"""
        response = requests.get(f"{BASE_URL}/api/hybrid/netneutrality/capabilities")
        assert response.status_code == 200
        data = response.json()
        
        assert data["name"] == "Net Neutrality & Digital Rights Hybrid"
        assert data["categories"]["advocacy"]["campaign_management"] == True
        assert data["categories"]["advocacy"]["petition_system"] == True
        assert data["categories"]["congressional_contact"]["representative_lookup"] == True
        assert data["categories"]["monitoring"]["throttling_simulation"] == True
    
    def test_internet_health_monitoring(self):
        """Test internet health monitoring"""
        response = requests.get(f"{BASE_URL}/api/hybrid/netneutrality/internet-health?region=global")
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] == True
        assert "health" in data
        assert data["health"]["region"] == "global"
        assert "overall_score" in data["health"]
        assert "metrics" in data["health"]
        
        # Verify metrics
        metrics = data["health"]["metrics"]
        assert "content_accessibility" in metrics
        assert "privacy_protections" in metrics
        assert "net_neutrality_compliance" in metrics
    
    def test_find_representatives(self):
        """Test representative lookup by ZIP code"""
        response = requests.get(f"{BASE_URL}/api/hybrid/netneutrality/representatives/10001")
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] == True
        assert data["zip_code"] == "10001"
        assert "representatives" in data
        assert len(data["representatives"]) >= 1
        
        # Verify representative structure
        rep = data["representatives"][0]
        assert "name" in rep
        assert "position" in rep
        assert "phone" in rep
    
    def test_get_call_script(self):
        """Test call script generation"""
        response = requests.get(f"{BASE_URL}/api/hybrid/netneutrality/call-script/net_neutrality")
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] == True
        assert data["issue"] == "net_neutrality"
        assert "script" in data
        assert "introduction" in data["script"]
        assert "main_message" in data["script"]
        assert "key_points" in data["script"]
        assert "tips" in data
    
    def test_create_campaign(self):
        """Test campaign creation"""
        response = requests.post(
            f"{BASE_URL}/api/hybrid/netneutrality/campaign",
            headers=self.headers,
            json={
                "title": "TEST_Save_Net_Neutrality",
                "description": "Test campaign for net neutrality",
                "type": "petition",
                "target": "congress",
                "goal": 10000
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] == True
        assert "campaign" in data
        assert data["campaign"]["title"] == "TEST_Save_Net_Neutrality"
        assert data["campaign"]["goal"] == 10000
        assert data["campaign"]["signatures"] == 0
        assert data["campaign"]["status"] == "active"
    
    def test_sign_petition(self):
        """Test petition signing"""
        # First create a campaign
        campaign_response = requests.post(
            f"{BASE_URL}/api/hybrid/netneutrality/campaign",
            headers=self.headers,
            json={
                "title": "TEST_Petition_Campaign",
                "type": "petition",
                "goal": 1000
            }
        )
        campaign_id = campaign_response.json()["campaign"]["id"]
        
        # Sign the petition
        response = requests.post(
            f"{BASE_URL}/api/hybrid/netneutrality/petition/sign",
            headers=self.headers,
            json={
                "campaign_id": campaign_id,
                "name": "Test User",
                "email": "test@example.com",
                "zip_code": "10001",
                "comment": "I support net neutrality!"
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] == True
        assert "message" in data


class TestMusicHybrid:
    """Tests for Music Hybrid Service"""
    
    def test_music_capabilities(self):
        """Test music capabilities endpoint"""
        response = requests.get(f"{BASE_URL}/api/hybrid/music/capabilities")
        assert response.status_code == 200
        data = response.json()
        
        assert "audio_formats" in data
        assert "mp3" in data["audio_formats"]
        assert "features" in data
        assert "AI music generation" in data["features"]
        assert data["status"] == "operational"


class TestMCPHybrid:
    """Tests for MCP (Model Context Protocol) Hybrid Service"""
    
    def test_mcp_discover(self):
        """Test MCP server discovery"""
        response = requests.get(f"{BASE_URL}/api/hybrid/mcp/discover")
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] == True
        assert "servers" in data
    
    def test_mcp_capabilities(self):
        """Test MCP capabilities"""
        response = requests.get(f"{BASE_URL}/api/hybrid/mcp/capabilities")
        assert response.status_code == 200
        data = response.json()
        
        # MCP returns capabilities list and categories
        assert "capabilities" in data or "name" in data
        assert "total_capabilities" in data or "servers" in data


class TestDevOpsHybrid:
    """Tests for DevOps Hybrid Service"""
    
    def test_devops_capabilities(self):
        """Test DevOps capabilities"""
        response = requests.get(f"{BASE_URL}/api/hybrid/devops/capabilities")
        assert response.status_code == 200
        data = response.json()
        
        # DevOps returns infrastructure, containers, deployment, etc.
        assert "infrastructure" in data or "name" in data
        assert "deployment" in data or "features" in data


class TestFrontendHybrid:
    """Tests for Frontend Hybrid Service"""
    
    def test_list_frameworks(self):
        """Test framework listing"""
        response = requests.get(f"{BASE_URL}/api/hybrid/frontend/frameworks")
        assert response.status_code == 200
        data = response.json()
        
        assert "frameworks" in data
        assert "total" in data
        assert data["total"] > 0
    
    def test_frontend_capabilities(self):
        """Test frontend capabilities"""
        response = requests.get(f"{BASE_URL}/api/hybrid/frontend/capabilities")
        assert response.status_code == 200
        data = response.json()
        
        # Frontend returns frameworks list and features
        assert "frameworks" in data or "name" in data
        assert "features" in data or "frameworks_supported" in data


class TestGamingHybrid:
    """Tests for Gaming Hybrid Service"""
    
    def test_gaming_capabilities(self):
        """Test gaming capabilities"""
        response = requests.get(f"{BASE_URL}/api/hybrid/gaming/capabilities")
        assert response.status_code == 200
        data = response.json()
        
        assert "name" in data or "engines" in data
    
    def test_gaming_templates(self):
        """Test gaming templates"""
        response = requests.get(f"{BASE_URL}/api/hybrid/gaming/templates")
        assert response.status_code == 200
        data = response.json()
        
        assert "templates" in data or isinstance(data, list)


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
