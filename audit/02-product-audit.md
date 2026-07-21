# Product & Core Functionality Audit

## 1. CURRENT STATE

### Value Proposition
"RepoToVideo is a powerful tool designed to help developers convert GitHub repositories into animated videos." — README, line 3.

The implied value is: paste a GitHub URL, get an animated explainer video. This is a valid, needed product category — competitors RepoClip ($24-166/mo), RepoToViralVideo (40 stars, launched Feb 2026), repo-explainer (3 stars, Jan 2026), and Phantom (7 stars, Apr 2026) all launch in this space in 2026.

### What Actually Works (verified by code inspection)
1. **Repository Fetching** — `repo_fetcher.py` can clone repos via GitPython or PyGithub API. Works for GitHub; GitLab/Bitbucket support is aspirational (requires API keys).
2. **Code Analysis** — `code_analysis.py` has a working AST-based Python analyzer. JS and Java analyzers are regex-based and fragile. Multi-language support is variable-quality.
3. **Data Structures** — `core/data_structures.py` has clean, working dataclasses with JSON serialization.
4. **Logging** — `utils/logging_config.py` has a solid rotating-file logging system.
5. **Rule-based Storyboard Generation** — The fallback `_generate_fallback_storyboard()` in `storyboard_generator.py` produces plausible `Storyboard` objects with real metrics (lines, functions, classes) from code analysis.
6. **Video Merging** — `rendering/video_merger.py` can concatenate video clips via MoviePy or ffmpeg (if ffmpeg is on PATH).
7. **Background Music** — `audio/audio_generator.py` generates white noise with low-pass filter via pydub (basic, but works).

### What's Broken/Aspirational
1. **Video Rendering** — ManimGL scenes, visual metaphors, and animation are all no-op stubs. The pipeline produces static text-over-color clips at best.
2. **TTS/Audio Narration** — Requires ElevenLabs API key; no fallback. Without it, audio pipeline returns `None`.
3. **E2B Execution Capture** — Simulated only; generates fake execution state data.
4. **AI Storyboard** — Fragile JSON parsing, unreliable token estimation, JSON response mode not supported on all Groq models. Will mostly fall through to rule-based.
5. **Semantic Search** — Requires FAISS + sentence-transformers, which aren't in requirements.txt. Will silently fail.
6. **Call Graph Generation** — Always returns `{'error': 'pycallgraph2 not available'}`.
7. **Dependency Analysis** — Always returns `{'error': 'pipdeptree not available'}`.

### Output Quality (inferred)
Without working ManimGL rendering, the **current output is a static slideshow** of text overlays on colored backgrounds, concatenated with silence (since audio returns nothing without ElevenLabs). No animations, no visual metaphors, no narration, no transitions between scenes.

### Customizability
- **Themes**: Light/dark/system — propagate through the test script but the fallback video doesn't use them meaningfully.
- **Video length**: Short/medium/long — controls number of scenes in storyboard.
- **Quality**: 720p/1080p/4k — passed through but fallback rendering only supports basic resolution.
- **Language**: Supposed to control TTS language, but ElevenLabs key is required.
- **Mobile optimization**: Flag exists, no implementation.

## 2. GAPS & RISKS

| Severity | Issue |
|----------|-------|
| **P0** | **The product doesn't produce the advertised output.** Claimed "3Blue1Brown-style animations" are impossible with current code. Output is a static slideshow. |
| **P0** | **No preview capability.** User cannot preview the storyboard or video before the full rendering pipeline runs (which takes minutes and may fail silently). |
| **P0** | **No script editing.** User cannot edit the storyboard script before rendering. The LLM-generated or rule-based script is final. |
| **P1** | **No output format options.** Only MP4 (via MoviePy). No GIF, no WebM, no social-media-optimized formats. |
| **P1** | **Multi-language repo support is uneven.** Python analysis uses AST (good), JS/Java use regex (fragile), other languages (Rust, Go, C++) have no detailed analysis path. |
| **P2** | **No progress feedback during long operations.** The test script just prints "This may take several minutes..." — user has no sense of progress. |
| **P2** | **No export of intermediate artifacts.** Storyboard JSON is saved, but audio files, individual scene videos, and execution traces are not surfaced to the user. |

## 3. BENCHMARK

| Feature | Repo2Video | RepoClip | RepoStudio | Phantom |
|---------|-----------|----------|------------|---------|
| Working video output | ❌ No | ✅ Yes | ✅ Yes | ✅ Yes |
| Preview before render | ❌ No | ✅ Yes | — | ✅ Yes (interactive viewer) |
| Script editing | ❌ No | ✅ Custom prompts | — | ✅ Step-by-step |
| Multi-language code | Partial | Full (web context) | Full (scanning) | Python/TS/JS/C#/Rust |
| Output formats | MP4 only | MP4, GIF | MP4 | MP4 + share link |
| Narration quality | None/poor | ElevenLabs TTS | ElevenLabs TTS | Timed captions |
| Visual quality | Static text | AI clips (Flux/Kling) | Screenshot Ken Burns | Hand-crafted templates |
| Demo available | ❌ No | ✅ repoclip.io | ✅ Live URL | ✅ Phantom viewer |

**Repo2Video is the only project in this category that cannot produce a demo video of itself.** This is the single most critical product gap.

## 4. CHECKLIST

### P0
- [ ] **Make the rendering pipeline produce actual video content** — even if that's just typing animation + code highlights via MoviePy (skip ManimGL entirely). [XL effort]
- [ ] **Add at least gTTS fallback** so audio works without paid API keys. [S effort]
- [ ] **Create a "Generate Demo for This Repo" button** — the tool must be able to create a video of itself. [M effort]

### P1
- [ ] **Add storyboard preview** — let users see and edit the scene list before rendering. [M effort]
- [ ] **Add script editing interface** — allow users to edit narration text per scene. [L effort]
- [ ] **Add WebM and GIF output options** for social media sharing. [S effort]
- [ ] **Add real progress reporting** during the rendering pipeline. [M effort]

### P2
- [ ] **Improve JS/Java analysis** — move from regex to proper AST/tree-sitter parsing. [L effort]
- [ ] **Add video resolution and quality controls** to the UI. [S effort]
- [ ] **Add export of subtitles** as SRT/VTT alongside video. [M effort]

## 5. OPEN QUESTIONS

1. **Is 3Blue1Brown-style animation the right target?** Competitors are targeting 30-60 second promo/walkthrough videos, not detailed educational animations. The ManimGL approach is over-engineered for the actual use case.
2. **Has any user ever successfully generated a complete video?** With the current state, the answer is almost certainly no — which means the entire product hypothesis is untested.
3. **Who is the target user?** The README says "developers" but doesn't specify whether this is for open-source maintainers (promo videos), educators (code walkthroughs), or engineering teams (internal docs).
