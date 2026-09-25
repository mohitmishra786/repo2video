"""
Core Data Structures

This module defines the basic data structures used throughout the advanced animation system.
"""

import logging
from dataclasses import dataclass, asdict
from typing import Dict, List, Any, Optional
from pathlib import Path
import json

logger = logging.getLogger(__name__)

@dataclass
class VisualElement:
    """Represents a visual element in the storyboard."""
    type: str
    properties: Dict[str, Any]
    position: Dict[str, float]
    color: str = "#1f77b4"
    size: float = 1.0

@dataclass
class AnimationStep:
    """Represents a single animation step."""
    action: str
    target: str
    duration: float
    easing: str = "ease_in_out"
    parameters: Dict[str, Any] = None

@dataclass
class CameraMovement:
    """Represents camera movement configuration."""
    phi: float = 75.0
    theta: float = -45.0
    zoom: float = 1.2
    duration: float = 2.0

@dataclass
class StoryboardScene:
    """Represents a single scene in the storyboard."""
    id: int
    concept: str
    visual_elements: List[VisualElement]
    animation_sequence: List[AnimationStep]
    narration: str
    duration: float
    camera_movement: CameraMovement
    code_snippet: Optional[str] = None
    execution_state: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class Storyboard:
    """Complete storyboard for a code repository."""
    title: str
    description: str
    scenes: List[StoryboardScene]
    total_duration: float
    metadata: Dict[str, Any]

@dataclass
class ExecutionState:
    """Represents the state of code execution at a point in time."""
    timestamp: float
    line_number: int
    variables: Dict[str, Any]
    call_stack: List[str]
    stdout: str
    stderr: str
    memory_usage: Optional[float] = None
    cpu_usage: Optional[float] = None

@dataclass
class ExecutionTrace:
    """Complete execution trace of a program."""
    code_content: str
    language: str
    states: List[ExecutionState]
    total_duration: float
    metadata: Dict[str, Any]

class DataStructureManager:
    """Manager for data structure operations."""
    
    @staticmethod
    def save_storyboard(storyboard: Storyboard, output_path: str) -> str:
        """Save storyboard to JSON file."""
        try:
            # Convert dataclasses to dictionaries
            storyboard_dict = asdict(storyboard)
            
            with open(output_path, 'w') as f:
                json.dump(storyboard_dict, f, indent=2)
            
            logger.info(f"Storyboard saved to {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error saving storyboard: {e}")
            raise
    
    @staticmethod
    def load_storyboard(file_path: str) -> Storyboard:
        """Load storyboard from JSON file."""
        try:
            with open(file_path, 'r') as f:
                storyboard_data = json.load(f)
            
            # Reconstruct dataclass objects
            scenes = []
            for scene_data in storyboard_data['scenes']:
                visual_elements = [VisualElement(**elem) for elem in scene_data['visual_elements']]
                animation_sequence = [AnimationStep(**anim) for anim in scene_data['animation_sequence']]
                camera_movement = CameraMovement(**scene_data['camera_movement'])
                
                scene = StoryboardScene(
                    id=scene_data['id'],
                    concept=scene_data['concept'],
                    visual_elements=visual_elements,
                    animation_sequence=animation_sequence,
                    narration=scene_data['narration'],
                    duration=scene_data['duration'],
                    camera_movement=camera_movement,
                    code_snippet=scene_data.get('code_snippet'),
                    execution_state=scene_data.get('execution_state'),
                    metadata=scene_data.get('metadata')
                )
                scenes.append(scene)
            
            return Storyboard(
                title=storyboard_data['title'],
                description=storyboard_data['description'],
                scenes=scenes,
                total_duration=storyboard_data['total_duration'],
                metadata=storyboard_data['metadata']
            )
            
        except Exception as e:
            logger.error(f"Error loading storyboard: {e}")
            raise 