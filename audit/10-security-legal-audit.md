# Security, Legal & Compliance Audit

## 1. CURRENT STATE

### Arbitrary Code Analysis/Execution Risk 🔴

**This is the single most serious non-functional risk in the project, specific to its core purpose.**

The tool's primary function — analyzing arbitrary GitHub repositories — inherently involves processing untrusted code. The codebase does this in two ways:

1. **Static Analysis (repo_fetcher.py + code_analysis.py)**: Reads file contents from cloned repos and processes them with AST parsing, regex pattern matching, and string operations. This is relatively safe — Python's `ast.parse()` is memory-safe, and regex/string operations on untrusted input are generally bounded in risk.

2. **Dynamic Execution (aspirational, execution_capture.py)**: The E2B sandbox integration (`_capture_python_execution`) is designed to **execute arbitrary code from repos inside a sandbox**. While the sandbox is intended to isolate execution, the current implementation has concerning aspects:
   - The E2B sandbox is **optional and aspirational** — when E2B is not available, `_simulate_execution_trace()` runs in-process with **zero isolation** using `ast.walk()` to generate synthetic traces. This doesn't actually execute code, so it's safe — but it produces fake data.
   - If E2B were enabled, code from untrusted repos would be executed in E2B's managed sandbox. E2B's security model is reasonable, but the project doesn't validate or filter what gets executed.
   - The sandbox warning in USAGE_GUIDE.md states "No network access from executed code" — but this is E2B's guarantee, not the project's.

3. **Content Sanitization (repo_fetcher.py, line 248-277)**: The `_sanitize_sensitive_content()` method attempts to redact emails, secrets, API keys, and credit card numbers from fetched file content. However:
   - The regex patterns are simplistic (e.g., `\b[A-Za-z0-9]{32,}\b` for hashes — this would catch many legitimate identifiers)
   - URL redaction pattern `\b(?:https?://)?(?:www\.)?([a-zA-Z0-9-]+\.[a-zA-Z]{2,})(?:/[^\s]*)?\b` is too broad — would redact legitimate GitHub URLs, imports, and references
   - The credit card regex is unnecessary and potentially risky (processing PCI data you don't need)
   - **This sanitization is applied BEFORE storing file content, meaning legitimate URLs needed for code analysis may be destroyed**
   - Sanitization is only applied to files < 1MB — larger files bypass it entirely

### API Key Handling
- **ElevenLabs key**: Read from environment variable `ELEVENLABS_API_KEY` via `os.getenv()` in `audio_generator.py`. Standard practice. No logging of keys detected.
- **Groq/OpenAI keys**: Read from environment via `langchain` configuration. Standard practice.
- **E2B key**: Read from `E2B_API_KEY` environment variable.
- **No `.env` file in repo**: The `.env` file is correctly gitignored.
- **config.env creation**: `setup.py` creates a `config.env` file with placeholder tokens. The comment says "Never commit API keys to version control" — good.
- **Risk**: Low. API keys are handled via environment variables. No hardcoded keys found.

### License Compatibility of Bundled Assets
- **Project license**: MIT (LICENSE file present).
- **Third-party audio/animation assets**: None detected. The background music generator creates its own audio (white noise with low-pass filter via pydub). No bundled font files, no bundled sound effects, no bundled images.
- **Third-party code dependencies**: All PyPI packages listed in requirements.txt have permissive licenses (MIT, Apache 2.0, BSD) by inspection. No copyleft dependencies detected.
- **Risk**: Low. No bundled third-party assets to worry about.

### GDPR/Privacy
- **No user data collection**: The project currently collects nothing — no accounts, no telemetry, no analytics persistence.
- **`AnalyticsManager` in `logging_config.py`**: Tracks in-memory only with no persistence. If made persistent in future, it would need:
  - GDPR-compliant privacy policy
  - Data processing disclosure
  - Right to deletion mechanism
  - Cookie/consent banner on any web UI
- **Risk**: Low currently. Would become Medium if the analytics system is completed and deployed without privacy considerations.

### Git Credentials
- `repo_fetcher.py` accepts a `github_token` parameter. If users provide tokens with broad scopes, and if logging accidentally captures the token, this could be a credential leak.
- The `PyGithub` library is used with or without a token (unauthenticated access for public repos). Token is passed to `Github(github_token)` constructor, which stores it in the object. If the `RepoFetcher` instance is serialized or logged, the token could leak.

## 2. GAPS & RISKS (Ranked by Severity)

| Severity | Issue |
|----------|-------|
| **P0** | **No code execution isolation when E2B is unavailable.** The simulation path runs in-process. While it doesn't execute code, if someone adds actual code execution without proper sandboxing, this becomes a critical RCE vulnerability. **Current risk: Low. Future risk: Critical.** |
| **P0** | **Content sanitization destroys legitimate data.** The overly broad regex patterns (URLs, hashes) will redact code content needed for analysis. The URL pattern would match `api.github.com`, `pypi.org`, and valid import paths. |
| **P1** | **Credit card detection regex is unnecessary liability.** Scanning third-party code for credit card numbers creates PCI scope considerations unnecessarily. Even storing redacted CC patterns in memory could be problematic. |
| **P1** | **No input validation for repo content size.** The tool will attempt to clone and analyze arbitrarily large repos. A malicious user could point the tool at a 10GB repo and cause OOM/crash. |
| **P2** | **No timeout for API calls.** GitHub API calls in `repo_fetcher.py` have no timeout set on the `requests` calls (Bitbucket path, line 213). |
| **P2** | **No explicit security policy** (`SECURITY.md`). If a vulnerability is found, there's no disclosure channel. |
| **P2** | **License copyright holder mismatch.** LICENSE says "Copyright (c) 2025 chessMan" but the GitHub account is "mohitmishra786." Minor but worth clarifying. |

## 3. BENCHMARK

| Practice | Repo2Video | Best Practice |
|----------|-----------|---------------|
| Code execution sandbox | Aspirational (E2B) | ✅ Mandatory for any dynamic analysis tool |
| Content sanitization | Overly broad regex | ✅ Context-aware filtering with allowlists |
| API key storage | Environment variables | ✅ Standard practice |
| Security policy | ❌ None | ✅ SECURITY.md with disclosure contact |
| Input size limits | ❌ None | ✅ Repo size limits + timeout |
| Docker isolation | ❌ None | ✅ Optional for self-hosting |
| Vulnerability disclosure | ❌ None | ✅ security.txt or SECURITY.md |

## 4. CHECKLIST

### P0 — Fix Before Launch
- [ ] **Address content sanitization overreach**: Fix regex patterns in `_sanitize_sensitive_content()` to not destroy legitimate code content. Remove the URL redaction pattern entirely (unnecessary). [M effort]
- [ ] **Remove CC number detection regex**: Unnecessary liability. PCI scope is not something a dev tool should touch. [S effort]
- [ ] **Add repo size limits**: Reject repos > 100MB for analysis (configurable). [S effort]

### P1 — Important
- [ ] **Add timeout to all HTTP requests**: `requests.get()` calls have no timeout. Set 30s default. [S effort]
- [ ] **Add warning in README**: Explicitly state that the tool processes code from untrusted sources and advise using it only on repos you trust. [S effort]
- [ ] **Add input validation for E2B execution path**: If E2B integration is completed, ensure code is executed in a properly isolated sandbox with network restrictions. [M effort]

### P2 — Nice to Have
- [ ] **Add SECURITY.md** with vulnerability disclosure contact. [S effort]
- [ ] **Clarify license copyright**: Update LICENSE to use the founder's actual name. [S effort]
- [ ] **Add a `--dry-run` flag**: Allow users to see what the tool would do without actually cloning or analyzing repos. [M effort]
- [ ] **Add Dockerfile**: Running inside a container provides OS-level isolation for repo processing. [M effort]

## 5. OPEN QUESTIONS

1. **Is E2B sandboxing planned to be the primary execution isolation mechanism?** Or is there intent to support other sandboxes (Docker, Firecracker, gVisor)?
2. **Has a security review been done on the PyGithub usage?** The token is stored in the RepoFetcher instance — if that object is serialized (e.g., for caching), the token leaks.
3. **What's the plan for handling malicious repos?** A repo could contain: a billion files (zip bomb), a crashing parser, or code that exploits the analysis system. There's currently no defense.
