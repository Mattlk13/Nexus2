import os
import logging
import asyncio
import base64
import io
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from pathlib import Path
from dotenv import load_dotenv
from elevenlabs.client import AsyncElevenLabs
from elevenlabs import VoiceSettings

ROOT_DIR = Path(__file__).parent.parent
load_dotenv(ROOT_DIR / '.env')

logger = logging.getLogger(__name__)

class ElevenLabsService:
    """Service for ElevenLabs voice generation and speech-to-text"""
    
    def __init__(self):
        self.api_key = os.environ.get('ELEVENLABS_API_KEY', '')
        self.client = None
        self.is_active = self._check_active()
        
        if self.is_active:
            self.client = AsyncElevenLabs(api_key=self.api_key, timeout=30.0)
            logger.info("✓ ElevenLabs client initialized")
        else:
            logger.warning("⚠ ElevenLabs API key not configured - service in demo mode")
    
    def _check_active(self) -> bool:
        """Check if ElevenLabs is properly configured"""
        if not self.api_key:
            return False
        placeholder_terms = ['demo', 'placeholder', 'your_key']
        return not any(term in self.api_key.lower() for term in placeholder_terms)
    
    async def generate_speech(
        self,
        text: str,
        voice_id: str = "21m00Tcm4TlvDq8ikWAM",  # Default Rachel voice
        stability: float = 0.5,
        similarity_boost: float = 0.75,
        style: float = 0.0,
        use_speaker_boost: bool = True
    ) -> Dict[str, Any]:
        """Generate speech from text using ElevenLabs TTS"""
        
        if not self.is_active:
            logger.warning("ElevenLabs not configured - returning mock response")
            return {
                "success": False,
                "audio_url": None,
                "mocked": True,
                "message": "ElevenLabs API key required. Add ELEVENLABS_API_KEY to .env"
            }
        
        try:
            voice_settings = VoiceSettings(
                stability=stability,
                similarity_boost=similarity_boost,
                style=style,
                use_speaker_boost=use_speaker_boost
            )
            
            # Generate audio
            audio_generator = self.client.text_to_speech.convert(
                text=text,
                voice_id=voice_id,
                model_id="eleven_multilingual_v2",
                voice_settings=voice_settings
            )
            
            # Collect audio data
            audio_data = b""
            for chunk in audio_generator:
                audio_data += chunk
            
            # Convert to base64 for easy storage/transfer
            audio_b64 = base64.b64encode(audio_data).decode()
            audio_url = f"data:audio/mpeg;base64,{audio_b64}"
            
            logger.info(f"✓ Generated speech: {len(text)} chars → {len(audio_data)} bytes")
            
            return {
                "success": True,
                "audio_url": audio_url,
                "audio_size": len(audio_data),
                "text_length": len(text),
                "voice_id": voice_id,
                "mocked": False
            }
        
        except Exception as e:
            logger.error(f"ElevenLabs TTS error: {e}")
            return {
                "success": False,
                "error": str(e),
                "mocked": False
            }
    
    async def transcribe_audio(self, audio_content: bytes, filename: str = "audio.mp3") -> Dict[str, Any]:
        """Transcribe audio to text using ElevenLabs Speech-to-Text"""
        
        if not self.is_active:
            logger.warning("ElevenLabs not configured - returning mock response")
            return {
                "success": False,
                "text": "",
                "mocked": True,
                "message": "ElevenLabs API key required"
            }
        
        try:
            # Transcribe
            transcription_response = self.client.speech_to_text.convert(
                file=io.BytesIO(audio_content),
                model_id="scribe_v1"
            )
            
            # Extract text
            transcribed_text = transcription_response.text if hasattr(transcription_response, 'text') else str(transcription_response)
            
            logger.info(f"✓ Transcribed audio: {len(audio_content)} bytes → {len(transcribed_text)} chars")
            
            return {
                "success": True,
                "text": transcribed_text,
                "audio_size": len(audio_content),
                "filename": filename,
                "mocked": False
            }
        
        except Exception as e:
            logger.error(f"ElevenLabs STT error: {e}")
            return {
                "success": False,
                "error": str(e),
                "mocked": False
            }
    
    async def get_available_voices(self) -> List[Dict[str, Any]]:
        """Get list of available ElevenLabs voices"""
        
        if not self.is_active:
            return [
                {"voice_id": "demo", "name": "Demo Voice", "category": "premade", "mocked": True}
            ]
        
        try:
            voices_response = await self.client.voices.get_all()
            voices = []
            
            for voice in voices_response.voices if hasattr(voices_response, 'voices') else []:
                voices.append({
                    "voice_id": voice.voice_id if hasattr(voice, 'voice_id') else str(voice),
                    "name": voice.name if hasattr(voice, 'name') else "Unknown",
                    "category": voice.category if hasattr(voice, 'category') else "premade",
                    "description": voice.description if hasattr(voice, 'description') else ""
                })
            
            logger.info(f"✓ Retrieved {len(voices)} ElevenLabs voices")
            return voices
        
        except Exception as e:
            logger.error(f"Error fetching voices: {e}")
            return []

elevenlabs_service = ElevenLabsService()
