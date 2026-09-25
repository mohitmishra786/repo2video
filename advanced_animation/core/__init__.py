"""
Core module for advanced animation system.

Contains data structures, storyboard generation, and execution capture.
"""

from .data_structures import (
    Storyboard, StoryboardScene, VisualElement, 
    AnimationStep, CameraMovement, ExecutionState, ExecutionTrace,
    DataStructureManager
)
from .storyboard_generator import StoryboardGenerator
from .execution_capture import RuntimeStateCapture

__all__ = [
    'Storyboard', 'StoryboardScene', 'VisualElement', 
    'AnimationStep', 'CameraMovement', 'ExecutionState', 'ExecutionTrace',
    'DataStructureManager', 'StoryboardGenerator', 'RuntimeStateCapture'
] 