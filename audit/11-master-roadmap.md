# Master Roadmap — 30/60/90 Day Plan

## Summary: Where We Are

A solo project with ~48 commits, last updated 6 months ago (Jan 26, 2026). 0 stars, 0 forks. The product claims to convert GitHub repos into animated videos but **cannot produce a working video** due to stub/no-op rendering code and a missing UI (`app.py` does not exist). The codebase has ~6,500 lines across 16 Python files, significant duplicate/dead code, and an overly heavy dependency footprint (154 packages).

The competitive landscape has **accelerated rapidly** in 2026. 10+ projects in this space launched between Jan-Jul 2026, with at least 2 (RepoClip, Phantom) having working products and early traction. **The window for "first mover" is closed, but the window for "open source alternative" is open** if the product works.

---

## Dependency Graph

```
[Fix rendering] ──> [Create demo video] ──> [READ.ME + GitHub SEO] ──> [Launch]
     │                       │
     └──> [Security fixes]   └──> [Test pipeline E2E]
           (sanitization,
            size limits)
     
[Remove dead code] ──> [Trim requirements.txt] ──> [CI/CD setup]
```

Key dependencies:
- **Launch is blocked by**: a working video output + demo video + fixed README
- **Demo video is blocked by**: working rendering pipeline
- **Working rendering pipeline requires**: either fixing ManimGL (XL) or replacing with MoviePy (L)
- **README fixes are independent** and can happen day 1
- **Security fixes** (sanitization overreach) can happen in parallel with rendering work

---

## Phase 1: Foundation (Days 1-10)

### Week 1-1.5: Rendering Fix

| Day | Task | Effort | Depends On |
|-----|------|--------|------------|
| 1 | **Decide: fix ManimGL or replace with MoviePy?** | S | — |
| 1-3 | **If replacing**: Build a MoviePy-based scene renderer that takes storyboard JSON and produces timed video clips with: code text overlay, fade transitions, basic typing effect, colored backgrounds per scene type | L | Decision from Day 1 |
| 1-3 | **If fixing ManimGL**: Remove stub classes, install ManimGL, fix generated scene code templates, test rendering a single scene | XL | — |
| 3-5 | **Integrate gTTS fallback** — Audio pipeline works without API keys. Generate `.mp3` per scene, sync with video duration | S | — |
| 5-7 | **Integrate audio + video** — `video_merger.py` already exists and works. Wire gTTS output into it | S | Above |
| 5-7 | **Add progress reporting** to the pipeline (callback-based, suitable for Streamlit integration later) | M | — |
| 7-9 | **Test end-to-end on 5 repos** of varying sizes. Fix crashes. Measure render time for small/medium/large repos | M | All above |
| 9-10 | **Record the "meta" demo video** — Run the tool on itself. Capture output as GIF + MP4 | S | Working pipeline |

### Week 1.5-2: Cleanup & Security

| Day | Task | Effort | Depends On |
|-----|------|--------|------------|
| 8-9 | **Fix content sanitization** — Remove URL/CC/phone redaction; keep only email and API key patterns | S | — |
| 8-9 | **Add repo size limits** — Warn/reject repos > 100MB | S | — |
| 9-10 | **Remove dead code paths**: E2B stubs, ManimGL stubs (if replacing), duplicate methods, LLM-generated pseudo-docstrings | M | Rendering decision |
| 9-10 | **Trim requirements.txt** — Remove OpenCV, scikit-learn, SciPy, plotly, kaleido, faiss-related, sentence-transformers. Target ~40 packages | S | — |
| 10 | **Test clean install** — `pip install -r requirements.txt` on a fresh Python env. Measure time and success | S | Above |

---

## Phase 2: Launch Prep (Days 11-20)

### Week 2-3: UI & Documentation

| Day | Task | Effort | Depends On |
|-----|------|--------|------------|
| 11-12 | **Build `app.py`** — Minimal Streamlit UI: URL input → "Generate" button → progress bar → download link. Keep it under 150 lines. It's okay to start simple | M | Phase 1 |
| 12-13 | **Fix README** — Replace all placeholder URLs, add demo GIF, add badges, fix clone instructions | S | Demo video |
| 12-13 | **Set GitHub repo metadata** — Description, topics (8-10), website URL, social preview image | S | — |
| 13-14 | **Add CI/CD** — GitHub Actions workflow: `pip install → python -c "import ..."` smoke tests on push | M | Trimmed requirements |
| 14-15 | **Create landing page** — GitHub Pages or Vercel one-pager with: tagline, 30s demo video, install command, GitHub link | M | Demo video |
| 15-17 | **Add issue templates, CONTRIBUTING.md, SECURITY.md** | S | — |
| 17-18 | **Create GitHub Release v0.1.0** — Tag, changelog, release notes | S | — |

### Week 3: Launch Material

| Day | Task | Effort | Depends On |
|-----|------|--------|------------|
| 17-18 | **Write Show HN post** — Title (3 variants), first comment story, FAQ for anticipated questions | M | Working product |
| 18-19 | **Record Product Hunt assets** — Gallery images (5+), demo video (90s), tagline, description | M | Demo video |
| 19-20 | **Prepare Reddit posts** — r/Python, r/programming, r/github, r/SideProject (different angles for each) | S | Working product |
| 19-20 | **Prepare X/Twitter thread** — 5-8 tweets with screenshots/GIF | S | Working product |
| 20 | **Set up analytics** — Privacy-respecting (Plausible or just GitHub traffic stats for now) | S | — |

---

## Phase 3: Launch (Days 21-23)

### The Launch Window

Launch on Hacker News (Show HN) as the primary channel. Reddit should be the **same week** for PyPI and Python news.

| Day | Event | Channel | Time (ET) |
|-----|-------|---------|-----------|
| 21 | **Show HN launch** | Hacker News | 10 AM ET |
| 21 | **X/Twitter thread** | X | 10:30 AM ET |
| 21 | **Comment engagement** (4+ hours) | HN | As needed |
| 22 | **Reddit posts** (staggered by 6h) | Multiple subreddits | 8 AM and 2 PM ET |
| 22 | **Dev.to build log** | dev.to | 10 AM ET |
| 23 | **Indie Hackers post** | Indie Hackers | 10 AM ET |
| 23 | **LinkedIn post** | LinkedIn | 12 PM ET |

---

## Phase 4: Post-Launch (Days 24-90)

### Week 4-6: Respond & Iterate

| Week | Focus | Activities |
|------|-------|------------|
| 4 | **Community response** | Reply to every Show HN/Reddit/PH comment. Fix P0 bugs reported by users within 24 hours |
| 4 | **First user feedback** | Identify top 3 friction points. Fix the easiest one immediately |
| 4-5 | **PyPI package** | Publish to PyPI so `pip install repotovideo` works. This is a big distribution channel |
| 5 | **Iteration based on feedback** | Ship v0.1.1 with bug fixes from first users |
| 5-6 | **Product Hunt launch** | If Show HN generated interest, now is the time to PH. Use the user base as proof |

### Month 2-3: Growth

| Week | Focus | Activities |
|------|-------|------------|
| 6-8 | **Content marketing** | Write 2-3 blog posts: technical architecture, comparison to competitors, tutorial. Pitch to dev.to, HackerNoon |
| 6-8 | **Community building** | Set up GitHub Discussions or Discord. Pin a "what to build next" thread |
| 8-10 | **Feature development** | Based on user feedback: script editing, custom voice selection, output format options |
| 10-12 | **Monetization exploration** | If users are asking for cloud hosting or premium features, design a freemium tier. If not, keep it free |
| 12 | **Status update** | Public "1 month after launch" retrospective with metrics |

---

## P0 Items (From All Artifacts) — Non-Negotiable Before Any Launch

These are the items that, if missing, make launch a bad idea:

1. **Working video rendering** (Product Audit, P0) — Must produce actual video, not static fallback
2. **Working app.py or UI** (UI/UX Audit, P0) — Must have a user-facing interface
3. **Fixed README clone URLs** (SEO Audit, P0) — Must not 404 on first impression
4. **GitHub repo description + topics** (SEO Audit, P0) — Must appear in search results
5. **Resolved name confusion** (SEO Audit, P0) — Consistent `repo2video` vs `RepoToVideo`
6. **Fixed content sanitization** (Security Audit, P0) — Must not destroy code content
7. **Demo video of the tool working** (Marketing Audit, P0) — Must show, not tell

Items 3-5 and 6 can be done by Day 2. Item 7 is blocked by Item 1. Items 1-2 are the critical path.

---

## Effort Estimates for the Critical Path

| Item | Hours | Can Parallelize? | Owner |
|------|-------|-----------------|-------|
| MoviePy rendering rewrite | 15-25 | No (core work) | Solo dev |
| gTTS integration | 2-4 | Yes | Solo dev |
| app.py Streamlit UI | 4-6 | Yes (separate file) | Solo dev |
| README + GitHub SEO fixes | 1-2 | Yes | Solo dev |
| Security sanitization fix | 1-2 | Yes | Solo dev |
| Demo video creation | 1-2 | Blocked by rendering | Solo dev |
| Requirements cleanup | 2-3 | Yes | Solo dev |
| CI/CD setup | 2-4 | Yes | Solo dev |
| **Total critical path** | **~28-48 hours** | — | Solo dev |

This is achievable in **1-2 weeks of focused work** for a solo developer working evenings/weekends, or **5-7 days** if working full-time.

---

## Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Rendering rewrite takes longer than expected | Medium | High (delays launch) | Start with the simplest possible output (static frames + fade transitions) |
| ManimGL cannot be made to work | High (given current state) | Medium | Don't try to fix it. Use MoviePy from the start |
| Show HN post doesn't get traction | Medium | Medium | Have Reddit and dev.to as backup channels |
| Competitor launches with more features during our fix period | Low (space is already active) | Low | Differentiate on "open source" and "local-first" |
| Founder loses motivation during fix period | Medium | Critical | Launch fast — momentum is motivating. Set a 14-day deadline |
| API costs surprise during testing | Low | Low | Use gTTS (free) and local rendering. Only use paid APIs for premium output |
