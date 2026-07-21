# Monetization Audit

## 1. CURRENT STATE

The project has **no monetization** implemented or even defined. `setup.py` mentions "Premium Features" as a comment stub:
```
# Premium Features (requires license)
PREMIUM_ENABLED=False
PREMIUM_LICENSE_KEY=
```
But no premium features exist in the codebase, no license key validation, no payment integration. The founder has a GitHub Sponsors profile (target: $50/month for educational content), but it's not linked from the repo.

## 2. IS MONETIZATION VIABLE?

### Cost Constraints
The core constraint: **each video generation costs real money in API calls** (Groq/OpenAI for storyboard, ElevenLabs for TTS, potentially Sora/Kling for video clips). If hosted as a SaaS, these costs are non-trivial:
- ElevenLabs TTS: ~$0.001-0.003 per character → ~$0.05-0.15 per 60-second narration
- LLM storyboard generation: ~$0.01-0.10 per repo (varying by model and repo size)
- Video rendering compute: ~$0.05-0.30 per minute (if cloud-hosted)
- **Total per video: ~$0.11-0.55 in direct API costs**

Compare to RepoClip's pricing:
- Free: 2 videos/month (loss leader, likely subsidized)
- Starter ($24/mo): 5 videos → $4.80/video
- Pro ($66/mo): 20 videos → $3.30/video
- Agency ($166/mo): 100 videos → $1.66/video

This suggests ~$1.50-5.00/video is the viable price range for SaaS in this space.

### Market Size
"Repo to video" is a niche within a niche (developer tools → developer marketing tools → repo video generators). The total addressable market in 2026 is likely:
- 10-30M public GitHub repos
- Active maintainers who might want promo videos: ~500K-1M
- Willing to pay: 1-5% → 5K-50K potential customers

**Honest assessment**: This is a small niche. A solo founder can build a lifestyle business ($5-20K/month MRR) but this is not VC-fundable scale. The successful OSS tools in this space (like the examples in the 2026 monetization research) target the top of the funnel for broader developer marketing services.

### Plausible Models

**Model 1: Open Core (OSS + SaaS) — RECOMMENDED**
- **Free/OSS**: Local-only generator with basic rendering (MoviePy + gTTS). Fully open source.
- **Paid Cloud**: Hosted version with better rendering (Remotion), ElevenLabs voices, no setup, faster renders.
- **Pricing**: Inspired by DenchClaw model ($29/mo individual, flat team pricing).
- **Pros**: Conscious-clear monetization, distribution through OSS, conversion on convenience.
- **Cons**: Requires building and operating a cloud rendering service (significant infra investment).

**Model 2: Freemium Feature Gating**
- **Free**: 720p output, watermark, 2 videos/month, gTTS only
- **Paid**: 1080p/4K, no watermark, unlimited videos, ElevenLabs voices, REST API
- **Pros**: Simpler than cloud hosting; everything runs locally
- **Cons**: Hard to enforce feature gates in fully open-source software. Would need a license key system (like Vike's Open Source Pricing model).
- **Note**: Vike's 2026 model uses local asymmetric encryption + heuristics — this could work for Repo2Video too.

**Model 3: API Access**
- **Free**: Self-host locally
- **Paid**: REST API for CI/CD integration (generate videos as part of your release pipeline)
- **Pros**: Developer-friendly, integrates with existing workflows
- **Cons**: Competitive with RepoClip's GitHub Action (which already exists)
- **Inspiration**: RepoClip's `repoclip/generate-video` GitHub Action

**Model 4: GitHub Sponsors / Donations**
- **Likely yield**: $50-200/month based on founder's existing Sponsors profile ($50 goal)
- **Not a primary business model**, but easy to set up with no effort

### What Won't Work
- **Pure donation model**: Produces negligible revenue for dev tools without a large user base
- **Enterprise sales**: No team, no product maturity, no compliance features to justify enterprise pricing
- **Advertising**: Not appropriate for a developer tool
- **Training data licensing**: The app analyzes other people's code — can't license that

## 3. RECOMMENDED PATH (Solo Developer)

**Phase 1 (0-6 months): Free OSS only.**
- Build users. Gather feedback. Don't monetize.
- Set up GitHub Sponsors as a "tip jar" but don't build a business around it.
- The goal is distribution, not revenue.

**Phase 2 (6-12 months): Freemium with license keys.**
- Implement Vike-style local license validation (MIT codebase, npm/package-based license check)
- Paid tier: 1080p, no watermark, ElevenLabs voices, REST API access
- Price: $19/month individual, $49/month team

**Phase 3 (12+ months): Optional hosted cloud service.**
- Only if Phase 2 shows demand and the founder has time to operate infra
- Charge 2-3x cost of API usage + markup

## 4. CHECKLIST

### P2 — Before Launch
- [ ] **Add GitHub Sponsors link** to README. Already have a Sponsors profile — link it. [5 minutes]
- [ ] **Decide on monetization model** — even if it's "free forever, we'll figure it out later." State it in the README. [S effort]

### P2 — Post-Launch
- [ ] **Monitor API costs** from the free tier to understand the per-video economics. [Ongoing]
- [ ] **Wait for users to ask for paid features** before building them. Don't build a monetization system nobody wants. [Ongoing]
- [ ] **If users request cloud hosting**, evaluate DenchClaw-style cloud offering. [L effort]

## 5. OPEN QUESTIONS

1. **Is the goal financial sustainability or just building something cool?** The answer determines the entire monetization strategy.
2. **Would the founder be willing to operate a cloud service?** This requires significantly more operational skill and time than an OSS project.
3. **Is there a B2B use case?** Companies generating internal codebase walkthroughs might pay more than individual developers. This could be the actual market.
