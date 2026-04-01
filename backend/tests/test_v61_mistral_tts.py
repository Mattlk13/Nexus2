"""
NEXUS v6.1 Test Suite - Mistral Voxtral TTS & Enterprise Slack Features
Tests:
- Mistral Voxtral TTS (NEW - 7 endpoints)
- Enterprise Slack CRM Bug Fix (MongoDB ObjectId serialization)
- Autonomous Auditor
- Dynamic Router (48+ hybrids)
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestMistralVoxtralTTS:
    """Mistral Voxtral TTS - Open-weight enterprise voice AI"""
    
    def test_capabilities(self):
        """GET /api/v2/hybrid/mistral_tts/capabilities"""
        response = requests.get(f"{BASE_URL}/api/v2/hybrid/mistral_tts/capabilities")
        assert response.status_code == 200
        
        data = response.json()
        assert data["name"] == "Mistral Voxtral TTS"
        assert data["provider"] == "Mistral AI"
        assert data["status"] == "active"
        assert "supported_languages" in data
        assert len(data["supported_languages"]) == 9  # 9 languages
        assert "en" in data["supported_languages"]
        assert "fr" in data["supported_languages"]
        assert "de" in data["supported_languages"]
        assert "es" in data["supported_languages"]
        print("✅ Mistral TTS capabilities endpoint working")
    
    def test_generate_speech_english(self):
        """POST /api/v2/hybrid/mistral_tts/generate - English"""
        response = requests.post(
            f"{BASE_URL}/api/v2/hybrid/mistral_tts/generate",
            json={"text": "Hello, this is a test.", "language": "en"}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "audio_url" in data
        assert data["synthesis"]["language"] == "en"
        assert data["synthesis"]["model_used"] == "Voxtral TTS 3.4B"
        print("✅ Mistral TTS English generation working")
    
    def test_generate_speech_french(self):
        """POST /api/v2/hybrid/mistral_tts/generate - French"""
        response = requests.post(
            f"{BASE_URL}/api/v2/hybrid/mistral_tts/generate",
            json={"text": "Bonjour, ceci est un test.", "language": "fr"}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert data["synthesis"]["language"] == "fr"
        print("✅ Mistral TTS French generation working")
    
    def test_generate_speech_german(self):
        """POST /api/v2/hybrid/mistral_tts/generate - German"""
        response = requests.post(
            f"{BASE_URL}/api/v2/hybrid/mistral_tts/generate",
            json={"text": "Hallo, dies ist ein Test.", "language": "de"}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert data["synthesis"]["language"] == "de"
        print("✅ Mistral TTS German generation working")
    
    def test_generate_speech_spanish(self):
        """POST /api/v2/hybrid/mistral_tts/generate - Spanish"""
        response = requests.post(
            f"{BASE_URL}/api/v2/hybrid/mistral_tts/generate",
            json={"text": "Hola, esta es una prueba.", "language": "es"}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert data["synthesis"]["language"] == "es"
        print("✅ Mistral TTS Spanish generation working")
    
    def test_generate_speech_unsupported_language(self):
        """POST /api/v2/hybrid/mistral_tts/generate - Unsupported language"""
        response = requests.post(
            f"{BASE_URL}/api/v2/hybrid/mistral_tts/generate",
            json={"text": "Test", "language": "xyz"}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == False
        assert "not supported" in data["error"]
        print("✅ Mistral TTS unsupported language handling working")
    
    def test_custom_voice_creation(self):
        """POST /api/v2/hybrid/mistral_tts/voice/custom"""
        response = requests.post(
            f"{BASE_URL}/api/v2/hybrid/mistral_tts/voice/custom",
            json={
                "voice_name": "TEST_CustomVoice",
                "reference_audio": "base64_audio_data",
                "language": "en"
            }
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "voice_profile" in data
        assert data["voice_profile"]["voice_name"] == "TEST_CustomVoice"
        assert data["voice_profile"]["zero_shot_capable"] == True
        assert "_id" not in data["voice_profile"]  # MongoDB ObjectId should be removed
        print("✅ Mistral TTS custom voice creation working (ObjectId fix verified)")
    
    def test_cross_lingual_voice_clone(self):
        """POST /api/v2/hybrid/mistral_tts/voice/cross-lingual - French to German"""
        response = requests.post(
            f"{BASE_URL}/api/v2/hybrid/mistral_tts/voice/cross-lingual",
            json={
                "text": "Guten Tag, wie geht es Ihnen?",
                "source_language": "fr",
                "target_language": "de",
                "voice_reference": "base64_french_audio"
            }
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert data["generation"]["original_voice_language"] == "fr"
        assert data["generation"]["generated_language"] == "de"
        assert data["generation"]["voice_preserved"] == True
        print("✅ Mistral TTS cross-lingual voice cloning working")
    
    def test_benchmarks(self):
        """GET /api/v2/hybrid/mistral_tts/benchmarks"""
        response = requests.get(f"{BASE_URL}/api/v2/hybrid/mistral_tts/benchmarks")
        assert response.status_code == 200
        
        data = response.json()
        assert data["model"] == "Voxtral TTS"
        assert "competitor_comparisons" in data
        assert "elevenlabs_flash_v2.5" in data["competitor_comparisons"]
        assert "technical_advantages" in data
        print("✅ Mistral TTS benchmarks endpoint working")
    
    def test_history(self):
        """GET /api/v2/hybrid/mistral_tts/history"""
        response = requests.get(f"{BASE_URL}/api/v2/hybrid/mistral_tts/history")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "generations" in data
        assert isinstance(data["generations"], list)
        print("✅ Mistral TTS history endpoint working")
    
    def test_voices(self):
        """GET /api/v2/hybrid/mistral_tts/voices"""
        response = requests.get(f"{BASE_URL}/api/v2/hybrid/mistral_tts/voices")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "flagship_voices" in data
        assert "custom_voices" in data
        assert "en" in data["flagship_voices"]
        print("✅ Mistral TTS voices endpoint working")


class TestEnterpriseSlackCRMBugFix:
    """Enterprise Slack CRM - MongoDB ObjectId serialization bug fix"""
    
    def test_crm_contact_creation_no_objectid(self):
        """POST /api/v2/hybrid/enterprise_slack/crm/contacts - Verify ObjectId fix"""
        response = requests.post(
            f"{BASE_URL}/api/v2/hybrid/enterprise_slack/crm/contacts",
            json={
                "name": "TEST_BugFix User",
                "email": "test_bugfix@example.com",
                "company": "Test Corp",
                "tags": ["test", "bugfix"]
            }
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "contact" in data
        assert "_id" not in data["contact"]  # MongoDB ObjectId should be removed
        assert "id" in data["contact"]  # String ID should be present
        print("✅ CRM contact creation working - ObjectId bug fixed")
    
    def test_crm_get_contacts(self):
        """GET /api/v2/hybrid/enterprise_slack/crm/contacts"""
        response = requests.get(f"{BASE_URL}/api/v2/hybrid/enterprise_slack/crm/contacts")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "contacts" in data
        print("✅ CRM get contacts working")


class TestEnterpriseSlackFeatures:
    """Enterprise Slack-Style AI Features"""
    
    def test_capabilities(self):
        """GET /api/v2/hybrid/enterprise_slack/capabilities"""
        response = requests.get(f"{BASE_URL}/api/v2/hybrid/enterprise_slack/capabilities")
        assert response.status_code == 200
        
        data = response.json()
        assert data["name"] == "Enterprise Slack-Style AI"
        assert data["total_features"] == 30
        assert len(data["categories"]) == 4
        print("✅ Enterprise Slack capabilities working")
    
    def test_deep_research(self):
        """POST /api/v2/hybrid/enterprise_slack/research"""
        response = requests.post(
            f"{BASE_URL}/api/v2/hybrid/enterprise_slack/research",
            json={"query": "AI trends 2026", "depth": "comprehensive"}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert data["depth"] == "comprehensive"
        assert data["phases_completed"] == 7
        print("✅ Deep Research working")
    
    def test_meeting_intelligence(self):
        """POST /api/v2/hybrid/enterprise_slack/meetings/analyze"""
        response = requests.post(
            f"{BASE_URL}/api/v2/hybrid/enterprise_slack/meetings/analyze",
            json={
                "transcript": "We discussed the roadmap and agreed on priorities.",
                "participants": ["John", "Sarah"]
            }
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "analysis" in data
        assert "summary" in data["analysis"]
        assert "action_items" in data["analysis"]
        print("✅ Meeting Intelligence working")
    
    def test_mcp_servers(self):
        """GET /api/v2/hybrid/enterprise_slack/mcp/servers"""
        response = requests.get(f"{BASE_URL}/api/v2/hybrid/enterprise_slack/mcp/servers")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert data["total_servers"] == 8
        print("✅ MCP servers listing working")


class TestAutonomousAuditor:
    """Autonomous Auditor - 24/7 platform management"""
    
    def test_capabilities(self):
        """GET /api/v2/hybrid/auditor/capabilities"""
        response = requests.get(f"{BASE_URL}/api/v2/hybrid/auditor/capabilities")
        assert response.status_code == 200
        
        data = response.json()
        assert data["name"] == "Autonomous Auditor"
        assert data["status"] == "active"
        assert "audits" in data
        print("✅ Autonomous Auditor capabilities working")


class TestBackendHealth:
    """Backend health and basic functionality"""
    
    def test_health_check(self):
        """GET /api/health"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        print("✅ Backend health check working")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
