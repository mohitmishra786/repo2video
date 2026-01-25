"""
Audio Generation Module for Advanced Animation System

This module handles text-to-speech generation using ElevenLabs API
for creating voice narration for video scenes.
"""

import os
import logging
import requests
from typing import Optional, Dict, Any, TYPE_CHECKING
if TYPE_CHECKING:
    from ..core.data_structures import Storyboard
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class AudioGenerator:
    """Handles text-to-speech generation using ElevenLabs API."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the audio generator.
        
        Args:
            api_key: ElevenLabs API key. If not provided, will try to load from environment.
        """
        self.api_key = api_key or os.getenv('ELEVENLABS_API_KEY')
        self.base_url = "https://api.elevenlabs.io/v1"
        
        if not self.api_key:
            logger.warning("ElevenLabs API key not provided. Audio generation will be disabled.")
            self.available = False
        else:
            self.available = True
            logger.info("ElevenLabs audio generator initialized successfully")
        
        # Default voice settings
        self.default_voice_id = "21m00Tcm4TlvDq8ikWAM"  # Rachel voice
        self.default_settings = {
            "stability": 0.5,
            "similarity_boost": 0.75,
            "style": 0.0,
            "use_speaker_boost": True
        }
    
    def generate_audio(self, text: str, output_path: str, voice_id: Optional[str] = None) -> bool:
        """
        Generate audio from text using ElevenLabs API.
        
        Args:
            text: Text to convert to speech
            output_path: Path where the audio file should be saved
            voice_id: Voice ID to use. If not provided, uses default voice.
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.available:
            logger.error("Audio generation not available - no API key provided")
            return False
        
        if not text.strip():
            logger.warning("Empty text provided for audio generation")
            return False
        
        try:
            voice_id = voice_id or self.default_voice_id
            
            # Prepare the request
            url = f"{self.base_url}/text-to-speech/{voice_id}"
            
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": self.api_key
            }
            
            data = {
                "text": text,
                "model_id": "eleven_multilingual_v2",  # Updated to newer model
                "voice_settings": self.default_settings
            }
            
            logger.info(f"Generating audio for text: {text[:50]}...")
            
            # Make the API request
            response = requests.post(url, json=data, headers=headers)
            
            if response.status_code == 200:
                # Save the audio file
                output_file = Path(output_path)
                output_file.parent.mkdir(parents=True, exist_ok=True)
                
                with open(output_file, 'wb') as f:
                    f.write(response.content)
                
                logger.info(f"Audio generated successfully: {output_path}")
                return True
            else:
                logger.error(f"Failed to generate audio: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error generating audio: {e}")
            return False
    
    def generate_scene_audio(self, scene_narration: str, scene_id: int, output_dir: str) -> Optional[str]:
        """
        Generate audio for a specific scene.
        
        Args:
            scene_narration: The narration text for the scene
            scene_id: The scene ID
            output_dir: Directory to save the audio file
            
        Returns:
            Optional[str]: Path to the generated audio file, or None if failed
        """
        if not self.available:
            logger.warning("Audio generation not available for scene")
            return None
        
        output_path = os.path.join(output_dir, f"scene_{scene_id}_narration.mp3")
        
        if self.generate_audio(scene_narration, output_path):
            return output_path
        else:
            return None
    
    def generate_storyboard_audio(self, storyboard: 'Storyboard', output_dir: str) -> Dict[int, str]:
        """
        Generate audio for all scenes in a storyboard.
        
        Args:
            storyboard: The storyboard containing scenes
            output_dir: Directory to save audio files
            
        Returns:
            Dict[int, str]: Mapping of scene ID to audio file path
        """
        if not self.available:
            logger.warning("Audio generation not available for storyboard")
            return {}
        
        audio_files = {}
        
        for scene in storyboard.scenes:
            audio_path = self.generate_scene_audio(
                scene.narration, 
                scene.id, 
                output_dir
            )
            if audio_path:
                audio_files[scene.id] = audio_path
        
        logger.info(f"Generated audio for {len(audio_files)} scenes")
        return audio_files
    
    def get_available_voices(self) -> list:
        """
        Get list of available voices from ElevenLabs.
        
        Returns:
            list: List of available voice information
        """
        if not self.available:
            logger.warning("Cannot get voices - no API key provided")
            return []
        
        try:
            url = f"{self.base_url}/voices"
            headers = {"xi-api-key": self.api_key}
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                voices = response.json().get('voices', [])
                logger.info(f"Found {len(voices)} available voices")
                return voices
            else:
                logger.error(f"Failed to get voices: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error getting voices: {e}")
            return []
    
    def test_connection(self) -> bool:
        """
        Test the connection to ElevenLabs API.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        if not self.available:
            logger.warning("Cannot test connection - no API key provided")
            return False
        
        try:
            voices = self.get_available_voices()
            return len(voices) > 0
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False 