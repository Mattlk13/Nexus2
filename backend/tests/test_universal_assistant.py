"""
Test Suite for NEXUS Universal AI Assistant
Tests the Universal Router Service endpoints:
- /api/universal/status
- /api/universal/services
- /api/universal/process
- /api/universal/history/{session_id}
"""

import pytest
import requests
import os
import time
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestUniversalAssistantStatus:
    """Test Universal Agent status endpoint"""
    
    def test_status_endpoint_returns_200(self):
        """Test that status endpoint is accessible"""
        response = requests.get(f"{BASE_URL}/api/universal/status")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print(f"✓ Status endpoint returned 200")
    
    def test_status_response_structure(self):
        """Test status response has correct structure"""
        response = requests.get(f"{BASE_URL}/api/universal/status")
        data = response.json()
        
        # Verify required fields
        assert "status" in data, "Missing 'status' field"
        assert "name" in data, "Missing 'name' field"
        assert "description" in data, "Missing 'description' field"
        assert "total_services" in data, "Missing 'total_services' field"
        assert "llm_model" in data, "Missing 'llm_model' field"
        assert "capabilities" in data, "Missing 'capabilities' field"
        
        # Verify values
        assert data["status"] == "active", f"Expected status 'active', got '{data['status']}'"
        assert data["total_services"] >= 30, f"Expected at least 30 services, got {data['total_services']}"
        assert "GPT-5.1" in data["llm_model"], f"Expected GPT-5.1 in llm_model, got '{data['llm_model']}'"
        
        print(f"✓ Status response structure valid: {data['total_services']} services available")


class TestUniversalAssistantServices:
    """Test Universal Agent services endpoint"""
    
    def test_services_endpoint_returns_200(self):
        """Test that services endpoint is accessible"""
        response = requests.get(f"{BASE_URL}/api/universal/services")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print(f"✓ Services endpoint returned 200")
    
    def test_services_response_structure(self):
        """Test services response has correct structure"""
        response = requests.get(f"{BASE_URL}/api/universal/services")
        data = response.json()
        
        # Verify required fields
        assert "total_services" in data, "Missing 'total_services' field"
        assert "services" in data, "Missing 'services' field"
        assert isinstance(data["services"], dict), "Services should be a dictionary"
        
        # Verify service count matches
        assert data["total_services"] == len(data["services"]), "Service count mismatch"
        
        print(f"✓ Services response valid: {data['total_services']} services listed")
    
    def test_services_have_required_fields(self):
        """Test each service has required fields"""
        response = requests.get(f"{BASE_URL}/api/universal/services")
        data = response.json()
        
        for intent, info in data["services"].items():
            assert "service" in info, f"Service '{intent}' missing 'service' field"
            assert "description" in info, f"Service '{intent}' missing 'description' field"
        
        print(f"✓ All {len(data['services'])} services have required fields")
    
    def test_key_services_present(self):
        """Test that key services are available"""
        response = requests.get(f"{BASE_URL}/api/universal/services")
        data = response.json()
        services = data["services"]
        
        # Key services that should be present
        key_intents = [
            "image_generation",
            "video_generation",
            "music_generation",
            "multi_agent",
            "code_analysis",
            "accessibility",
            "payments"
        ]
        
        for intent in key_intents:
            assert intent in services, f"Missing key service: {intent}"
        
        print(f"✓ All {len(key_intents)} key services present")


class TestUniversalAssistantProcess:
    """Test Universal Agent process endpoint - Intent Classification"""
    
    def test_process_endpoint_requires_message(self):
        """Test that process endpoint requires a message"""
        response = requests.post(
            f"{BASE_URL}/api/universal/process",
            json={}
        )
        # Should return 422 for validation error
        assert response.status_code == 422, f"Expected 422 for missing message, got {response.status_code}"
        print(f"✓ Process endpoint correctly validates required message field")
    
    def test_process_image_generation_intent(self):
        """Test intent classification for image generation"""
        session_id = f"test_session_{uuid.uuid4().hex[:8]}"
        response = requests.post(
            f"{BASE_URL}/api/universal/process",
            json={
                "message": "Generate an image of a futuristic city with flying cars",
                "session_id": session_id
            }
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        # Verify response structure
        assert "success" in data, "Missing 'success' field"
        assert "response" in data, "Missing 'response' field"
        assert "routed_to" in data, "Missing 'routed_to' field"
        assert "metadata" in data, "Missing 'metadata' field"
        
        # Verify intent classification
        assert data["success"] == True, "Request should succeed"
        assert data["routed_to"] == "image_generation", f"Expected 'image_generation', got '{data['routed_to']}'"
        
        # Verify metadata
        assert "confidence" in data["metadata"], "Missing confidence in metadata"
        assert data["metadata"]["confidence"] >= 0.5, f"Low confidence: {data['metadata']['confidence']}"
        
        print(f"✓ Image generation intent classified correctly (confidence: {data['metadata']['confidence']:.2%})")
    
    def test_process_music_generation_intent(self):
        """Test intent classification for music generation"""
        session_id = f"test_session_{uuid.uuid4().hex[:8]}"
        response = requests.post(
            f"{BASE_URL}/api/universal/process",
            json={
                "message": "Create a lo-fi hip hop beat for studying",
                "session_id": session_id
            }
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        assert data["success"] == True, "Request should succeed"
        assert data["routed_to"] == "music_generation", f"Expected 'music_generation', got '{data['routed_to']}'"
        
        print(f"✓ Music generation intent classified correctly (confidence: {data['metadata']['confidence']:.2%})")
    
    def test_process_multi_agent_intent(self):
        """Test intent classification for multi-agent workflows"""
        session_id = f"test_session_{uuid.uuid4().hex[:8]}"
        response = requests.post(
            f"{BASE_URL}/api/universal/process",
            json={
                "message": "Run a multi-agent research team to analyze market trends",
                "session_id": session_id
            }
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        assert data["success"] == True, "Request should succeed"
        assert data["routed_to"] == "multi_agent", f"Expected 'multi_agent', got '{data['routed_to']}'"
        
        print(f"✓ Multi-agent intent classified correctly (confidence: {data['metadata']['confidence']:.2%})")
    
    def test_process_code_analysis_intent(self):
        """Test intent classification for code analysis"""
        session_id = f"test_session_{uuid.uuid4().hex[:8]}"
        response = requests.post(
            f"{BASE_URL}/api/universal/process",
            json={
                "message": "Analyze my Python code for bugs and performance issues",
                "session_id": session_id
            }
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        assert data["success"] == True, "Request should succeed"
        assert data["routed_to"] == "code_analysis", f"Expected 'code_analysis', got '{data['routed_to']}'"
        
        print(f"✓ Code analysis intent classified correctly (confidence: {data['metadata']['confidence']:.2%})")
    
    def test_process_accessibility_intent(self):
        """Test intent classification for accessibility"""
        session_id = f"test_session_{uuid.uuid4().hex[:8]}"
        response = requests.post(
            f"{BASE_URL}/api/universal/process",
            json={
                "message": "Run an accessibility audit on my website for WCAG compliance",
                "session_id": session_id
            }
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        assert data["success"] == True, "Request should succeed"
        assert data["routed_to"] == "accessibility", f"Expected 'accessibility', got '{data['routed_to']}'"
        
        print(f"✓ Accessibility intent classified correctly (confidence: {data['metadata']['confidence']:.2%})")
    
    def test_process_video_generation_intent(self):
        """Test intent classification for video generation"""
        session_id = f"test_session_{uuid.uuid4().hex[:8]}"
        response = requests.post(
            f"{BASE_URL}/api/universal/process",
            json={
                "message": "Generate a short promotional video for my product",
                "session_id": session_id
            }
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        assert data["success"] == True, "Request should succeed"
        assert data["routed_to"] == "video_generation", f"Expected 'video_generation', got '{data['routed_to']}'"
        
        print(f"✓ Video generation intent classified correctly (confidence: {data['metadata']['confidence']:.2%})")
    
    def test_process_response_contains_service_info(self):
        """Test that process response contains service information"""
        session_id = f"test_session_{uuid.uuid4().hex[:8]}"
        response = requests.post(
            f"{BASE_URL}/api/universal/process",
            json={
                "message": "Help me discover AI tools on GitHub",
                "session_id": session_id
            }
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        # Verify service_used is present
        assert "service_used" in data, "Missing 'service_used' field"
        assert data["service_used"] is not None, "service_used should not be None"
        
        # Verify metadata contains reasoning
        assert "reasoning" in data["metadata"], "Missing reasoning in metadata"
        
        print(f"✓ Response contains service info: {data['service_used']}")


class TestUniversalAssistantHistory:
    """Test Universal Agent conversation history endpoint"""
    
    def test_history_endpoint_returns_200(self):
        """Test that history endpoint is accessible"""
        session_id = f"test_session_{uuid.uuid4().hex[:8]}"
        response = requests.get(f"{BASE_URL}/api/universal/history/{session_id}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print(f"✓ History endpoint returned 200")
    
    def test_history_response_structure(self):
        """Test history response has correct structure"""
        session_id = f"test_session_{uuid.uuid4().hex[:8]}"
        response = requests.get(f"{BASE_URL}/api/universal/history/{session_id}")
        data = response.json()
        
        # Verify required fields
        assert "session_id" in data, "Missing 'session_id' field"
        assert "total" in data, "Missing 'total' field"
        assert "conversations" in data, "Missing 'conversations' field"
        assert isinstance(data["conversations"], list), "Conversations should be a list"
        
        print(f"✓ History response structure valid")
    
    def test_history_persists_conversation(self):
        """Test that conversation history is persisted in MongoDB"""
        session_id = f"test_persist_{uuid.uuid4().hex[:8]}"
        
        # Send a message
        process_response = requests.post(
            f"{BASE_URL}/api/universal/process",
            json={
                "message": "TEST_HISTORY: Generate a test image",
                "session_id": session_id
            }
        )
        assert process_response.status_code == 200, "Process request failed"
        
        # Wait for MongoDB write
        time.sleep(1)
        
        # Retrieve history
        history_response = requests.get(f"{BASE_URL}/api/universal/history/{session_id}")
        assert history_response.status_code == 200, "History request failed"
        
        data = history_response.json()
        
        # Verify conversation was stored
        assert data["total"] >= 1, f"Expected at least 1 conversation, got {data['total']}"
        
        # Verify conversation content
        conversations = data["conversations"]
        found_test_message = False
        for conv in conversations:
            if "TEST_HISTORY" in conv.get("user_message", ""):
                found_test_message = True
                assert "intent" in conv, "Missing intent in conversation"
                assert "assistant_response" in conv, "Missing assistant_response in conversation"
                break
        
        assert found_test_message, "Test message not found in history"
        
        print(f"✓ Conversation history persisted correctly ({data['total']} conversations)")
    
    def test_history_limit_parameter(self):
        """Test that history limit parameter works"""
        session_id = f"test_limit_{uuid.uuid4().hex[:8]}"
        
        # Send multiple messages
        for i in range(3):
            requests.post(
                f"{BASE_URL}/api/universal/process",
                json={
                    "message": f"TEST_LIMIT_{i}: Test message {i}",
                    "session_id": session_id
                }
            )
            time.sleep(0.5)
        
        # Wait for MongoDB writes
        time.sleep(1)
        
        # Retrieve with limit
        response = requests.get(f"{BASE_URL}/api/universal/history/{session_id}?limit=2")
        assert response.status_code == 200, "History request failed"
        
        data = response.json()
        # Note: limit may return fewer if there are fewer conversations
        assert len(data["conversations"]) <= 2, f"Expected at most 2 conversations, got {len(data['conversations'])}"
        
        print(f"✓ History limit parameter works correctly")


class TestUniversalAssistantWithAuth:
    """Test Universal Agent with authentication (optional auth)"""
    
    def test_process_works_without_auth(self):
        """Test that process endpoint works without authentication"""
        session_id = f"test_noauth_{uuid.uuid4().hex[:8]}"
        response = requests.post(
            f"{BASE_URL}/api/universal/process",
            json={
                "message": "Generate a simple image",
                "session_id": session_id
            }
        )
        
        assert response.status_code == 200, f"Expected 200 without auth, got {response.status_code}"
        data = response.json()
        assert data["success"] == True, "Request should succeed without auth"
        
        print(f"✓ Process endpoint works without authentication")
    
    def test_process_works_with_auth(self):
        """Test that process endpoint works with authentication"""
        # First, register/login to get a token
        test_email = f"test_universal_{uuid.uuid4().hex[:8]}@test.com"
        test_password = "testpass123"
        test_username = f"testuser_{uuid.uuid4().hex[:8]}"
        
        # Register
        register_response = requests.post(
            f"{BASE_URL}/api/auth/register",
            json={
                "email": test_email,
                "password": test_password,
                "username": test_username
            }
        )
        
        if register_response.status_code == 200:
            token = register_response.json().get("token")
        else:
            # Try login if user exists
            login_response = requests.post(
                f"{BASE_URL}/api/auth/login",
                json={"email": test_email, "password": test_password}
            )
            if login_response.status_code == 200:
                token = login_response.json().get("token")
            else:
                pytest.skip("Could not authenticate for auth test")
                return
        
        # Test with auth
        session_id = f"test_auth_{uuid.uuid4().hex[:8]}"
        response = requests.post(
            f"{BASE_URL}/api/universal/process",
            json={
                "message": "Generate an image with authentication",
                "session_id": session_id
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200, f"Expected 200 with auth, got {response.status_code}"
        data = response.json()
        assert data["success"] == True, "Request should succeed with auth"
        
        print(f"✓ Process endpoint works with authentication")


class TestUniversalAssistantErrorHandling:
    """Test Universal Agent error handling"""
    
    def test_invalid_session_id_format(self):
        """Test handling of various session ID formats"""
        # Empty session_id should use default
        response = requests.post(
            f"{BASE_URL}/api/universal/process",
            json={
                "message": "Test message",
                "session_id": ""
            }
        )
        # Should still work with empty session_id (uses default)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print(f"✓ Empty session_id handled correctly")
    
    def test_very_long_message(self):
        """Test handling of very long messages"""
        long_message = "Test " * 1000  # 5000 characters
        session_id = f"test_long_{uuid.uuid4().hex[:8]}"
        
        response = requests.post(
            f"{BASE_URL}/api/universal/process",
            json={
                "message": long_message,
                "session_id": session_id
            }
        )
        
        # Should handle long messages gracefully
        assert response.status_code in [200, 422], f"Unexpected status: {response.status_code}"
        print(f"✓ Long message handled correctly (status: {response.status_code})")
    
    def test_special_characters_in_message(self):
        """Test handling of special characters in messages"""
        special_message = "Generate an image with émojis 🎨 and spëcial çharacters <script>alert('test')</script>"
        session_id = f"test_special_{uuid.uuid4().hex[:8]}"
        
        response = requests.post(
            f"{BASE_URL}/api/universal/process",
            json={
                "message": special_message,
                "session_id": session_id
            }
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data["success"] == True, "Request should succeed with special characters"
        
        print(f"✓ Special characters handled correctly")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
