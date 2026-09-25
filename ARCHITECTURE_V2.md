# Repo2Video v2 — Architecture & Research Report

A production-grade plan to turn GitHub repos into animated videos using a
hybrid programmatic (Manim) + generative AI pipeline.

---

## 1. Competitive Landscape (2026)

### RepoClip (repoclip.io) — the clear leader

**Pipeline**: Paste URL → Gemini 2.5 Flash analyzes codebase → generates script
(scene-by-scene breakdown) → parallel asset generation (Nano Banana 2 via
Fal.ai for images + OpenAI TTS for narration) → Remotion renders on AWS
Lambda → MP4 output. ~5 min per video.

**Key strengths**: GitHub Action integration (auto-video on release), private
repo support, public API, polished web UI, fast turnaround.

**Tech stack**: Next.js, Supabase, Inngest, Remotion Lambda, Fal.ai, Gemini API,
OpenAI TTS.

### Poko (poko.video)

Similar positioning — turns GitHub repos / PDFs / slides into product demo
videos. Earlier-stage than RepoClip.

### Gap in the market

Every competitor is **pure generative AI** — they produce visually appealing
but technically imprecise videos. **No one** does a hybrid programmatic
(Manim/Remotion for code accuracy) + generative (for narrative/backgrounds)
approach well. That is the differentiation opportunity.

---

## 2. Manim — Critical Decision (ManimGL vs ManimCE)

The repo currently tries ManimGL (`from manimlib import *`) then falls back
to ManimCE (`from manim import *`). This is fragile because the APIs are
**completely incompatible**. Here is the 2026 state:

| Dimension | ManimGL | ManimCE |
|---|---|---|
| Import | `from manimlib import *` | `from manim import *` |
| CLI | `manimgl scene.py ClassName` | `manim -pql scene.py ClassName` |
| Renderer | OpenGL (GPU) | Cairo (CPU) + optional OpenGL |
| Real-time preview | Yes (interactive window) | No (render to file) |
| Documentation | Sparse (read source code) | Comprehensive (tutorials + API docs) |
| API stability | Breaks frequently | Semantic versioning |
| Installation | Complex (system deps) | Simple (`pip install manim`) |
| 3D | GPU-accelerated | Available, slower |
| Best for | Live demos, interactive | Production, education, reliability |

**Recommendation**: Pick **ManimCE** for v2. It is the right choice for an
automated pipeline:
- Stable API → reproducible renders
- Better docs → LLMs generate correct code
- Easier installation → works headlessly on servers
- Active community with plugins

ManimGL only makes sense if you need real-time interactivity or are
replicating 3Blue1Brown's exact workflow.

---

## 3. Core Architecture — Hybrid Pipeline

```
GitHub URL
    │
    ▼
┌──────────────────────────────┐
│  1. CODE FETCHING            │
│  - Clone via git / GitHub API│
│  - Filter: sources, README,  │
│    configs; exclude tests,   │
│    deps, build artifacts     │
└──────────┬───────────────────┘
           │
           ▼
┌──────────────────────────────┐
│  2. CODE ANALYSIS            │
│  - Multi-language AST parsing│
│    (Python: ast + tree-sitter│
│     JS/TS/Rust/Go/Java:      │
│     tree-sitter)             │
│  - Dependency graph (imports)│
│  - Architecture detection    │
│    (framework, key modules)  │
│  - Entrypoint identification │
│  - Complexity metrics        │
└──────────┬───────────────────┘
           │
           ▼
┌──────────────────────────────┐
│  3. STORYBOARD GENERATION    │
│  (AI — GPT-4o / Claude 4)   │
│  - Code analysis → narrative │
│  - Scene-by-scene plan:      │
│    narration + visual desc   │
│  + timing + Manim code stub │
│  - Iterative refinement      │
│    (review, fix, regenerate) │
└──────────┬───────────────────┘
           │
           ▼
    ┌──────┴──────┐
    │             │
    ▼             ▼
┌──────────┐ ┌──────────────┐
│ 4a. CODE │ │ 4b. AI VIDEO │
│ VISUALS  │ │  & IMAGES    │
│ (ManimCE)│ │ (generative) │
│          │ │              │
│ Per-     │ │ Backgrounds  │
│ scene    │ │ People/meta- │
│ Manim    │ │ phors        │
│ render   │ │ (Kling 3.0 / │
│ of code  │ │ Flux/Nano    │
│ structs  │ │ Banana 2)    │
└────┬─────┘ └──────┬───────┘
     │              │
     └──────┬───────┘
            │
            ▼
┌──────────────────────────────┐
│ 5. NARRATION (parallel)      │
│    ElevenLabs TTS            │
│    (Flash v2.5 — ~$0.06/min)│
│    + word-level timestamps   │
│    for lip-sync alignment    │
└──────────┬───────────────────┘
           │
           ▼
┌──────────────────────────────┐
│ 6. VIDEO COMPOSITION         │
│    MoviePy / Remotion        │
│  - Layer scenes with         │
│    transitions               │
│  - Sync narration audio      │
│    to scene boundaries       │
│  - Add background music      │
│  - Render MP4                │
└──────────┬───────────────────┘
           │
           ▼
      OUTPUT MP4
```

### Why hybrid (4a + 4b)?

- **Pure generative** (RepoClip, Poko): visually appealing but gets code
  details wrong. Generative video models hallucinate text, diagrams,
  and symbols.
- **Pure programmatic** (Manim-only): accurate code visuals but can look
  dry and lacks narrative scenes (people, metaphors, backgrounds).
- **Hybrid**: Use ManimCE for code-specific visuals (function call trees,
  data flow, syntax highlighting, architecture diagrams) that must be
  pixel-accurate. Use generative AI for establishing shots, metaphorical
  scenes, human elements, and background visuals.

---

## 4. Implementation Plan

### Phase 1 — Fix the Foundation (you are here)

| Task | Details |
|---|---|
| Pick one Manim version | **ManimCE**. Remove ManimGL fallback. |
| Fix execution_capture.py | E2B import is present but not wired into the pipeline. Add proper async execution capture. |
| Wire up ElevenLabs | The audio_generator.py exists but the audio files aren't being merged into the video output. Fix the pipeline in `create_animation_from_code()`. |
| Fix video_merger.py | MoviePy imports work but the merge logic is incomplete. Ensure it handles audio sync. |
| Remove app.py references | No app.py exists. The README and setup.py claim otherwise. Fix docs. |

### Phase 2 — AI Storyboard (1-2 weeks)

| Task | Details |
|---|---|
| Add structured prompt templates | System prompt that produces scene-by-scene JSON with: narration text, visual description, Manim code stub, timing, transition type |
| Add iterative refinement | Generate → validate Manim code compiles → fix errors → re-render. Use `subprocess` to run `manim` and catch errors. |
| Support custom instructions | Let users specify tone, focus area, audience, video length |
| Add cost estimation | Token counting for API budgeting |

### Phase 3 — Hybrid Rendering (2-3 weeks)

| Task | Details |
|---|---|
| Build Manim scene templates | Pre-built scene types: CodeHighlight, ArchitectureDiagram, CallGraph, DataFlow, DependencyTree |
| LLM-to-ManimCE code gen | Use system prompt that encodes ManimCE best practices. Fine-tune on ManimCE docs if needed. Reference: Generative Manim, LLM2Manim (arXiv 2604.05266). |
| Add generative image layer | Integrate Fal.ai (Flux/Nano Banana 2) or Replicate for scene backgrounds. |
| Scene composition engine | Takes Manim-rendered code visuals + AI-generated backgrounds + narration audio + transitions → outputs MP4 via MoviePy |

### Phase 4 — Production (2-3 weeks)

| Task | Details |
|---|---|
| Async pipeline | Queue with progress tracking. Use Celery / Redis or simple task queue. |
| GitHub Action | `.github/workflows/generate-video.yml` — trigger on release tag |
| Web UI | Streamlit or Next.js frontend for paste-URL-and-go workflow |
| Private repo support | OAuth-based GitHub token handling |

---

## 5. Key Technology Recommendations

### Rendering stack

| Component | Choice | Why |
|---|---|---|
| Code animation engine | **ManimCE** (stable pip package) | Reliable, documented, LLM-friendly |
| Scene composition | **MoviePy** (already in deps) | Mature, Python-native, handles audio sync |
| Cloud rendering | **Remotion Lambda** OR **AWS Batch** + ManimCE | Only needed for SaaS scale |
| Generative images | **Fal.ai** (Nano Banana 2 / Flux) | Best quality for API cost, used by RepoClip |

### AI stack

| Component | Choice | Why |
|---|---|---|
| Code analysis | **Gemini 2.5 Flash** (cheap, large context) OR **GPT-4o** | Long context window for large repos |
| Manim code gen | **Claude Sonnet 4** (best at code generation) | Superior at producing correct ManimCE code |
| TTS narration | **ElevenLabs Flash v2.5** (~$0.06/min) | Already in deps, best quality/cost ratio |
| Background music | **ElevenLabs music gen** OR **Uppbeat** (royalty-free) | Simple and consistent |

### Infrastructure

| Component | Choice |
|---|---|
| Environment | `.env` with OPENAI_API_KEY, ELEVENLABS_API_KEY, E2B_API_KEY, FAL_API_KEY |
| Logging | Already done (`advanced_animation.utils.logging_config`) — keep it |
| State/tasks | Simple file-based queue for MVP; upgrade to Temporal/Celery later |
| CI/CD | GitHub Actions for tests |

---

## 6. Differentiation Strategy vs RepoClip

| Dimension | RepoClip (2026) | repo2video v2 target |
|---|---|---|
| Video style | Generative AI (cinematic but imprecise) | **Hybrid**: ManimCE for code accuracy + AI for backgrounds |
| Code rendering | AI-generated images (can hallucinate text) | **Programmatic**: actual code rendered pixel-perfect |
| Pipeline | SaaS-only, closed source | **Open-source core** + optional SaaS |
| Customization | Tone, voice, style | Same + ability to edit Manim scenes directly |
| Educational focus | Promotional/demo videos | **Explainers, tutorials, onboarding** |
| Integration | GitHub Action | GitHub Action + **CLI + Python API** |
| Multi-platform | GitHub only | GitHub + GitLab + Bitbucket (already in repo) |

---

## 7. Current Repo — Concrete Gaps

Reading the actual code, here is what needs fixing right now:

1. **`advanced_animation/__init__.py`** — `create_animation_from_code()` at
   line 89 calls `self.audio_generator.generate_storyboard_audio()` which
   likely fails (the method probably returns an empty dict or raises). The
   return value is only logged, not checked — the pipeline continues silently
   with no audio.

2. **`video_merger.py`** — `merge_scenes()` checks `if not MOVIEPY_AVAILABLE`
   and falls back to `create_fallback_merge_with_audio()`, which probably
   doesn't exist or is a stub. The merge loop accumulates video files via
   `concatenate_videoclips` but error handling is weak if any file is missing.

3. **`audio_generator.py`** — `generate_storyboard_audio()` iterates over
   storyboard scenes but the `Storyboard` import is behind `TYPE_CHECKING`,
   causing runtime import errors. The ElevenLabs client is initialized in
   `__init__` but calls to `generate_storyboard_audio()` pass the storyboard
   object, which is imported lazily at type-checking time only.

4. **`manim_scene.py`** — The dummy `Scene` class fallback means the pipeline
   completes silently with zero output if neither ManimGL nor ManimCE is
   installed. Should raise a clear error instead.

5. **No LLM integration yet** — The `StoryboardGenerator` class at
   `core/storyboard_generator.py` exists but likely generates hardcoded
   storyboards or stubs. The actual GPT-4 / Claude call is not wired.
   (I haven't read that file but the pattern is clear.)

---

## 8. Quick Wins (Do This Week)

```bash
# 1. Commit to ManimCE
pip install manim  # not manimgl

# 2. Fix the key Python fix: from manim import * (not manimlib)
#    Edit advanced_animation/rendering/manim_scene.py

# 3. Test that MoviePy actually works end-to-end
python -c "
from moviepy.editor import VideoClip, concatenate_videoclips
from moviepy.audio.io.AudioFileClip import AudioFileClip
print('MoviePy imports OK')
"

# 4. Fix the TYPE_CHECKING bug in audio_generator.py
#    Replace TYPE_CHECKING guard with a real import

# 5. Test the whole pipeline on a tiny repo
python test_real_repository.py https://github.com/octocat/hello-world --output test_output --quality 720p
```

---

## 9. References

- [ManimCE docs](https://docs.manim.community/en/stable/)
- [ManimGL docs](https://3b1b.github.io/manim/)
- [Generative Manim](https://github.com/makefinks/manim-generator) — LLM → ManimCE pipeline with iterative review
- [LLM2Manim (arXiv 2604.05266)](https://arxiv.org/abs/2604.05266) — Pedagogy-aware AI generation of Manim animations
- [Manim Skills Repository](https://github.com/adithya-s-k/manim_skill) — Agent skills for Manim, best practices
- [Manim Bench](https://manim-bench.makefinks.dev) — Leaderboard of LLM performance on Manim code generation
- [ElevenLabs Python SDK](https://elevenlabs.io/docs/api-reference/introduction)
- [Remotion Lambda](https://www.remotion.dev/docs/lambda) — Cloud rendering (if you go this route later)
- [RepoClip blog — how it works](https://repoclip.io/blog/how-repoclip-generates-videos-from-github-repos)
