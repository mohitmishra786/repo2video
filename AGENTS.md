# RepoToVideo — Agent Instructions

Convert GitHub repos into 3Blue1Brown-style animated videos. Pipeline:
`repo_fetcher → code_analysis → storyboard_generator → (manim_scene + audio_generator) → video_merger`

## Setup

```bash
pip install -r requirements.txt
python setup.py              # installs deps, creates config.env + logs/ output/ temp/ dirs
```

API keys go in `.env` (loaded via `python-dotenv`):
- `OPENAI_API_KEY` — storyboard generation (GPT-4)
- `ELEVENLABS_API_KEY` — TTS narration
- `E2B_API_KEY` — sandboxed code execution capture

## Key commands

```bash
# Main test/run — clones a repo, analyzes it, renders video
python test_real_repository.py https://github.com/user/repo
python test_real_repository.py https://github.com/user/repo --output my_videos --theme dark --quality 720p

# No `app.py` exists despite docs references. CLI is the only interface.
# No lint/typecheck config in the repo. No CI workflows.
```

## Architecture boundaries

| Directory / File | Role |
|---|---|
| `repo_fetcher.py` | Fetch repos from GitHub/GitLab/Bitbucket via PyGithub |
| `code_analysis.py` | AST + regex analysis; optional tree-sitter & FAISS vector search |
| `advanced_animation/core/` | `Storyboard` dataclasses, AI storyboard gen, E2B execution capture |
| `advanced_animation/rendering/` | ManimGL rendering (with ManimCE fallback), MoviePy video merge |
| `advanced_animation/audio/` | ElevenLabs TTS narration |
| `advanced_animation/visualizations/` | Visual metaphor library |

## Rendering gotchas

- **ManimGL** (`manimlib`) is primary; **ManimCE** (`manim`) is fallback. If neither imports, dummy `Scene` classes are used — code runs silently with no visible output.
- **MoviePy** is required for `video_merger.py`. Test: `python -c "from moviepy.editor import VideoClip"`
- ManimGL often requires system-level deps (ffmpeg, latex, etc.). On macOS: `brew install ffmpeg`.
- `code_analysis.py` uses `ThreadPoolExecutor` (up to 8 workers) and chunks large repos via `chunk_size` param.

## Logging

All logs write to `logs/` as per-run files via `advanced_animation.utils.logging_config`. Test output goes to `real_repo_output/` by default.

## Conventions

- `.never/config.yaml` enables agents (`agents: true`), disables cursor/claude/copilot
- `.gitignore` ignores `AGENTS.md`, `*.mp4`, `*.mp3`, `logs/`, `output/`, `.env`
- No formatter, linter, or typechecker config exists. Code style is inconsistent (e.g. some files have LLM-generated auto-docstrings on every method).
- Imports: stdlib → third-party → local. Prefer `from __future__ import annotations` for deferred eval.
