# Task 04 — Security Injection Surface Map

Scope: every place where text derived from the *target* (user-supplied) repository —
file contents, filenames, function/class names, docstrings, README text, or
model output influenced by that text — flows into (a) generated Python source
that is later executed/imported/rendered via Manim, or (b) an E2B sandbox call.

Evidence date: 2026-09-26, on the restored audit-implementation state (a08a43e).
Code-path analysis only; no exploit was constructed or executed.

## 1. Execution-relevant call sites (full list)

### 1a. Generated Python source written to disk and executed as a subprocess

| # | Call site | What is interpolated | Origin of the text | Destination |
|---|-----------|----------------------|--------------------|-------------|
| 1 | `advanced_animation/rendering/manim_scene.py:426` (`_get_scene_body`) | `truncated` narration string | storyboard scene narration (AI output influenced by repo content, or rule-based fallback) | generated scene file `scene_<id>.py`, written by `create_scene_file` (manim_scene.py:338), then executed via `manim`/`manimgl` subprocess in `render_with_manim` (manim_scene.py:1218, `subprocess.run(..., timeout=300)`) |
| 2 | `advanced_animation/rendering/manim_scene.py:464` and `:468` (`_generate_visual_elements_code`) | `text_content` = `element.properties["text"|"value"]` (AI output) inside `Text("...")` | AI storyboard JSON → `VisualElement.properties` (`storyboard_generator.py:525`) | same generated scene file |
| 3 | `advanced_animation/rendering/manim_scene.py:466` | `text_content` inside `Code(code="...")` | AI storyboard JSON | same generated scene file |
| 4 | `advanced_animation/rendering/manim_scene.py:481-496` (`_generate_animation_steps_code`) | `step.target` used as a Python identifier in `self.play(FadeIn({target_var}))` | AI storyboard JSON `animation_sequence[].target` | same generated scene file |

Important reachability note: `create_scene_file` calls `self.generate_scene_code(...)`
(manim_scene.py:351), but **no method named `generate_scene_code` is defined** on
`ManimSceneRenderer` in the current tree — the call raises `AttributeError`, which
`render_scene` catches and falls back to `create_fallback_video` (MoviePy). The
string-built-Manim path is therefore currently **unreachable dead code**, not an
active exploit path. It must still be neutralized (Task 05) because any repair of
the codegen would re-open it, and because dead-but-executable codegen is a standing
template-injection hazard.

### 1b. E2B sandbox calls (remote execution of repo-derived Python)

| # | Call site | What is executed | Origin | Notes |
|---|-----------|------------------|--------|-------|
| 5 | `advanced_animation/core/execution_capture.py:49` (`capture_execution`) → `_capture_python_execution` (:81) → `Sandbox(template="base")` (:101) | `scene.code_snippet` (instrumented via `_instrument_python_code`, :167) | AI storyboard JSON `scenes[].code_snippet` (`storyboard_generator.py:545`); the prompt invites the model to include "runtime execution visualization" (:470) — i.e. model- and repo-influenced Python | default `capture_execution=True` on `create_animation_from_code` (`advanced_animation/__init__.py:57`), invoked by `test_real_repository.py:131`. Guarded only by `E2B_AVAILABLE` (package import); no explicit API-key check in this module — without a key, `Sandbox()` raises and the caller simulates. |
| 6 | `advanced_animation/rendering/manim_scene.py:359` (`execute_code_with_e2b`) → `e2b.Sandbox.create(template="python")` (:377) → `sandbox.commands.run(f"{command} {file_path}", timeout_seconds=20)` | arbitrary `code` string | caller-supplied; currently **no caller** passes repo-derived code into this method (grep-verified), so it is dormant but reachable from any future wiring | has an `enable_e2b` gate = `E2B_AVAILABLE and bool(E2B_API_KEY)` (manim_scene.py:252) |

### 1c. Repository-derived data sent to third-party services (data exposure, not code exec)

| # | Call site | What leaves the machine |
|---|-----------|------------------------|
| 7 | `advanced_animation/core/storyboard_generator.py:459` (`_create_storyboard_prompt`) and `:383` (`_create_chunked_storyboard_prompt`) | `json.dumps(code_analysis)` — includes docstrings, function/class names, error snippets — sent to Groq or OpenAI. Docstrings/identifiers are attacker-controllable prompt-injection channels. |
| 8 | `advanced_animation/audio/audio_generator.py:132` (ElevenLabs) / `:179` (gTTS) | narration text (model output influenced by repo content) sent to elevenlabs.io / translate.google.com |

### 1d. Safe-by-construction sites (verified, no change needed)

- `advanced_animation/visualizations/visual_metaphors.py` — builds Manim objects
  via the API (`Text(str(value))`, :310/:340), never string-builds Python source.
- `advanced_animation/rendering/video_merger.py` — untrusted text only becomes
  MoviePy `TextClip(text=...)` render inputs; ffmpeg concat lists contain local
  file paths only (:205, :263).
- `advanced_animation/rendering/manim_scene.py:1279` (`create_fallback_video`) —
  MoviePy clip composition with untrusted strings as render data. This is the
  **actual active render path** today.
- `code_analysis.py` — AST analysis only; never executes repo code.

## 2. Threat summary

A malicious repository can steer model output (docstrings/comments are read into
`code_analysis`, then `json.dumps`'d into the storyboard prompt). If the model
echoes hostile content into `concept`/`narration`/`properties.text`/`code_snippet`,
site #1–#4 turn it into executable Python on the user's machine (when the Manim
codegen is repaired), and site #5 runs it inside E2B. Example payload shape:
a repo file containing `"; import os; os.system('id') #` positioned so it lands
inside a `Text("...")` or `code_snippet` literal.

## 3. Fix plan (Task 05/06)

- Dead codegen path (#1–#4): delete or repair via safe templating — untrusted
  strings must be embedded as escaped literals (`repr()` / `json.dumps` of the
  string) or rendered through Manim API objects, never concatenated raw. Add a
  runtime guard that refuses to write a scene file unless every interpolated
  value is a validated escaped literal.
- E2B path (#5, #6): keep sandbox; add explicit E2B_API_KEY gate to
  `execution_capture`, keep the 1MB size cap, and document/configure sandbox
  timeout, resource limits, and network policy (Task 06).
- Data-exposure sites (#7, #8): out of scope for the injection fix; tracked in
  the security audit's P1 "prompt injection/data leakage" item.

## 4. Task 06 — E2B isolation status (verified against E2B docs + SDK)

Verified capabilities of the E2B sandbox and the Python SDK (e2b 2.51):
[E2B internet-access docs](https://docs.e2b.dev/network/internet-access),
[update-sandbox-network API](https://docs.e2b.dev/api-reference/sandboxes/update-sandbox-network).

| Control | SDK support | Status after Task 06 |
|---|---|---|
| Timeout | `Sandbox.create(timeout=...)` (sandbox lifetime) and `commands.run(..., timeout=...)` (per command) | Set in both `_capture_python_execution` (execution_capture.py: sandbox + command timeout = `max_execution_time`, default 30s) and `execute_code_with_e2b` (20s both) |
| Network restriction | `Sandbox.create(allow_internet_access=False)` disables all outbound egress (equivalent to `deny_out: ["0.0.0.0/0"]`) | Set (`allow_internet_access=False`) in both E2B call sites |
| Resource limits | CPU/RAM are properties of the sandbox *template* (e.g. `base`); the SDK exposes `get_metrics()` but no per-call CPU/mem override | Bounded by template choice + 1MB source cap + short lifetime; per-job spend caps remain a monetization-layer concern (audit/09) |
| Filesystem isolation | Each sandbox is an isolated VM with its own filesystem; state written to `/tmp` never touches the host | Documented; the capture path reads `/tmp/execution_state.json` from inside the sandbox |
| Explicit key gate | — | `_capture_python_execution` now requires `E2B_API_KEY` explicitly; without it, the path simulates instead of spawning a sandbox |

Remaining limitations (documented, not fixed here):
- Sandbox network egress defaults to *allowed* if a future call site omits
  `allow_internet_access=False`; both current sites set it, but a lint/test
  guard should watch for regressions.
- Resource ceilings are template-defined; precise CPU/RAM budgets need the
  template owner's configuration and are tracked with the monetization work.

