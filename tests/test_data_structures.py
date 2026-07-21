"""Unit tests for data_structures module."""

import json
import tempfile
from pathlib import Path
import pytest
from advanced_animation.core.data_structures import (
    Storyboard,
    StoryboardScene,
    VisualElement,
    AnimationStep,
    CameraMovement,
    DataStructureManager,
)


@pytest.fixture
def sample_storyboard():
    scenes = [
        StoryboardScene(
            id=1,
            concept="Introduction",
            visual_elements=[
                VisualElement(
                    type="text",
                    properties={"text": "Hello"},
                    position={"x": 0.0, "y": 0.0, "z": 0.0},
                )
            ],
            animation_sequence=[
                AnimationStep(action="fade_in", target="text", duration=1.0)
            ],
            narration="Welcome to the code walkthrough.",
            duration=5.0,
            camera_movement=CameraMovement(),
        )
    ]
    return Storyboard(
        title="Test Repo",
        description="A test storyboard",
        scenes=scenes,
        total_duration=5.0,
        metadata={"language": "python"},
    )


class TestStoryboardSerialization:
    def test_roundtrip(self, sample_storyboard):
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name

        try:
            DataStructureManager.save_storyboard(sample_storyboard, path)
            loaded = DataStructureManager.load_storyboard(path)

            assert loaded.title == "Test Repo"
            assert loaded.description == "A test storyboard"
            assert len(loaded.scenes) == 1
            assert loaded.scenes[0].id == 1
            assert loaded.scenes[0].concept == "Introduction"
            assert loaded.scenes[0].narration == "Welcome to the code walkthrough."
            assert loaded.scenes[0].duration == 5.0
        finally:
            Path(path).unlink(missing_ok=True)

    def test_save_creates_valid_json(self, sample_storyboard):
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name

        try:
            DataStructureManager.save_storyboard(sample_storyboard, path)
            with open(path) as f:
                data = json.load(f)

            assert data["title"] == "Test Repo"
            assert len(data["scenes"]) == 1
        finally:
            Path(path).unlink(missing_ok=True)


class TestStoryboardScene:
    def test_scene_with_code_snippet(self):
        scene = StoryboardScene(
            id=2,
            concept="Code Analysis",
            visual_elements=[],
            animation_sequence=[],
            narration="Here is the code.",
            duration=10.0,
            camera_movement=CameraMovement(),
            code_snippet="def hello():\n    print('world')",
        )
        assert scene.code_snippet == "def hello():\n    print('world')"

    def test_scene_without_code_snippet(self):
        scene = StoryboardScene(
            id=3,
            concept="Conclusion",
            visual_elements=[],
            animation_sequence=[],
            narration="Thank you.",
            duration=3.0,
            camera_movement=CameraMovement(),
        )
        assert scene.code_snippet is None


class TestVisualElement:
    def test_default_values(self):
        elem = VisualElement(
            type="rectangle",
            properties={},
            position={"x": 0.0, "y": 0.0, "z": 0.0},
        )
        assert elem.color == "#1f77b4"
        assert elem.size == 1.0


class TestCameraMovement:
    def test_default_values(self):
        cam = CameraMovement()
        assert cam.phi == 75.0
        assert cam.theta == -45.0
        assert cam.zoom == 1.2
        assert cam.duration == 2.0
