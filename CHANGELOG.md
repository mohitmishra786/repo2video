# Changelog

## [0.1.0] — 2026-07-21

### Added
- MoviePy-based video rendering pipeline with color-coded scene types
- gTTS fallback for offline text-to-speech (works without ElevenLabs API key)
- Streamlit web UI (`app.py`) with URL input, progress display, and download button
- Content sanitization for email and API key redaction
- Repository size limits (configurable, default 100MB)
- HTTP request timeout guards (30s default)
- Security policy (`SECURITY.md`)
- CI/CD pipeline with pytest, ruff linting, and import smoke tests
- Issue templates for bug reports and feature requests
- Version tracking (`VERSION` file)

### Changed
- Standardized project name to `repo2video` across all files
- Updated MoviePy imports to v2 API (flat imports, `.with_position()`, etc.)
- Rewrote README with accurate clone URLs, badges, and security note

### Fixed
- Removed over-broad content sanitization patterns (URL, CC, phone, hash redaction)
- Removed duplicate `generate_scene_code()` method in `manim_scene.py`
- Removed unreachable duplicate code after return in `video_merger.py`

### Removed
- ManimGL and Manim CE as hard dependencies (replaced by MoviePy)
- E2B code interpreter dependency (aspirational, not implemented)
- Unused dependencies: OpenCV, scikit-learn, SciPy, plotly, kaleido, pandas, pyarrow
- Credit card number detection in content sanitizer (PCI scope risk)
