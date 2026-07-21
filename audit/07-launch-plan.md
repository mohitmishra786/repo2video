# Launch Plan

## Strategic Context (July 2026)

The "repo to video" space is **already active** with multiple competitors having launched in 2026:
- RepoClip: SaaS, $24-166/mo, launched Feb 2026, Show HN success, paid plans live
- RepoToViralVideo: OSS (40 stars), launched Feb 2026, positioned for X/LinkedIn virality
- repo-explainer: OSS (3 stars), Jan 2026, uses Gemini VEO
- Repodcast: OSS, comprehensive technical blog post
- Phantom: OSS (7 stars), Apr 2026, focused on code visualization

**The window for "first mover" is closed.** Repo2Video must differentiate on: (a) being free and fully open-source, (b) having a unique angle (educational code walkthrough vs. promo video), or (c) superior developer experience.

## Recommended Launch Sequence

### Phase 0: Fix the Product (1-2 weeks)
Before any launch activity, the product must produce a working video. See Pre-Launch Checklist (06-pre-launch-checklist.md). Without this, every launch channel will generate negative sentiment ("this doesn't work").

### Phase 1: Soft Launch — Developer Communities (Week 1)
**Goal:** First 20-50 GitHub stars, first users, first feedback.

**Channels:**
1. **Reddit** — Post to r/Python, r/programming, r/github
   - Format: "I built a tool that turns any GitHub repo into a narrated code walkthrough video"
   - Include: 30-second demo video, GitHub link, honest description of current limitations
   - DO NOT: Make it sound like a finished product. Frame as "early beta, feedback welcome"
   
2. **Dev.to / Hashnode** — Build log / tutorial
   - Title: "How I Built an AI Pipeline to Turn GitHub Repos into Animated Videos"
   - Content: Architecture decisions, challenges, lessons learned
   - Include: Code snippets, pipeline diagram, demo video

3. **Hacker News (Show HN)** — The primary launch event
   - Title format: `Show HN: Repo2Video – Paste a GitHub URL, Get a Narrated Code Walkthrough Video`
   - Timing: Tuesday-Thursday, 10 AM ET (14:00 UTC) for maximum developer visibility
   - First comment: Founder's story — why they built it, what it does, what's next
   - Be present for the first 4 hours responding to every comment

### Phase 2: Amplification (Week 2)
**Goal:** Convert early interest into sustained attention.

**Channels:**
1. **X/Twitter thread** — 5-8 tweets: the hook, how it works, what it produces, link to try it
2. **Product Hunt launch** — Only after fixing the product and gathering early user feedback
   - Hunter: Ideally someone with dev-tool launch experience
   - Assets: Demo video, 5+ screenshots, compelling tagline
   - Tagline option: "Turn any GitHub repo into a narrated code walkthrough video — open source, free, runs on your machine"
3. **LinkedIn post** — Technical audience, architecture-focused

### Phase 3: Long-Tail Distribution (Ongoing)
**Goal:** Sustainable organic discovery.

**Channels:**
1. **PyPI submission** — `pypi install repotovideo` should work
2. **SaaSHub listing** — Free listing, long-tail SEO for "repo to video" keywords
3. **Awesome lists** — Submit to `awesome-python`, `awesome-developer-tools`, `awesome-open-source`
4. **GitHub topic tagging** — Already done in pre-launch

## Channel-Specific Preparation

### Show HN Preparation
- **Title options** (test multiple):
  - "Show HN: Repo2Video – Free, open-source GitHub-to-video generator"
  - "Show HN: I built a tool that makes narrated code walkthroughs from any GitHub repo"
  - "Show HN: Turn any GitHub repo into an explainer video — open source, local-first"
- **First comment template**: 2-3 paragraphs: "Hi HN, I built this because... Here's how it works... What's next..."
- **Anticipated questions**: How is this different from RepoClip? What about large repos? Can I edit the script? API cost? Why open source?
- **Have answers prepared** for: performance, cost (API keys), rendering time, output quality, language support, comparison to competitors

### Product Hunt Preparation
- **Tagline** (60 char max): "Generate narrated code walkthrough videos from any GitHub repo — free & open source"
- **Description** (500 char max): Clear, specific, includes GitHub link
- **Gallery images**:
  1. Screenshot of the app with a generated video
  2. Pipeline diagram
  3. Sample output (before/after)
  4. Code analysis visualization
  5. Installation instructions
- **First comment**: "I'm the founder. Here's why I built this and where it's going..."

### Reddit Strategy
- **Subreddits**: r/Python (2.5M), r/programming (5M+), r/github (600K), r/SideProject (1M+)
- **Format per subreddit**:
  - r/Python: Emphasize the Python/Streamlit stack, AST analysis
  - r/github: Emphasize GitHub API integration, open-source use case
  - r/SideProject: Personal story, challenges, learning
- **DO**: Engage in comments, be honest about limitations, ask for feedback
- **DON'T**: Post the same link to multiple subs simultaneously; use different angles

## Success Metrics

| Metric | Good | Great | Amazing |
|--------|------|-------|---------|
| GitHub stars (week 1) | 50 | 150 | 300+ |
| GitHub stars (month 1) | 150 | 500 | 1000+ |
| Product Hunt upvotes | 50 | 150 | 300+ |
| Working installs (month 1) | 20 | 100 | 500+ |
| Videos generated (month 1) | 50 | 200 | 1000+ |

## Budget (Launch Costs)

| Item | Cost |
|------|------|
| Domain registration (repotovideo.com) | ~$12/year |
| Show HN | $0 |
| Reddit | $0 |
| Product Hunt | $0 |
| GitHub Pages | $0 |
| API costs (testing) | ~$20 (Groq + ElevenLabs trial) |
| **Total** | **~$32** |

The beauty of an open-source dev tool launch: the only real costs are domain + API test credits.

## 5. OPEN QUESTIONS

1. **Should we wait for a "perfect" product or launch with a minimal working version?** Current evidence from 2026 launches (Gingiris playbook) strongly favors "launch early, iterate fast." A working-but-minimal video generator that produces 30-second narrated slideshows is launchable.
2. **Is the founder willing to spend 4+ hours on launch day responding to comments?** This is the single biggest factor in Show HN success per every analyzed playbook.
3. **Is there a "hook" or unique angle?** "Open source alternative to RepoClip" is a valid position. "Local-first, no upload to cloud" is another. "Educational code walkthroughs" vs. "promo videos" is a third. Pick one.
