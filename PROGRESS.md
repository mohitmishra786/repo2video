# PROGRESS.md — Autonomous execution run (Tasks 00–13), 2026-09-26

Status of every task from the execution plan, its PR, and what still needs a
human decision. All PRs were verified with the repo's own CI commands before
opening; each PR ran green in GitHub Actions (8 checks: compile-check,
pytest ×3.9–3.12, ruff, import-check, pip-audit).

## Completed tasks

| Task | PR | Outcome |
|---|---|---|
| 00 — Environment bootstrap | #53 (merged) | Clean venv install logged in `audit/00-environment-log.txt`; confirmed audit assumptions (v0.1.0 tag, 54 commits) |
| 01 — Fix compile error | #54 (merged) | Unterminated f-strings in `video_merger.py` fixed; all 24 `.py` files parse |
| 02 — Fix CI | #55 (merged) | Root-caused commit `972b1ae` ("scrap"): it silently reverted 23 code files to pre-audit versions, re-breaking lint/tests/imports/CI-install. Reverted the regression to the audited `a08a43e` state; CI green again (all 5 original jobs) |
| 03 — CI gates | #56 (merged) | `compile-check` (py_compile on every PR) and warn-only `pip-audit` gates added alongside pytest/lint/import-check |
| 04 — Injection surface map | #57 (merged) | `audit/04-security-injection-surface.md`: 8 call sites catalogued with reachability analysis |
| 05 — Neutralize Manim injection | #58 (merged) | `generate_scene_code()` implemented with repr-escaped literals/validated identifiers/numeric coercion + `ast.parse` runtime guards; hostile-payload verified inert |
| 06 — Injection tests + E2B hardening | #59 (merged) | `tests/test_injection_safety.py`; E2B sandbox now network-isolated (`allow_internet_access=False`) with hard timeouts, explicit `E2B_API_KEY` gate; modernized to SDK 2.x API (the old calls never worked) |
| 07 — Real test suite | #60 (merged) | 77 tests (now 78) replacing the ad-hoc script; coverage baseline 41% committed to `audit/07-coverage-report.txt`; fixed missing `tree-sitter` core dep and a Java-extraction bug |
| 08 — Ruff cleanup | #61 (merged) | Triaged: 12 unused imports, 3 bare excepts, 9 unused locals removed; per-file-ignores narrowed 14 → 4 with documented reasons; findings-without-ignores 117 → 66 |
| 09 — Dependency audit | #62 (merged) | `audit/09-dependency-audit.txt` with dispositions: pillow (35 CVEs) and click blocked by upstream caps (moviepy, gTTS); diskcache unfixed (hard manimgl dep); setuptools deliberately <81 for manimgl `pkg_resources` |
| 10 — Repo identity | #63 (merged) | `repo2video` naming consistent repo-wide; GitHub description + 9 topics set via `gh repo edit` |
| 11 — brag comparison | #64 (merged) | `audit/11-brag-comparison.md` decision doc (5 subsections; nothing implemented, per plan) |
| 12a — Execution off by default | #65 (merged) | `capture_execution=False` default + regression test; font-fallback fix (blank-render bug) enabling sample generation |
| 12c — Pages + links | #66 (open) | GitHub Pages live (`https://mohitmishra786.github.io/repo2video/`), homepage set, README site badge, all README links verified 200 |
| 13 — This summary | — | `PROGRESS.md` |

## Handoffs (manual steps the agent could not complete)

| Item | Where it stopped | What chessMan needs to do |
|---|---|---|
| Social preview image | No REST API for social-preview upload | Upload `docs/social-preview.svg` via repo Settings (one drag-and-drop) |
| Sample videos (checklist P0) | Rendering now works (3.0s MP4 verified after #65); publishing is a content judgment call ("only if genuinely watchable") | Generate 3 samples from public repos and attach to the release/README |
| Docker clean-install check | Docker daemon not running on this machine | Optionally add a Docker-build CI job (`Dockerfile` exists) |

## Remaining items that need a human decision

| Decision | Context | Where discussed |
|---|---|---|
| Hosted vs local-only launch | FastAPI backend stays private until auth/quotas/retention exist (per `audit/10-security-legal-audit.md` P0) | `audit/06-pre-launch-checklist.md` P1 row 2; issue #29 |
| Pricing intent (v1) | Free local/BYOK vs measured-cost pricing | `audit/06-pre-launch-checklist.md` P1 row 3; issue #29 |
| Optional hosted renderer (Hyperframes-style "pretty mode") | Decision doc only — tradeoffs in `audit/11-brag-comparison.md` §4 | Task 11 |
| Naming | Standardized on `repo2video` (lower-risk default); branding is chessMan's call | Task 10 PR notes |
| Launch timing / channels (Show HN, Product Hunt) | Gated on the P0 checklist being green — it now is, minus the sample videos | `audit/06-pre-launch-checklist.md` P2 |
| Copyright confirmation | `LICENSE` says "Mohit Mishra" (restored in #55); confirm correct owner | `audit/10-security-legal-audit.md` open question |

## Follow-up run — dependency vulnerability sweep (PR #68)

Re-applied the closed Dependabot PR #52 (Next.js 14.2.35 → 16.3.6, React
19.2) on the repaired main. Its CI had failed only because it branched off
the broken 'scrap' state, not because of the bump. This closes all 23 open
Dependabot alerts (every one was `next` in `frontend/package.json`), adds a
committed `package-lock.json` (first lockfile in the repo), a working
`npm run lint` (Next 16 removed `next lint`), and a new `frontend-build`
CI gate (npm ci + npm audit + lint + build) so the frontend can no longer
break silently — CI is now 9 green checks.

Remaining advisories are unchanged from the dispositions in
`audit/09-dependency-audit.txt`: pillow (35) and click (1) are blocked by
upstream caps verified in the installed metadata (`moviepy 2.2.1:
pillow<12.0`, `gtts 2.5.4: click<8.2`, both latest releases); diskcache
(no fix exists) is a hard manimgl dependency; setuptools is held <81 for
manimgl's `pkg_resources`. These stay behind the warn-only pip-audit gate.

## Current state

- CI: 9 green checks on every PR (compile-check, pytest 3.9/3.10/3.11/3.12, ruff, import-check, warn-only pip-audit, frontend-build)
- Tests: 78 passing, offline, ~7s; injection-safety regression suite included
- Security: repo-derived text can no longer execute as Python; E2B execution is opt-in, network-isolated, and timeout-bounded
- Lint: `ruff check .` → 0 findings
- Docs: README/USAGE_GUIDE/setup.py naming consistent; landing page live
- Known accepted risks: pillow/click CVEs (blocked by upstream caps — `audit/09-dependency-audit.txt`); FastAPI backend not production-ready (kept private)
