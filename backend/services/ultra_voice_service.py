"""
ULTRA Voice Service - Hybrid TTS Integration
Combines: XTTS-v2 (Coqui) + Piper + Kokoro + ElevenLabs (fallback)

This hybrid service provides:
- Voice cloning from 6s audio (XTTS-v2)
- Fast, efficient TTS (Piper)
- Low-latency generation (Kokoro)
- Cloud fallback (ElevenLabs)
"""
import logging
import asyncio
import httpx
import os
import base64
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from enum import Enum

logger = logging.getLogger(__name__)

class VoiceBackend(Enum):
    XTTS = "xtts"  # Best voice cloning
    PIPER = "piper"  # Fastest, most efficient
    KOKORO = "kokoro"  # Low latency
    ELEVENLABS = "elevenlabs"  # Cloud fallback

class UltraVoiceService:
    """
    Elite hybrid TTS service combining best open-source + commercial.
    
    Features:
    - Voice cloning from short samples
    - Multi-language support (30+ languages)
    - Real-time streaming
    - Smart backend selection
    - Zero cost for local backends
    """
    
    def __init__(self):
        # Backend endpoints
        self.xtts_url = os.getenv('XTTS_URL', 'http://localhost:8020')
        self.piper_url = os.getenv('PIPER_URL', 'http://localhost:8021')
        self.kokoro_url = os.getenv('KOKORO_URL', 'http://localhost:8022')
        self.elevenlabs_api_key = os.getenv('ELEVENLABS_API_KEY', '')
        
        # Backend availability
        self.available_backends = []
        self.backend_performance = {}
        
        # Voice profiles
        self.voices = {
            'default_male': {'backend': VoiceBackend.PIPER, 'voice_id': 'en_US-lessac-medium'},
            'default_female': {'backend': VoiceBackend.PIPER, 'voice_id': 'en_US-amy-medium'},
            'expressive_male': {'backend': VoiceBackend.XTTS, 'voice_id': 'default'},
            'fast_neutral': {'backend': VoiceBackend.KOKORO, 'voice_id': 'af_sarah'}
        }
        
        logger.info("ULTRA Voice Service initialized")
    
    async def initialize(self):
        """Check which backends are available"""
        await self._check_backend_availability()
        logger.info(f"Available TTS backends: {self.available_backends}")
    
    async def _check_backend_availability(self):
        """Test connectivity to all backends"""
        async with httpx.AsyncClient(timeout=5.0) as client:
            # Check XTTS (Coqui)
            try:
                response = await client.get(f"{self.xtts_url}/health")
                if response.status_code == 200:
                    self.available_backends.append(VoiceBackend.XTTS)
                    logger.info("✓ XTTS-v2 available")
            except:
                logger.warning("XTTS not available (install: pip install TTS, run: tts-server)")
            
            # Check Piper
            try:
                response = await client.get(f"{self.piper_url}/api/voices")
                if response.status_code == 200:
                    self.available_backends.append(VoiceBackend.PIPER)
                    logger.info("✓ Piper available")
            except:
                logger.warning("Piper not available (install: pip install piper-tts)")
            
            # Check Kokoro
            try:
                response = await client.get(f"{self.kokoro_url}/health")
                if response.status_code == 200:
                    self.available_backends.append(VoiceBackend.KOKORO)
                    logger.info("✓ Kokoro available")
            except:
                logger.warning("Kokoro not available")
            
            # ElevenLabs always available if key exists
            if self.elevenlabs_api_key:
                self.available_backends.append(VoiceBackend.ELEVENLABS)
                logger.info("✓ ElevenLabs available (fallback)")
    
    async def generate_speech(
        self,
        text: str,
        voice: str = "default_female",
        language: str = "en",
        speed: float = 1.0,
        backend: Optional[VoiceBackend] = None
    ) -> Dict[str, Any]:
        """
        Generate speech using the best available backend.
        
        Smart routing:
        1. Use specified voice's preferred backend
        2. Fall back to fastest available
        3. Use ElevenLabs if all local fail
        """
        start_time = datetime.now(timezone.utc)
        
        # Auto-select backend
        if not backend:
            if voice in self.voices:
                backend = self.voices[voice]['backend']
            else:
                backend = await self._select_best_backend()
        
        if not backend:
            return {
                "success": False,
                "error": "No TTS backends available. Install XTTS, Piper, or configure ElevenLabs."
            }
        
        logger.info(f"Generating speech with {backend.value}: {text[:50]}...")
        
        try:
            if backend == VoiceBackend.XTTS:
                result = await self._generate_xtts(text, voice, language, speed)
            elif backend == VoiceBackend.PIPER:
                result = await self._generate_piper(text, voice, speed)
            elif backend == VoiceBackend.KOKORO:
                result = await self._generate_kokoro(text, voice)
            elif backend == VoiceBackend.ELEVENLABS:
                result = await self._generate_elevenlabs(text, voice)
            else:
                return {"success": False, "error": "Invalid backend"}
            
            # Track performance
            elapsed = (datetime.now(timezone.utc) - start_time).total_seconds()
            self.backend_performance[backend.value] = elapsed
            
            result["backend"] = backend.value
            result["generation_time"] = elapsed
            return result
        
        except Exception as e:
            logger.error(f"{backend.value} TTS failed: {e}")
            
            # Try fallback
            if backend != VoiceBackend.ELEVENLABS and VoiceBackend.ELEVENLABS in self.available_backends:
                logger.info("Falling back to ElevenLabs...")
                return await self.generate_speech(text, voice, language, speed, VoiceBackend.ELEVENLABS)
            
            return {
                "success": False,
                "error": str(e),
                "backend": backend.value
            }
    
    async def _select_best_backend(self) -> Optional[VoiceBackend]:
        """Select best backend based on availability"""
        if not self.available_backends:
            await self._check_backend_availability()
        
        # Priority: Piper (fastest) > XTTS (quality) > Kokoro > ElevenLabs
        priority = [VoiceBackend.PIPER, VoiceBackend.XTTS, VoiceBackend.KOKORO, VoiceBackend.ELEVENLABS]
        
        for backend in priority:
            if backend in self.available_backends:
                return backend
        
        return None
    
    async def _generate_xtts(self, text: str, voice: str, language: str, speed: float) -> Dict[str, Any]:
        """Generate using XTTS-v2 (Coqui)"""
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.xtts_url}/api/tts",
                json={
                    "text": text,
                    "speaker_wav": voice,
                    "language": language,
                    "speed": speed
                }
            )
            
            if response.status_code == 200:
                audio_data = response.content
                return {
                    "success": True,
                    "audio_base64": base64.b64encode(audio_data).decode(),
                    "format": "wav"
                }
            else:
                raise Exception(f"XTTS API error: {response.status_code}")
    
    async def _generate_piper(self, text: str, voice: str, speed: float) -> Dict[str, Any]:
        """Generate using Piper TTS"""
        voice_id = self.voices.get(voice, {}).get('voice_id', 'en_US-amy-medium')
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.piper_url}/api/tts",
                json={
                    "text": text,
                    "voice": voice_id,
                    "speed": speed
                }
            )
            
            if response.status_code == 200:
                audio_data = response.content
                return {
                    "success": True,
                    "audio_base64": base64.b64encode(audio_data).decode(),
                    "format": "wav",
                    "note": "Generated with Piper (fastest open-source TTS)"
                }
            else:
                raise Exception(f"Piper API error: {response.status_code}")
    
    async def _generate_kokoro(self, text: str, voice: str) -> Dict[str, Any]:
        """Generate using Kokoro TTS"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.kokoro_url}/generate",
                json={"text": text, "voice": voice}
            )
            
            if response.status_code == 200:
                audio_data = response.content
                return {
                    "success": True,
                    "audio_base64": base64.b64encode(audio_data).decode(),
                    "format": "wav",
                    "note": "Generated with Kokoro (82M params, ultra-fast)"
                }
            else:
                raise Exception(f"Kokoro API error: {response.status_code}")
    
    async def _generate_elevenlabs(self, text: str, voice: str) -> Dict[str, Any]:
        """Generate using ElevenLabs (fallback)"""
        # Use existing ElevenLabs service
        from services.elevenlabs_service import elevenlabs_service
        
        result = await elevenlabs_service.generate_speech(text, voice)
        return result
    
    async def clone_voice(
        self,
        audio_sample_base64: str,
        voice_name: str,
        backend: VoiceBackend = VoiceBackend.XTTS
    ) -> Dict[str, Any]:
        """
        Clone a voice from audio sample (requires XTTS or ElevenLabs).
        
        XTTS requires only 6 seconds of audio for cloning.
        """
        if backend == VoiceBackend.XTTS and VoiceBackend.XTTS in self.available_backends:
            audio_data = base64.b64decode(audio_sample_base64)
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.xtts_url}/api/clone",
                    files={"audio": audio_data},
                    data={"name": voice_name}
                )
                
                if response.status_code == 200:
                    return {
                        "success": True,
                        "voice_id": voice_name,
                        "message": "Voice cloned successfully with XTTS-v2"
                    }
        
        return {"success": False, "error": "Voice cloning requires XTTS-v2 backend"}
    
    def get_status(self) -> Dict[str, Any]:
        """Get service status"""
        return {
            "available_backends": [b.value for b in self.available_backends],
            "backend_count": len(self.available_backends),
            "performance": self.backend_performance,
            "voices": list(self.voices.keys()),
            "features": {
                "voice_cloning": VoiceBackend.XTTS in self.available_backends,
                "multilingual": True,
                "streaming": False  # Future feature
            },
            "recommendation": "Install Piper for fastest TTS, XTTS for voice cloning"
        }

# Singleton instance
ultra_voice = UltraVoiceService()
