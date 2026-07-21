# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability in Repo2Video, please **do not** open a public GitHub issue.

Instead, report it via:

- **Email**: Create a [private security advisory](https://github.com/mohitmishra786/repo2video/security/advisories/new) on GitHub
- **Alternative**: Contact the maintainer directly through GitHub

We aim to acknowledge reports within 48 hours and provide an initial assessment within 5 business days.

## Security Considerations for Users

Repo2Video analyzes and processes code from GitHub repositories. When using this tool:

1. **Only analyze repositories you trust.** The tool reads and parses arbitrary code, which may contain malicious patterns.
2. **API keys are read from environment variables only.** Never hardcode API keys in configuration files or command-line arguments.
3. **Repository content is processed locally.** Fetched code is stored temporarily on your machine. Sensitive content (emails, API keys) is redacted before storage, but this is best-effort filtering — not a guarantee.
4. **Code execution features (E2B sandbox) are disabled by default.** If enabled, ensure you trust the repository being executed.

## Dependency Security

We recommend running dependency vulnerability scans regularly. For a local scan:

```bash
pip install safety
safety check -r requirements.txt
```

This project does not currently have automated dependency scanning in CI — this is tracked as a planned improvement.
