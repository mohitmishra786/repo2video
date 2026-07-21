# Monetization Analysis for repo2video

## Recommendation: Open Core Model

After analyzing 4 viable monetization models against the constraints of a solo developer building an open-source dev tool, **Open Core** is the recommended approach. Here's the analysis:

## Models Compared

### 1. Open Core (Recommended)

**How it works**: The OSS local version stays free forever. A cloud-hosted SaaS version offers convenience (no install, faster renders, premium TTS voices, no FFmpeg setup).

**Why it wins**:
- **Zero friction for OSS adoption**: Users clone, install, run locally — no paywall, no registration. Maximizes GitHub stars, word-of-mouth, and community contributions.
- **Natural upgrade path**: Users who love the tool but hate managing dependencies pay for cloud convenience. The conversion is organic, not forced.
- **No license key DRM**: No need to build/maintain license validation. The OSS code IS the free tier.
- **Revenue aligns with costs**: Cloud rendering costs real compute money. Cloud users pay for what they consume.
- **Proven by successful OSS tools**: GitLab, Sentry, Plausible, Supabase all use this model.

**Risks**: Requires building and operating a cloud rendering service (significant infra/ops investment). Not urgent — can wait until there's demonstrated demand.

### 2. Freemium (Rejected)

**How it works**: Free tier with limited features (720p, watermark, 2 videos/month, gTTS only). Paid tier unlocks 1080p/4K, no watermark, unlimited videos, ElevenLabs voices.

**Why rejected**:
- **Hard to enforce in OSS**: Users can fork the code and remove feature gates. Requires license key DRM (like Vike's model) which adds complexity.
- **Bad OSS community vibe**: Feature-gating open source feels hostile. Users expect OSS to be fully featured.
- **Support burden**: Free tier generates support requests without revenue to fund them.

### 3. API Access (Future Add-on)

**How it works**: REST API for CI/CD integration. Free self-host + paid API endpoint for automated video generation in CI pipelines.

**Why deferred**: This is complementary to Open Core, not instead of it. Add it after the cloud SaaS is validated. Competitor RepoClip already has a GitHub Action for this use case.

### 4. Donations Only (Rejected as Primary)

**How it works**: GitHub Sponsors + "buy me a coffee" links. No paywall, no premium features.

**Why rejected as primary model**:
- **Negligible revenue**: Typical yield is $50-200/month even for popular OSS tools with thousands of users.
- **Unsustainable**: API costs (LLM, TTS, cloud rendering) can't be covered by donations.
- **No growth flywheel**: Revenue doesn't scale with usage. More users = more costs, same revenue.

## Recommended Phased Approach

### Phase 1: Free + Sponsors (Now)
- Fully free OSS local tool
- GitHub Sponsors link in README
- Discord community for support
- Goal: 100+ GitHub stars, 50+ active users

### Phase 2: Cloud SaaS (6-12 months)
- Trigger: Users asking for cloud hosting or complaining about local setup
- Offer: Web-based rendering, no install, premium TTS, faster renders
- Pricing: $19/mo individual, $49/mo team (inspired by DenchClaw)
- Cost per video: ~$0.10-0.30 in API+compute costs
- Breakeven: ~5-10 paid users

### Phase 3: API + Enterprise (12+ months)
- REST API for CI/CD integration
- Team management, usage analytics
- Custom voice/model selection
- Pricing: Usage-based or flat team tiers

## Why Not Ads or Data Monetization
- **Ads**: Completely inappropriate for a developer tool. Destroys trust.
- **Training data**: The tool analyzes public repos, not user data. Nothing proprietary to sell.
- **Enterprise sales**: No team, no compliance certs, no sales pipeline — not realistic for a solo dev.

## Summary

Open Core is the highest-probability path to sustainable revenue while preserving the open-source ethos that differentiates repo2video from competitors like RepoClip ($24-166/mo, closed source). The key insight: monetize convenience (cloud hosting), not features.
