"""Unit tests for repo_fetcher module."""

import re
import pytest
from repo_fetcher import RepoFetcher


@pytest.fixture
def fetcher() -> RepoFetcher:
    return RepoFetcher()


class TestSanitization:
    def test_email_redaction(self, fetcher):
        result = fetcher._sanitize_sensitive_content("contact user@example.com", "test.py")
        assert result == "contact [EMAIL_REDACTED]"

    def test_complex_email(self, fetcher):
        result = fetcher._sanitize_sensitive_content("admin@sub.domain.co.uk", "test.py")
        assert result == "[EMAIL_REDACTED]"

    def test_url_preserved(self, fetcher):
        result = fetcher._sanitize_sensitive_content("import from https://pypi.org/project/requests", "test.py")
        assert "https://pypi.org" in result

    def test_api_key_redacted(self, fetcher):
        result = fetcher._sanitize_sensitive_content('api_key: "sk-abc123def456"', "config.py")
        assert "[SECRET_REDACTED]" in result
        assert "sk-abc123def456" not in result

    def test_token_redacted(self, fetcher):
        result = fetcher._sanitize_sensitive_content('token = "ghp_1234567890abcdef"', "config.py")
        assert "[SECRET_REDACTED]" in result

    def test_password_redacted(self, fetcher):
        result = fetcher._sanitize_sensitive_content('password: "s3cr3t!"', "config.py")
        assert "[SECRET_REDACTED]" in result

    def test_auth_token_redacted(self, fetcher):
        result = fetcher._sanitize_sensitive_content('auth_token = "tok_abc123"', "config.py")
        assert "[SECRET_REDACTED]" in result

    def test_access_key_redacted(self, fetcher):
        result = fetcher._sanitize_sensitive_content('access_key: "AKIA1234567890ABCD"', "config.py")
        assert "[SECRET_REDACTED]" in result

    def test_phone_preserved(self, fetcher):
        result = fetcher._sanitize_sensitive_content("call 555-123-4567", "test.py")
        assert "555-123-4567" in result

    def test_credit_card_preserved(self, fetcher):
        result = fetcher._sanitize_sensitive_content("4111111111111111", "test.py")
        assert "4111111111111111" in result

    def test_hash_preserved(self, fetcher):
        result = fetcher._sanitize_sensitive_content("a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4", "test.py")
        assert "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4" in result

    def test_readme_skip(self, fetcher):
        result = fetcher._sanitize_sensitive_content("user@example.com", "README.md")
        assert "user@example.com" in result

    def test_secret_single_quotes(self, fetcher):
        result = fetcher._sanitize_sensitive_content("secret: 'abc123'", "config.py")
        assert "[SECRET_REDACTED]" in result


class TestRepoValidation:
    def test_valid_github_url(self, fetcher):
        valid, platform, owner, repo = fetcher.validate_repo_url("https://github.com/user/repo")
        assert valid
        assert platform == "github"
        assert owner == "user"
        assert repo == "repo"

    def test_github_url_with_git_suffix(self, fetcher):
        valid, platform, owner, repo = fetcher.validate_repo_url("https://github.com/user/repo.git")
        assert valid
        assert repo == "repo"

    def test_invalid_url(self, fetcher):
        valid, _, _, _ = fetcher.validate_repo_url("https://notgithub.com/user/repo")
        assert not valid

    def test_gitlab_url(self, fetcher):
        valid, platform, owner, repo = fetcher.validate_repo_url("https://gitlab.com/user/repo")
        assert valid
        assert platform == "gitlab"

    def test_bitbucket_url(self, fetcher):
        valid, platform, owner, repo = fetcher.validate_repo_url("https://bitbucket.org/user/repo")
        assert valid
        assert platform == "bitbucket"


class TestFileFiltering:
    def test_relevant_python_file(self, fetcher):
        assert fetcher._is_relevant_file("main.py")

    def test_relevant_js_file(self, fetcher):
        assert fetcher._is_relevant_file("index.js")

    def test_irrelevant_file(self, fetcher):
        assert not fetcher._is_relevant_file("image.png")

    def test_readme_file(self, fetcher):
        assert fetcher._is_relevant_file("README")


class TestSizeLimits:
    def test_default_max_size(self):
        f = RepoFetcher()
        assert f.max_repo_size_mb == 100

    def test_custom_max_size(self):
        f = RepoFetcher(max_repo_size_mb=50)
        assert f.max_repo_size_mb == 50

    def test_zero_size_allowed(self):
        f = RepoFetcher(max_repo_size_mb=0)
        assert f.max_repo_size_mb == 0


class TestRequestTimeout:
    def test_default_timeout(self, fetcher):
        assert fetcher.REQUEST_TIMEOUT == 30
