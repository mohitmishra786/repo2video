# Task 11 — repo2video vs `brag`: UX/Architecture Comparison (decision doc)

Study subject: [`latent-spaces/brag`](https://github.com/latent-spaces/brag)
(read-only clone; `README.md`, `PRODUCT.md`, `skills/brag/`). This is a
**decision document** — none of the recommendations below are implemented.

**Evidence date: 2026-09-26.**

## 1. Output structure

**brag**: produces one predictable folder, `brag-output/`, containing the
plan, a composition brief, share copy (`share-copy.txt`), and the rendered
`brag.mp4`. The user gets an auditable trail of *why* the video looks the way
it does, alongside the artifact they came for.

**repo2video today**: output is scattered. A run writes
- storyboard JSON (`storyboard_generator.save_storyboard`, path chosen by the caller),
- per-scene MP4s under renderer-specific output dirs (`manim_output/`, or
  fallback `scene_*.mp4` files in the same dir),
- narration MP3s (`scene_<id>_narration_<lang>.mp3`),
- an SRT from `app.py`'s `_generate_subtitles`,
- the final `final_comprehensive_analysis.mp4` (or `_mobile`/`.webm`/`.gif`
  variants) from `VideoMerger`,
- plus `logs/animation_run_*.log` in a separate top-level directory.

There is no single, predictable output folder and no first-class "script"
artifact a user can review or re-run against.

**Recommendation (P2, high value/low risk)**: converge on a single
`repo2video-output/<repo-name>/` directory containing:
`storyboard.json`, `narration/`, `scenes/`, `final.mp4`, `subtitles.srt`,
`share-copy.txt` (new), and `run.log` (copy of the per-run log).
`share-copy.txt` is nearly free — the storyboard already contains a title,
description, and per-scene narrations; formatting them for social is
string work. This also gives Task 12's "demo assets" a stable home.

## 2. Single-command UX

**brag**: the whole interface is one invocable command, `/brag`, with two
optional flags (`--tone`, `--voice`). Zero first-run friction beyond having
the CLI installed; defaults are opinionated (no voiceover, music on, 30-ish
seconds). Documentation, install, and invocation all fit in one README
screen.

**repo2video today**: three entrypoints with different mental models —
`streamlit run app.py` (web UI), `python test_real_repository.py <URL>
[8 flags]` (CLI), and an undocumented FastAPI prototype
(`uvicorn backend.app.main:app`). The Streamlit path is the closest to
"paste URL and go" and is genuinely low-friction. The CLI has 8 flags where
2 would do; the backend is unadvertised and unlaunched (per the security
audit it must stay local until auth/quota exist).

**Recommendation (P1)**: keep Streamlit as the front door, but make the CLI
match brag's ergonomics: a positional URL plus `--tone/--length/--quality`
is already there; trim the *rest* behind sane defaults and document
**one** blessed path in the README ("streamlit run app.py" as step 1, CLI
as step 2). The FastAPI backend stays out of user-facing docs until the
security preconditions in `audit/10` are met. A `--dry-run` exists but is
undocumented in the README — surface it as the "try without rendering"
step.

## 3. Multi-agent distribution pattern

**brag**: one skill source, symlinked into `.claude/skills/`,
`.opencode/skills/`, `.agents/skills/` so Claude Code, opencode, Codex CLI,
and friends all auto-discover the same skill without per-tool config, plus
an `npx skills add` installer and a plugin marketplace manifest.

**Relevance to repo2video**: orthogonal to the core pipeline, but directly
relevant if repo2video ever wants an "explain this repo as a video" mode
invoked from inside an agent session (the agent already has repo access and
could call the pipeline locally, no UI needed). The repo already ships
`.agents/skills/` and `.claude/skills/` entries (for *developing* repo2video
with agents), so the pattern is in use — just not for a repo2video feature.

**Recommendation (future, not scheduled)**: a `repo2video-skill` that wraps
`analyze_github_repo(..., dry-run/short)` and returns either the storyboard
or a finished MP4 path. Cheap to build once Task 07's tested pipeline
functions are stable; zero new rendering code. Keep it out of the
pre-launch critical path.

## 4. Rendering architecture: in-house Manim vs hosted renderer

**brag** does not render video itself. It authors a brief and hands it to
Hyperframes (hosted, paid, HeyGen). **repo2video** renders in-house
(MoviePy composition as the active path, Manim codegen as the repaired
path) via FFmpeg locally.

| Dimension | (a) Stay in-house (Manim/MoviePy/FFmpeg) | (b) Optional hosted backend (Hyperframes-style) |
|---|---|---|
| Control | Full ownership of every frame and timing; code visuals are precise (real filenames/metrics) | Composition limited to what the hosted engine supports; code accuracy is best-effort |
| Cost per video | ~$0 compute (user's CPU); LLM/TTS spend only | Per-render hosted cost on top of LLM/TTS; ties into `audit/09-monetization-audit.md`'s freemium-hosted-vs-OSS question |
| Dependency risk | You own all rendering bugs — this task list literally started with a repo2video rendering compile error and moviepy 1.x/2.x API drift | Vendor availability/pricing changes are someone else's bug but also someone else's break |
| Setup friction | FFmpeg + heavy Python deps (the two biggest install complaints) | Node 22 + `npx hyperframes` + account |
| Offline/self-host | Fully offline-capable (LLM optional via rule-based storyboard) | Requires network + paid account; breaks the pure-OSS story |
| Quality ceiling | Good for code-walkthrough content; motion polish limited by hand-built scenes | Higher out-of-the-box visual polish (motion design, transitions) |

**Neutral read**: the two are complements, not substitutes. In-house
rendering *is* repo2video's differentiation (per `ARCHITECTURE_V2.md`, no
competitor does precise programmatic code animation), while a hosted
backend is an optional "pretty mode" that would move the product toward a
hybrid/SaaS cost model. **Do not implement either now.** If pursued later,
the low-risk shape is an optional `--renderer hyperframes` backend that
consumes the same storyboard JSON — the storyboard is already a clean
interchange format — with in-house rendering kept as the default and the
OSS story intact. Decision owner: chessMan (ties to issue #29
monetization).

## 5. Asset licensing hygiene

**brag** documents exact credits for bundled music ("Happy Beats / Business
Moves" by ende.app, per-file listing with durations) and SFX ("CC0,
Kenney.nl, public domain"), both in `README.md` Credits and in
`skills/brag/assets/music/README.md` / `references/audio.md`.

**repo2video**: no bundled third-party music, SFX, or fonts. Verified:
background "music" is generated white noise via `pydub.generators.WhiteNoise`
(`audio_generator.py:_add_background_music`); render fonts are system font
names (`Arial`, `Courier-New`); no asset directories exist in the tree.
This matches `audit/10-security-legal-audit.md` §"Legal/privacy and assets"
— cross-referenced there, not duplicated.

**Status: no P1 legal item** for bundled assets today. Two proactive notes
for the future: (1) if a royalty-free music bundle is ever added to improve
on white noise (a likely quality complaint), document exact per-file
credits the way brag does; (2) system-font names in `TextClip(font="Arial")
are platform-dependent (the MoviePy fallback already fails on machines
without Arial — seen in local testing), so a bundled OFL-licensed font
(e.g., a Noto/DejaVu face) with credit noted in the README would fix both
robustness and any future attribution question. Not scheduled in this
plan.
