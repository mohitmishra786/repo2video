# Marketing & GTM Audit

## 1. CURRENT STATE

### Audience Targeting
The implied audience across README and docs is **software developers** — specifically open-source maintainers who want promotional videos for their repos. This is a real audience that exists and is underserved (proven by RepoClip's early traction, Show HN success with 200+ points). However:
- The README doesn't explicitly call out *who* this is for or *why* they need it
- No use-case examples (e.g., "for your next Show HN," "for your Twitter launch thread," "for your conference talk")
- No comparison to alternatives (freelance video editors, other AI tools, doing it manually)

### Current Presence
- **GitHub**: 0 stars, 0 forks, 0 watchers — zero organic presence
- **Reddit**: No mentions found via web search
- **Hacker News**: No mentions found
- **Product Hunt**: No listing
- **Twitter/X**: No mentions found
- **dev.to / Hashnode**: No articles
- **YouTube**: No demo video
- **PyPI**: No package published

### Positioning/Messaging
Current README tagline: *"RepoToVideo is a powerful tool designed to help developers convert GitHub repositories into animated videos."* This is generic and doesn't differentiate.

Competing taglines in the same space:
- RepoClip: "Turn any GitHub repo into a demo video in 60 seconds"
- RepoToViralVideo: "Turn any GitHub repository into a viral promo video in one-click"
- repo-explainer: "Auto-generate 30-second explainer videos from any git repository using AI"

**Problem with Repo2Video's messaging**: It says nothing about speed ("in 60 seconds"), quality ("viral"), or format ("demo video"). It uses the generic "animated videos" which could mean anything.

### Content Marketing Opportunities
The single most obvious content asset — **a demo video of RepoToVideo generating a video about RepoToVideo** — does not exist. This is the "meta" pitch that competitors (RepoToViralVideo, repo-explainer) have explicitly used. The ironic/recursive nature of a "repo-to-video" tool generating a video of its own repo is a powerful marketing hook that is currently untapped.

## 2. GAPS & RISKS

| Severity | Issue |
|----------|-------|
| **P0** | **No demo video exists.** For a product whose output is video, this is fatal. Every competitor has at least a sample output. |
| **P0** | **No external presence on any channel.** Zero mentions, zero discussions, zero social proof. |
| **P1** | **Messaging doesn't differentiate.** "Powerful tool" and "animated videos" are commodity phrases. |
| **P1** | **No clear target use case.** Is this for Show HN launches? Internal documentation? Educational content? The README doesn't say. |
| **P2** | **No "How it works" visual explainer.** The pipeline diagram exists in AGENTS.md but not in the README. |
| **P2** | **No social sharing buttons or viral hooks** in the product itself. |
| **P2** | **No email capture or waitlist** — even a simple "notify me when ready" form. |

## 3. BENCHMARK — Where Similar Projects Found Audience

Based on competitive analysis of 10+ projects in this space (all launched Jan-Jul 2026):

| Channel | Repo2Video | Peers | Best For |
|---------|-----------|-------|----------|
| GitHub Show HN | ❌ | ✅ RepoClip (200+ pts), others | Developer-first tool launches |
| Product Hunt | ❌ | ✅ RepoClip (launched) | Broader tech audience |
| Reddit (/r/programming, /r/github) | ❌ | — | Community validation |
| dev.to build logs | ❌ | ✅ RepoClip had detailed dev.to post | Technical audience, long-tail SEO |
| X/Twitter launch thread | ❌ | — | Rapid virality |
| YouTube demo | ❌ | ✅ Multiple competitors | Visual proof |
| PyPI listing | ❌ | — | Install convenience |

## 4. CHECKLIST

### P0 — Before Any Launch Activity
- [ ] **Fix the product so it can produce a demo video** — even a 30-second clip with basic animations + gTTS. [XL effort]
- [ ] **Create a "meta" demo video**: RepoToVideo generating a video of itself. [M effort after product fix]
- [ ] **Craft a specific tagline**: e.g., "Paste any GitHub URL → Get a 1080p narrated code walkthrough video in under 5 minutes" [S effort]

### P1 — Pre-Launch Marketing
- [ ] **Write and publish a "building in public" post** about the technical architecture and challenges. [M effort]
- [ ] **Post to relevant Reddit communities** — r/programming, r/Python, r/github, r/SideProject — with a "I built a thing" narrative, not a product pitch. [M effort]
- [ ] **Create a Product Hunt "Coming Soon" page** to capture early interest. [S effort]
- [ ] **Set up a simple landing page** (GitHub Pages or Vercel) with a "Get notified" email form. [S effort]

### P2 — Growth
- [ ] **Create a 60-second demo video** optimized for X/Twitter (vertical format, captions, hook in first 3 seconds). [M effort]
- [ ] **Draft the Show HN post** — title, story, comment strategy — ready to go when the product works. [S effort]
- [ ] **Build a simple "Share this video" feature** that includes a backlink to RepoToVideo. [M effort]

## 5. OPEN QUESTIONS

1. **Is the founder willing/able to invest in marketing?** Building in public requires consistent effort over weeks, not a single push.
2. **Any existing network or audience?** The founder has 785 GitHub followers — this is a significant asset. Are they following because of other projects?
3. **Is there a preferred launch channel?** The founder's GitHub profile shows 117 public repos — there's clearly an active builder. Which community are they most active in?
