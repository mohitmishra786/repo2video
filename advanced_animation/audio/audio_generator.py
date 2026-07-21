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
from googletrans import Translator

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# Optional imports for advanced audio features
try:
    import pysrt
    import pydub
    from pydub import AudioSegment
    from pydub.generators import WhiteNoise
    ADVANCED_AUDIO_AVAILABLE = True
except ImportError:
    ADVANCED_AUDIO_AVAILABLE = False

# gTTS fallback for offline text-to-speech
try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False

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
            if GTTS_AVAILABLE:
                logger.warning("ElevenLabs API key not provided. Using gTTS as fallback.")
                self.available = True
                self._use_elevenlabs = False
            else:
                logger.warning("ElevenLabs API key not provided and gTTS not available. Audio generation will be disabled.")
                self.available = False
                self._use_elevenlabs = False
        else:
            self.available = True
            self._use_elevenlabs = True
            logger.info("ElevenLabs audio generator initialized successfully")
        
        # Default voice settings
        self.default_voice_id = "21m00Tcm4TlvDq8ikWAM"  # Rachel voice
        self.default_settings = {
            "stability": 0.5,
            "similarity_boost": 0.75,
            "style": 0.0,
            "use_speaker_boost": True
        }
        
        # Initialize translator for multi-language support
        self.translator = Translator()
        self.supported_languages = {
            'en': 'English',
            'es': 'Spanish', 
            'fr': 'French',
            'de': 'German',
            'it': 'Italian',
            'pt': 'Portuguese',
            'ru': 'Russian',
            'zh': 'Chinese',
            'ja': 'Japanese',
            'ar': 'Arabic'
        }
        
        # Multi-voice support - will be populated dynamically
        self.voice_options = {}
        
        # Background music settings
        self.background_music_enabled = False
        self.background_music_volume = -20  # dB
    
    def _translate_text(self, text: str, target_language: str) -> str:
        """
        Translate text to the target language.
        
        Args:
            text: Text to translate
            target_language: Target language code
            
        Returns:
            Translated text
        """
        if target_language == 'en':
            return text  # No translation needed for English
        
        try:
            translation = self.translator.translate(text, dest=target_language)
            logger.info(f"Translated text from English to {target_language}")
            return translation.text
        except Exception as e:
            logger.error(f"Translation failed, using original text: {e}")
            return text
    
    def generate_audio(self, text: str, output_path: str, voice_id: Optional[str] = None, language: str = 'en', 
                      voice_type: str = 'female', add_background_music: bool = False) -> bool:
        """
        Generate audio from text using ElevenLabs API or gTTS as fallback.

        Args:
            text: Text to convert to speech
            output_path: Path where the audio file should be saved
            voice_id: Voice ID to use. If not provided, uses default voice.
            language: Language code for the text (e.g., 'en', 'es', 'fr')
            voice_type: Type of voice (male, female, child, elderly, robot)
            add_background_music: Whether to add background music

        Returns:
            bool: True if successful, False otherwise
        """
        if not self.available:
            logger.error("Audio generation not available")
            return False

        if not text.strip():
            logger.warning("Empty text provided for audio generation")
            return False

        try:
            if self._use_elevenlabs:
                return self._generate_elevenlabs_audio(text, output_path, voice_id, language, voice_type, add_background_music)
            elif GTTS_AVAILABLE:
                return self._generate_gtts_audio(text, output_path, language, add_background_music)
            else:
                logger.error("No TTS engine available")
                return False
        except Exception as e:
            logger.error(f"Error generating audio: {e}")
            return False

    def _generate_elevenlabs_audio(self, text: str, output_path: str, voice_id: Optional[str] = None,
                                    language: str = 'en', voice_type: str = 'female',
                                    add_background_music: bool = False) -> bool:
        """Generate audio using ElevenLabs API."""
        # Translate text if needed
        translated_text = self._translate_text(text, language)

        # Use voice type if specified
        if voice_type in self.voice_options:
            voice_id = self.voice_options[voice_type]
        elif not voice_id:
            voice_id = self.default_voice_id

        # Prepare the request
        url = f"{self.base_url}/text-to-speech/{voice_id}"

        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.api_key
        }

        data = {
            "text": translated_text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": self.default_settings
        }

        logger.info(f"Generating ElevenLabs audio: {translated_text[:50]}... (Language: {language}, Voice: {voice_type})")

        response = requests.post(url, json=data, headers=headers)

        if response.status_code == 200:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)

            with open(output_file, 'wb') as f:
                f.write(response.content)

            logger.info(f"ElevenLabs audio generated: {output_path}")

            if add_background_music and ADVANCED_AUDIO_AVAILABLE:
                self._add_background_music(output_path)

            return True
        else:
            logger.error(f"ElevenLabs API error: {response.status_code} - {response.text}")
            return False

    def _generate_gtts_audio(self, text: str, output_path: str, language: str = 'en',
                              add_background_music: bool = False) -> bool:
        """Generate audio using gTTS (Google Text-to-Speech) as fallback."""
        if not GTTS_AVAILABLE:
            return False

        logger.info(f"Generating gTTS audio: {text[:50]}... (Language: {language})")

        try:
            tts = gTTS(text=text, lang=language, slow=False)
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            tts.save(str(output_file))

            logger.info(f"gTTS audio generated: {output_path}")

            if add_background_music and ADVANCED_AUDIO_AVAILABLE:
                self._add_background_music(output_path)

            return True
        except Exception as e:
            logger.error(f"gTTS generation failed: {e}")
            return False
    
    def generate_scene_audio(self, scene_narration: str, scene_id: int, output_dir: str, language: str = 'en') -> Optional[str]:
        """
        Generate audio for a specific scene.
        
        Args:
            scene_narration: The narration text for the scene
            scene_id: The scene ID
            output_dir: Directory to save the audio file
            language: Language code for the narration
            
        Returns:
            Optional[str]: Path to the generated audio file, or None if failed
        """
        if not self.available:
            logger.warning("Audio generation not available for scene")
            return None
        
        output_path = os.path.join(output_dir, f"scene_{scene_id}_narration_{language}.mp3")
        
        if self.generate_audio(scene_narration, output_path, language=language):
            return output_path
        else:
            return None
    
    def generate_storyboard_audio(self, storyboard: 'Storyboard', output_dir: str, language: str = 'en') -> Dict[int, str]:
        """
        Generate audio for all scenes in a storyboard.
        
        Args:
            storyboard: The storyboard containing scenes
            output_dir: Directory to save audio files
            language: Language code for all narrations
            
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
                output_dir,
                language
            )
            if audio_path:
                audio_files[scene.id] = audio_path
        
        logger.info(f"Generated audio for {len(audio_files)} scenes in {language}")
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
    
    def get_supported_languages(self) -> Dict[str, str]:
        """
        Get supported languages for translation and audio generation.
        
        Returns:
            Dict[str, str]: Mapping of language codes to language names
        """
        return self.supported_languages
    
    def _add_background_music(self, audio_path: str):
        """
        Add background music to audio file.
        
        Args:
            audio_path: Path to the audio file
        """
        if not ADVANCED_AUDIO_AVAILABLE:
            logger.warning("pydub not available for background music")
            return
        
        try:
            # Load the narration audio
            narration = AudioSegment.from_mp3(audio_path)
            
            # Generate or load background music
            # For demo purposes, we'll generate a simple ambient sound
            # In production, you would use royalty-free music tracks
            duration = len(narration)
            background = WhiteNoise().to_audio_segment(duration=duration)
            
            # Apply low pass filter to make it less intrusive
            background = background.low_pass_filter(1000)
            
            # Reduce volume
            background = background + self.background_music_volume
            
            # Mix narration and background
            mixed = narration.overlay(background)
            
            # Save the result
            mixed.export(audio_path, format="mp3")
            logger.info(f"Added background music to: {audio_path}")
            
        except Exception:
            logger.exception("Error adding background music")
    
    def generate_subtitles(self, text: str, output_path: str) -> bool:
        """
        Generate subtitle file for the given text.
        
        Args:
            text: Text to generate subtitles for
            output_path: Path to save the subtitle file
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not ADVANCED_AUDIO_AVAILABLE:
            logger.warning("pysrt not available for subtitle generation")
            return False
        
        try:
            # Create a simple subtitle file
            # In a real implementation, this would be more sophisticated
            # with proper timing based on speech analysis
            
            subs = pysrt.SubRipFile()
            
            # Split text into sentences for subtitles
            sentences = text.split('.')
            
            for i, sentence in enumerate(sentences):
                if sentence.strip():
                    # Add subtitle with timing (simplified)
                    start_time = i * 3000  # 3 seconds per subtitle
                    end_time = start_time + 3000
                    
                    sub = pysrt.SubRipItem(
                        index=i+1,
                        start=pysrt.SubRipTime(milliseconds=start_time),
                        end=pysrt.SubRipTime(milliseconds=end_time),
                        text=sentence.strip() + '.'
                    )
                    subs.append(sub)
            
            # Save the subtitle file
            subs.save(output_path, encoding='utf-8')
            logger.info(f"Generated subtitles: {output_path}")
            return True
            
        except (IOError, OSError, ValueError) as e:
            logger.error(f"Error generating subtitles: {e}")
            return False
        except Exception:
            logger.exception("Unexpected error generating subtitles")
            return False
    
    def generate_scene_audio_with_subtitles(self, scene_narration: str, scene_id: int, output_dir: str, 
                                          language: str = 'en', voice_type: str = 'female') -> Dict[str, str]:
        """
        Generate audio and subtitles for a scene.
        
        Args:
            scene_narration: The narration text for the scene
            scene_id: The scene ID
            output_dir: Directory to save the audio and subtitle files
            language: Language code for the narration
            voice_type: Type of voice to use
            
        Returns:
            Dict[str, str]: Dictionary with 'audio_path' and 'subtitle_path'
        """
        if not self.available:
            logger.warning("Audio generation not available for scene")
            return {'audio_path': '', 'subtitle_path': ''}
        
        # Generate audio
        audio_path = os.path.join(output_dir, f"scene_{scene_id}_narration_{language}.mp3")
        audio_success = self.generate_audio(
            scene_narration, 
            audio_path,
            voice_type=voice_type,
            language=language
        )
        
        # Generate subtitles
        subtitle_path = os.path.join(output_dir, f"scene_{scene_id}_subtitles_{language}.srt")
        subtitle_success = self.generate_subtitles(scene_narration, subtitle_path)
        
        result = {
            'audio_path': audio_path if audio_success else '',
            'subtitle_path': subtitle_path if subtitle_success else ''
        }
        
        logger.info(f"Generated audio and subtitles for scene {scene_id}")
        return result
    
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