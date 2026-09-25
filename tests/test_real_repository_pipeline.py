"""Pytest conversion of the ad-hoc ``test_real_repository.py`` pipeline script.

The original script remains available as a manual end-to-end CLI; these tests
exercise the same functions with all network/CD-bound pieces mocked so the
suite never requires live GitHub access or video rendering.
"""

import os
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import test_real_repository as trr


class TestFetchRepository:
    def test_success_returns_temp_dir(self, tmp_path):
        def fake_run(cmd, **kwargs):
            clone_target = Path(cmd[3])
            clone_target.mkdir(parents=True, exist_ok=True)
            (clone_target / "main.py").write_text("x = 1\n")
            return MagicMock(returncode=0)

        with patch.object(trr.subprocess, "run", side_effect=fake_run):
            path = trr.fetch_repository("https://github.com/user/repo")
        assert (Path(path) / "main.py").exists()

    def test_failure_raises_value_error(self):
        with patch.object(
            trr.subprocess, "run",
            side_effect=subprocess.CalledProcessError(128, "git clone"),
        ):
            with pytest.raises(ValueError, match="Failed to clone"):
                trr.fetch_repository("https://github.com/user/repo")


class TestAnalyzeRepository:
    def test_wrapper_returns_analysis(self, tmp_path):
        (tmp_path / "sample.py").write_text("def hi():\n    return 1\n")
        analysis = trr.analyze_repository(str(tmp_path))
        assert "files" in analysis
        assert any(str(p).endswith("sample.py") for p in analysis["files"])


class TestAnalyzeGithubRepo:
    def test_non_github_url_returns_false(self, capsys):
        # analyze_github_repo itself clones; a non-GitHub URL fails at
        # git clone and is reported as a processing error.
        assert trr.analyze_github_repo("https://gitlab.com/user/repo") is False
        assert "Error" in capsys.readouterr().out

    def test_happy_path_with_mocks(self, tmp_path, monkeypatch, capsys):
        monkeypatch.setattr(
            trr, "fetch_repository", lambda url: str(tmp_path / "cloned"), raising=False
        )
        (tmp_path / "cloned").mkdir()
        (tmp_path / "cloned" / "main.py").write_text("def hi():\n    return 1\n")

        analysis = trr.analyze_repository(str(tmp_path / "cloned"))
        monkeypatch.setattr(trr, "analyze_repository", lambda path: analysis, raising=False)

        fake_system = MagicMock()
        fake_system.storyboard_generator.generate_storyboard.return_value.scenes = []
        fake_system.create_animation_from_code.return_value = str(tmp_path / "out.mp4")
        monkeypatch.setattr(trr, "AdvancedAnimationSystem", MagicMock(return_value=fake_system))

        ok = trr.analyze_github_repo("https://github.com/user/repo", str(tmp_path / "out"))
        assert ok is True
        fake_system.create_animation_from_code.assert_called_once()


class TestMainCLI:
    def test_dry_run_validates_without_rendering(self, monkeypatch, capsys):
        monkeypatch.setattr(
            "sys.argv",
            ["test_real_repository.py", "https://github.com/user/repo", "--dry-run"],
        )
        trr.main()
        out = capsys.readouterr().out
        assert "Dry run complete" in out

    def test_dry_run_rejects_invalid_url(self, monkeypatch, capsys):
        monkeypatch.setattr(
            "sys.argv",
            ["test_real_repository.py", "https://gitlab.com/user/repo", "--dry-run"],
        )
        trr.main()
        out = capsys.readouterr().out
        assert "valid GitHub repository URL" in out
