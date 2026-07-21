# Pre-Launch Checklist

## What Must Be True Before Any Public Announcement

This checklist assumes the goal is a public launch (Show HN, Reddit, etc.) that drives real adoption rather than embarrassment. Calibrated for a solo developer.

### 🔴 CRITICAL — Launch Blockers (Must Fix or Skip the Launch)

- [ ] **Make the rendering pipeline produce an actual video** — Even if it's basic (MoviePy-based typing animation + static code screens + gTTS narration), it must produce something watchable. Without this, the product is vaporware.
- [ ] **Create `app.py` or replace Streamlit with a working interface** — The user-facing interface must exist. Currently the project is CLI-only.
- [ ] **Fix placeholder README clone URLs** — `yourusername/RepoToVideo.git` must be `mohitmishra786/repo2video.git`. A 404 clone error on first visit will lose every visitor permanently.
- [ ] **Add repo description and topics on GitHub** — 5-minute fix; without it, GitHub search results show nothing useful.
- [ ] **Resolve name confusion** — Pick `repo2video` or `RepoToVideo` and use consistently across URL, README, code, and docs.
- [ ] **Remove/stub the broken ManimGL dependency** — A fresh install should not spend 15 minutes installing ManimGL and its system deps only to hit no-op stubs. Either make it work or remove it.
- [ ] **Verify `requirements.txt` installs cleanly** — Test on a clean machine/container. Currently it will attempt to install 154 packages including heavy GPU-adjacent deps.

### 🟡 HIGH — Launch Readiness (Should Fix Before Major Launch)

- [ ] **Add at least gTTS fallback for audio** — Without ElevenLabs key, the entire audio pipeline returns silence. gTTS is free and already in requirements.txt. This is ~2 hours of work.
- [ ] **Create a demo GIF/video** of the tool working. For a video-generation tool, this is the single most important README asset. Even a CLI demo with `asciinema` is better than nothing.
- [ ] **Test the full pipeline end-to-end** — Clone a real repo, run the full pipeline, verify the output exists. Identify and fix crashes.
- [ ] **Add basic error handling for the "no API key" case** — Currently the system fails silently with stub returns. User-facing error messages needed.
- [ ] **Add a LICENSE file** — Already present (MIT). Verify copyright holder name. Currently: `Copyright (c) 2025 chessMan`. Should this be the founder's name?
- [ ] **Remove dead code paths** — `E2B` execution capture, `pycallgraph2`, `pipdeptree`, `googletrans` translation. Either implement or remove.
- [ ] **Trim requirements.txt** — Remove unrelated heavy dependencies (OpenCV, scikit-learn, SciPy, plotly, kaleido, librosa-equivalent). Target ~40 packages.

### 🟢 MEDIUM — Polishing

- [ ] **Set up GitHub Pages landing page** with a one-pager: what it does, how to install, demo video, GitHub link. Free via GitHub Pages.
- [ ] **Add GitHub social preview image** — Set in repo settings. A compelling 1280×640 banner.
- [ ] **Add README badges** — Stars, license, Python version.
- [ ] **Write a "How It Works" section** with the pipeline diagram currently only in AGENTS.md.
- [ ] **Set up GitHub Sponsors** — Already partially configured (the founder has a GitHub Sponsors profile). Link it in the README.
- [ ] **Add a CHANGELOG.md** — Even if it just lists "Initial release."

### 🔵 LOW — Nice to Have Before Launch

- [ ] **Dockerfile** for easy testing.
- [ ] **GitHub Actions CI** with basic lint and import checks.
- [ ] **Verify memory usage** — Code analysis with ThreadPoolExecutor(8) on a large repo could OOM a standard machine.

## Post-Checklist: One-Week Sprint

If I were the solo developer, I'd do this in order over one focused week:

| Day | Focus | Deliverable |
|-----|-------|-------------|
| 1 | **Fix rendering** | Get MoviePy to produce a 30-second video with code frames + gTTS narration. Skip all the fancy Manim stuff. |
| 2 | **Create app.py** | Minimal Streamlit app: URL input → generate button → progress bar → download link. ~100 lines. |
| 3 | **Cleanup** | Fix README, add description/topics, trim requirements, remove dead code. |
| 4 | **Test + Demo** | Run end-to-end on 3 repos. Record demo GIF/video. |
| 5 | **Launch prep** | Write Show HN post, prepare Reddit posts, set up landing page. |
| 6 | **Buffer** | Fix anything that broke during testing. |
| 7 | **Launch** | Go live on Show HN. |

## Open Questions

1. **Is the current codebase worth salvaging, or should the rendering be rewritten from scratch?** Given the extent of the stubs, a MoviePy-based rewrite of the rendering layer might be faster than fixing the existing ManimGL code.
2. **What's the minimum viable output?** A 30-second narrated slideshow with code snippets and fade transitions? Or do we need actual code typing animation?
3. **Are there any working videos from earlier versions?** The commit "video update" (5692f1f) suggests there might have been a working state at some point. Check git history.
