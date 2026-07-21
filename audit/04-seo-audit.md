# SEO & Discoverability Audit

## 1. CURRENT STATE

### GitHub-Native SEO (Repo-Level)
**Current GitHub repo page state (verified via fetch on 2026-07-21):**
- **Description**: ❌ Empty — "No description, website, or topics provided."
- **Topics/Tags**: ❌ None — `[no topics listed]`
- **Website URL**: ❌ Not set — "No website link"
- **Social preview image**: ❌ None — GitHub generates a generic OG image from the repo stats
- **Stars**: 0
- **Language**: "Python" detected automatically

**Impact**: When this repo appears in GitHub search results, it shows as:
> `mohitmishra786/repo2video` — No description, website, or topics provided.

This means:
- Zero clues about what the project does in search results
- No keyword relevance signals for GitHub's internal search
- No hyperlink to any landing page or demo
- No badge visibility (stars, forks) to trigger social proof

### README SEO
Current README (`README.md`, 128 lines) issues:
- **Placeholder URLs**: `git clone https://github.com/yourusername/RepoToVideo.git` (lines 20, 91) — any visitor who actually tries to clone gets a 404
- **Empty Configuration section**: Shows JSON config snippets that don't correspond to any actual implementation
- **No demo GIF or screenshot**: The most important SEO asset for a tool that *makes videos* — missing
- **No badges**: No build status, PyPI version, license, or star badges
- **No "Try it now" or "Live demo" link**: No way to see the tool working without cloning
- **Generic feature list**: "Efficiently clones and processes" / "Advanced parsing" — zero specificity
- **No comparison table or why-us section**: Doesn't differentiate from alternatives
- **"Contact" section links to placeholder**: `https://github.com/yourusername/RepoToVideo/issues`

### External Web Presence
Web search for "repo2video" and "RepoToVideo" returns:
- The GitHub repo itself
- **No external mentions** on Reddit, Hacker News, Twitter/X, Product Hunt, dev.to, blogs, or tutorial sites
- The name "RepoToVideo" is **competing with** (and losing to) "Repoclip" (launched Feb 2026, has blog/tutorial coverage, Show HN thread with 200+ points)
- **Zero organic keyword rankings** for any search term. The tool has never been indexed by Google for any competitive keyword.

### Landing Page
**No landing page exists.** Options:
- `repotovideo.com` — unverified; likely not registered
- `repotovideo.ai` — unverified
- No GitHub Pages site (`mohitmishra786.github.io/repo2video`)
- No Vercel/Netlify deployment

### Name Confusion
Critical branding/SEO issue: **The GitHub repo is named `repo2video`, but the README calls it `RepoToVideo`**. These are different strings for search engines:
- GitHub URL: `github.com/mohitmishra786/repo2video`
- README title: `RepoToVideo`
- Internal code references: `RepoToVideo` (class names, imports)
- Install command uses: `RepoToVideo` (directory name in clone URL)

This split means:
- SEO effort is split between two names
- GitHub search and Google may index one name while users search for the other
- Any backlinks or mentions will be fractured
- The README's clone URL (`yourusername/RepoToVideo.git`) matches neither the actual repo name nor the display name

### Competitor SEO Positioning
| Competitor | GitHub Description | Topics Set | Website | Has Blog |
|------------|-------------------|-----------|---------|----------|
| **RepoClip** | "Turn any GitHub repo into a demo video in 60 seconds" | ✅ Yes | ✅ repoclip.io | ✅ Blog + Show HN |
| **RepoToViralVideo** | "Turn any GitHub repository into a promo video in one-click" | ✅ Yes | ❌ No | ❌ But README is comprehensive |
| **repo-explainer** | "Auto-generate 30s explainer videos from any git repo" | ✅ Yes | ❌ No | ❌ |
| **Repodcast** | "Turn GitHub repos into narrated tech videos" | ✅ Yes | ❌ No | ✅ Technical blog post |
| **Repo2Video** | **Empty** | **None** | **None** | **None** |

## 2. GAPS & RISKS

| Severity | Issue |
|----------|-------|
| **P0** | **No repo description, topics, or website URL set on GitHub.** These are free, 5-minute fixes that would massively improve discoverability. |
| **P0** | **Name confusion between repo2video / RepoToVideo.** SEO effort is split. Pick one name and standardize. |
| **P1** | **Placeholder clone URLs in README.** Anyone landing on the repo who tries to clone gets a 404 error. This is a first-impression catastrophe. |
| **P1** | **No demo GIF or video.** For a video-generating tool, a static README is a terrible advertisement. |
| **P1** | **No external presence anywhere.** Zero mentions, zero backlinks, zero social proof. |
| **P2** | **No landing page or website.** Even a single-page GitHub Pages site would help with SEO and credibility. |
| **P2** | **No badges in README.** Star count (0), license, build status — these are social signals that affect click-through. |
| **P2** | **No `awesome-list` presence.** Not listed in any relevant GitHub topic or awesome list. |

## 3. BENCHMARK — Best Practices (2026)

Based on analysis of successful OSS dev-tool repos (Gingiris playbook, LaunchPact research, multiple Show HN case studies):
1. **README must have a demo GIF within the first 3 seconds** of scrolling — this is the single highest-ROI SEO asset
2. **GitHub description field** should be a keyword-rich 1-sentence summary: "Generate AI-narrated explainer videos from any GitHub repository — paste a URL, get a 1080p MP4 with code walkthrough, animations, and voiceover"
3. **Topics** on GitHub are now a primary discovery surface: `repo-to-video`, `code-to-video`, `explainer-video`, `ai-video-generator`, `developer-tools`, `python`, `streamlit`, `manim`, `animation`
4. **Star-button psychology** (from Gingiris playbook): The star button should be visually prominent, and the README should include a "Star if you find this useful" prompt with context
5. **Social preview image** should be set via `.github/social-preview.png` or GitHub repo settings

## 4. CHECKLIST

### P0 — Launch-Blocking
- [ ] **Add repo description** on GitHub: "Generate AI-narrated explainer videos from any GitHub repository — paste a URL, get a video." [5 min]
- [ ] **Add repo topics** on GitHub: `repo-to-video`, `code-to-video`, `explainer-video`, `ai-video-generator`, `developer-tools`, `python`, `open-source`, `manim` [5 min]
- [ ] **Set website URL** on GitHub to wherever the project lives (GitHub Pages, or skip for now). [5 min]
- [ ] **Fix placeholder URLs in README** — change `yourusername/RepoToVideo.git` to `mohitmishra786/repo2video.git`. [5 min]
- [ ] **Resolve name confusion** — pick one name (recommend `repo2video` for GitHub consistency) and use it everywhere. [S effort]

### P1 — Pre-Launch
- [ ] **Create a demo GIF** of the tool working (even a CLI demo) and add it to the README. [M effort]
- [ ] **Add README badges**: GitHub stars, license, Python version, dependencies status. [S effort]
- [ ] **Set GitHub social preview image** (`og:image`) to something compelling. [S effort]
- [ ] **Create a GitHub Pages landing page** with tool description, demo, and install instructions. [M effort]

### P2 — Ongoing
- [ ] **Write and publish a "How I Built This" blog post** on dev.to/Hashnode. [M effort]
- [ ] **Submit to awesome lists** — `awesome-python`, `awesome-developer-tools`, etc. [S effort]
- [ ] **Create a product listing on SaaSHub** for long-tail SEO. [S effort]
- [ ] **Add an `og:image` and `og:description`** meta tags via a landing page. [S effort]

## 5. OPEN QUESTIONS

1. **Is the author aware that `yourusername/RepoToVideo.git` is still in the README?** This is the kind of template artifact that suggests the README was never reviewed after scaffolding.
2. **Is `repotovideo.com` domain available?** Register it immediately if so — $12/year for massive credibility gain.
3. **Is the name `RepoToVideo` or `repo2video`?** This needs a deliberate decision. The GitHub name `repo2video` is concise and searchable. `RepoToVideo` is more readable. Pick one.
