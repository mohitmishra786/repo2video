"""
Video Merger Module for Advanced Animation System

This module handles merging multiple scene videos into a single comprehensive video.
"""

import logging
from pathlib import Path
from typing import List, Optional
import subprocess
import json

logger = logging.getLogger(__name__)

try:
    from moviepy.video.io.VideoFileClip import VideoFileClip
    from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
    from moviepy.video.VideoClip import TextClip, ColorClip
    from moviepy.audio.io.AudioFileClip import AudioFileClip
    from moviepy import concatenate_videoclips
    MOVIEPY_AVAILABLE = True
except ImportError:
    MOVIEPY_AVAILABLE = False
    logger.warning("MoviePy not available for video merging")

class VideoMerger:
    """Merges multiple scene videos into a single comprehensive video."""
    
    def __init__(self, output_dir: str = "final_video"):
        """
        Initialize the video merger.
        
        Args:
            output_dir: Directory for final video output
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        logger.info(f"VideoMerger initialized with output directory: {output_dir}")
    
    def merge_scenes(self, video_files: List[str], storyboard_path: Optional[str] = None, mobile_optimized: bool = False) -> str:
        """
        Merge multiple scene videos into a single comprehensive video with audio.
        
        Args:
            video_files: List of paths to scene video files
            storyboard_path: Optional path to storyboard JSON for metadata
            mobile_optimized: Whether to optimize for mobile devices
            
        Returns:
            Path to the merged video file
        """
        try:
            if not MOVIEPY_AVAILABLE:
                logger.error("MoviePy not available for video merging")
                return self.create_fallback_merge_with_audio(video_files, mobile_optimized)
            
            logger.info(f"Merging {len(video_files)} scene videos with audio")
            
            # Load storyboard metadata if available
            metadata = self.load_storyboard_metadata(storyboard_path) if storyboard_path else {}
            
            # Create video clips with audio
            clips = []
            audio_files = []
            
            for i, video_file in enumerate(video_files):
                if Path(video_file).exists():
                    # Load video clip
                    clip = VideoFileClip(video_file)
                    
                    # Look for corresponding audio file
                    video_path = Path(video_file)
                    # Audio files are in the main output directory, not in the video subdirectories
                    audio_file = self.output_dir / f"scene_{i+1}_narration.mp3"
                    
                    if audio_file.exists():
                        logger.info(f"Found audio file for scene {i+1}: {audio_file}")
                        # Load audio and set it to the video clip
                        audio_clip = AudioFileClip(str(audio_file))
                        clip = clip.set_audio(audio_clip)
                    else:
                        logger.warning(f"No audio file found for scene {i+1}: {audio_file}")
                    
                    clips.append(clip)
                    logger.info(f"Added scene {i+1}: {video_file}")
                else:
                    logger.warning(f"Video file not found: {video_file}")
            
            if not clips:
                logger.error("No valid video clips found")
                return self.create_fallback_merge_with_audio(video_files, mobile_optimized)
            
            # Add scene transitions
            clips = self.create_scene_transitions(clips)
            
            # Concatenate clips
            final_video = concatenate_videoclips(clips, method="compose")
            
            # Add title and metadata
            final_video = self.add_title_and_metadata(final_video, metadata)
            
            # Save the merged video
            output_path = self.output_dir / ("final_comprehensive_analysis_mobile.mp4" if mobile_optimized else "final_comprehensive_analysis.mp4")
            
            # Use mobile-optimized settings if requested
            if mobile_optimized:
                final_video.write_videofile(
                    str(output_path),
                    fps=30,
                    codec='libx264',
                    audio_codec='aac',
                    bitrate='2000k',
                    threads=4,
                    preset='fast',
                    ffmpeg_params=['-profile:v', 'main', '-level', '3.1', '-pix_fmt', 'yuv420p']
                )
            else:
                final_video.write_videofile(
                    str(output_path),
                    fps=24,
                    codec='libx264',
                    audio_codec='aac'
                )
            
            # Clean up
            for clip in clips:
                clip.close()
            final_video.close()
            
            logger.info(f"Successfully merged videos with audio to: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Error merging videos: {e}")
            return self.create_fallback_merge_with_audio(video_files, mobile_optimized)
    
    def load_storyboard_metadata(self, storyboard_path: str) -> dict:
        """Load metadata from storyboard JSON file."""
        try:
            with open(storyboard_path, 'r') as f:
                storyboard = json.load(f)
            
            return {
                'title': storyboard.get('title', 'Code Repository Analysis'),
                'description': storyboard.get('description', ''),
                'total_duration': storyboard.get('total_duration', 0),
                'scene_count': len(storyboard.get('scenes', []))
            }
        except Exception as e:
            logger.error(f"Error loading storyboard metadata: {e}")
            return {}
    
    def add_title_and_metadata(self, video_clip, metadata: dict):
        """Add title and metadata overlay to the video."""
        try:
            # Create title text
            title = metadata.get('title', 'Code Repository Analysis')
            title_clip = TextClip(
                title,
                fontsize=48,
                color='white',
                font='Arial-Bold'
            ).set_position(('center', 50)).set_duration(3)
            
            # Create subtitle with metadata
            subtitle_text = f"Duration: {metadata.get('total_duration', 0):.1f}s | Scenes: {metadata.get('scene_count', 0)}"
            subtitle_clip = TextClip(
                subtitle_text,
                fontsize=24,
                color='gray',
                font='Arial'
            ).set_position(('center', 100)).set_duration(3)
            
            # Composite the video
            final_clip = CompositeVideoClip([video_clip, title_clip, subtitle_clip])
            
            return final_clip
            
        except Exception as e:
            logger.error(f"Error adding title and metadata: {e}")
            return video_clip
    
    def create_fallback_merge(self, video_files: List[str]) -> str:
        """Create a fallback merged video using ffmpeg."""
        try:
            # Create a file list for ffmpeg
            file_list_path = self.output_dir / "video_list.txt"
            with open(file_list_path, 'w') as f:
                for video_file in video_files:
                    video_path = Path(video_file)
                    if video_path.exists():
                        # Use absolute path to avoid path issues
                        f.write(f"file '{video_path.absolute()}'\n")
                    else:
                        logger.warning(f"Video file not found: {video_file}")
            
            # Use ffmpeg to concatenate
            output_path = self.output_dir / "final_comprehensive_analysis.mp4"
            
            cmd = [
                'ffmpeg',
                '-f', 'concat',
                '-safe', '0',
                '-i', str(file_list_path),
                '-c', 'copy',
                str(output_path),
                '-y'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"Fallback merge successful: {output_path}")
                return str(output_path)
            else:
                logger.error(f"Fallback merge failed: {result.stderr}")
                return ""
                
        except Exception as e:
            logger.error(f"Error in fallback merge: {e}")
            return ""

    def create_fallback_merge_with_audio(self, video_files: List[str], mobile_optimized: bool = False) -> str:
        """Create a fallback merged video with audio using ffmpeg."""
        try:
            # Create a file list for ffmpeg
            file_list_path = self.output_dir / "video_list.txt"
            audio_list_path = self.output_dir / "audio_list.txt"
            
            with open(file_list_path, 'w') as f:
                for video_file in video_files:
                    video_path = Path(video_file)
                    if video_path.exists():
                        # Use absolute path to avoid path issues
                        f.write(f"file '{video_path.absolute()}'\n")
                    else:
                        logger.warning(f"Video file not found: {video_file}")
            
            # Create audio list
            with open(audio_list_path, 'w') as f:
                for i, video_file in enumerate(video_files):
                    # Audio files are in the main output directory
                    audio_file = self.output_dir / f"scene_{i+1}_narration.mp3"
                    if audio_file.exists():
                        f.write(f"file '{audio_file.absolute()}'\n")
                        logger.info(f"Found audio file for scene {i+1}: {audio_file}")
                    else:
                        logger.warning(f"No audio file found for scene {i+1}: {audio_file}")
            
            # Use ffmpeg to concatenate videos and audio separately, then combine
            temp_video_path = self.output_dir / "temp_video.mp4"
            temp_audio_path = self.output_dir / "temp_audio.mp3"
            output_path = self.output_dir / ("final_comprehensive_analysis_mobile.mp4" if mobile_optimized else "final_comprehensive_analysis.mp4")
            
            # First concatenate videos
            video_cmd = [
                'ffmpeg',
                '-f', 'concat',
                '-safe', '0',
                '-i', str(file_list_path),
                '-c', 'copy',
                str(temp_video_path),
                '-y'
            ]
            
            result = subprocess.run(video_cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"Video concatenation failed: {result.stderr}")
                return self.create_fallback_merge(video_files)  # Fall back to video-only
            
            # Then concatenate audio files
            audio_cmd = [
                'ffmpeg',
                '-f', 'concat',
                '-safe', '0',
                '-i', str(audio_list_path),
                '-c', 'copy',
                str(temp_audio_path),
                '-y'
            ]
            
            result = subprocess.run(audio_cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"Audio concatenation failed: {result.stderr}")
                # If audio fails, just use the video
                temp_video_path.rename(output_path)
                return str(output_path)
            
            # Finally combine video and audio with mobile optimization if requested
            combine_cmd = [
                'ffmpeg',
                '-i', str(temp_video_path),
                '-i', str(temp_audio_path),
                '-c:v', 'libx264',
                '-c:a', 'aac',
                '-shortest'
            ]
            
            if mobile_optimized:
                combine_cmd.extend([
                    '-profile:v', 'main',
                    '-level', '3.1',
                    '-pix_fmt', 'yuv420p',
                    '-b:v', '2000k',
                    '-maxrate', '2000k',
                    '-bufsize', '4000k',
                    '-preset', 'fast',
                    '-g', '30',
                    '-r', '30'
                ])
            else:
                combine_cmd.extend(['-c:v', 'copy'])
            
            combine_cmd.extend([str(output_path), '-y'])
            
            result = subprocess.run(combine_cmd, capture_output=True, text=True)
            
            # Clean up temp files
            if temp_video_path.exists():
                temp_video_path.unlink()
            if temp_audio_path.exists():
                temp_audio_path.unlink()
            
            if result.returncode == 0:
                logger.info(f"Fallback merge with audio successful: {output_path}")
                return str(output_path)
            else:
                logger.error(f"Audio-video combination failed: {result.stderr}")
                # If combination fails, just use the video
                if temp_video_path.exists():
                    temp_video_path.rename(output_path)
                    return str(output_path)
                return ""
            
        except Exception as e:
            logger.error(f"Error in fallback merge with audio: {e}")
            return self.create_fallback_merge(video_files)  # Fall back to video-only
            
            # Then concatenate audio files
            audio_cmd = [
                'ffmpeg',
                '-f', 'concat',
                '-safe', '0',
                '-i', str(audio_list_path),
                '-c', 'copy',
                str(temp_audio_path),
                '-y'
            ]
            
            result = subprocess.run(audio_cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"Audio concatenation failed: {result.stderr}")
                # If audio fails, just use the video
                temp_video_path.rename(output_path)
                return str(output_path)
            
            # Finally combine video and audio
            combine_cmd = [
                'ffmpeg',
                '-i', str(temp_video_path),
                '-i', str(temp_audio_path),
                '-c:v', 'copy',
                '-c:a', 'aac',
                '-shortest',
                str(output_path),
                '-y'
            ]
            
            result = subprocess.run(combine_cmd, capture_output=True, text=True)
            
            # Clean up temp files
            if temp_video_path.exists():
                temp_video_path.unlink()
            if temp_audio_path.exists():
                temp_audio_path.unlink()
            
            if result.returncode == 0:
                logger.info(f"Fallback merge with audio successful: {output_path}")
                return str(output_path)
            else:
                logger.error(f"Audio-video combination failed: {result.stderr}")
                # If combination fails, just use the video
                if temp_video_path.exists():
                    temp_video_path.rename(output_path)
                    return str(output_path)
                return ""
                
        except Exception as e:
            logger.error(f"Error in fallback merge with audio: {e}")
            return self.create_fallback_merge(video_files)  # Fall back to video-only
    
    def create_scene_transitions(self, clips: List) -> List:
        """Add smooth transitions between scenes."""
        try:
            transitioned_clips = []
            
            for i, clip in enumerate(clips):
                # Add fade in/out effects
                if i == 0:  # First clip
                    clip = clip.fadein(0.5)
                if i == len(clips) - 1:  # Last clip
                    clip = clip.fadeout(0.5)
                else:  # Middle clips
                    clip = clip.fadein(0.3).fadeout(0.3)
                
                transitioned_clips.append(clip)
            
            return transitioned_clips
            
        except Exception as e:
            logger.exception(f"Error creating transitions: {e}")
            return clips 