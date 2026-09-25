"""Unit tests for repo_fetcher network paths — all network calls mocked.

No test in this module touches the real GitHub/GitLab/Bitbucket APIs.
"""

import os
import sys
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from github.Repository import Repository
from repo_fetcher import RepoFetcher


def _mock_repo(size_mb: float = 1.0):
    repo = MagicMock()
    repo.size = int(size_mb * 1024)  # GitHub API reports size in KB
    repo.name = "sample"
    repo.owner.login = "someone"
    return repo


class TestFetchRepoGitHub:
    def test_fetch_returns_repo(self):
        fetcher = RepoFetcher()
        mock_repo = _mock_repo()
        fetcher.github = MagicMock()
        fetcher.github.get_repo.return_value = mock_repo

        result = fetcher.fetch_repo("https://github.com/someone/sample")
        assert result is mock_repo
        fetcher.github.get_repo.assert_called_once_with("someone/sample")

    def test_oversized_repo_rejected(self):
        fetcher = RepoFetcher(max_repo_size_mb=10)
        fetcher.github = MagicMock()
        fetcher.github.get_repo.return_value = _mock_repo(size_mb=50)

        with pytest.raises(ValueError, match="too large"):
            fetcher.fetch_repo("https://github.com/someone/huge")

    def test_custom_size_limit_accepted(self):
        fetcher = RepoFetcher(max_repo_size_mb=100)
        fetcher.github = MagicMock()
        mock_repo = _mock_repo(size_mb=50)
        fetcher.github.get_repo.return_value = mock_repo

        assert fetcher.fetch_repo("https://github.com/someone/ok") is mock_repo


class TestFetchRepoGitLabBitbucket:
    def test_gitlab_without_token_raises(self):
        fetcher = RepoFetcher()
        with pytest.raises(ValueError, match="GitLab token"):
            fetcher.fetch_repo("https://gitlab.com/someone/sample")

    def test_bitbucket_without_token_raises(self):
        fetcher = RepoFetcher()
        with pytest.raises(ValueError, match="Bitbucket token"):
            fetcher.fetch_repo("https://bitbucket.org/someone/sample")


class TestGetRepoContents:
    def _mock_content_file(self, name, content, size=100):
        item = MagicMock()
        item.type = "file"
        item.name = name
        item.path = name
        item.size = size
        if isinstance(content, bytes):
            item.decoded_content = content
        else:
            item.decoded_content = content.encode("utf-8")
        return item

    def test_contents_fetched_and_sanitized(self):
        fetcher = RepoFetcher()
        mock_repo = MagicMock(spec=Repository)
        mock_repo.get_contents.return_value = [
            self._mock_content_file("main.py", "x = 1\ncontact dev@example.com\n")
        ]

        contents = fetcher.get_repo_contents(mock_repo)
        assert len(contents) == 1
        assert contents[0]["name"] == "main.py"
        assert "[EMAIL_REDACTED]" in contents[0]["content"]
        assert "dev@example.com" not in contents[0]["content"]

    def test_directories_recursed(self):
        fetcher = RepoFetcher()
        mock_repo = MagicMock(spec=Repository)

        root_dir = MagicMock()
        root_dir.type = "dir"
        root_dir.path = "src"

        mock_repo.get_contents.side_effect = [
            [root_dir],
            [self._mock_content_file("util.py", "y = 2\n")],
        ]

        contents = fetcher.get_repo_contents(mock_repo)
        assert [c["name"] for c in contents] == ["util.py"]

    def test_irrelevant_files_skipped(self):
        fetcher = RepoFetcher()
        mock_repo = MagicMock(spec=Repository)
        mock_repo.get_contents.return_value = [
            self._mock_content_file("logo.png", b"\x89PNG", size=8)
        ]

        contents = fetcher.get_repo_contents(mock_repo)
        assert contents == []

    def test_large_files_content_not_fetched(self):
        fetcher = RepoFetcher()
        big = self._mock_content_file("big.py", "x = 1\n", size=2 * 1024 * 1024)
        mock_repo = MagicMock(spec=Repository)
        mock_repo.get_contents.return_value = [big]

        contents = fetcher.get_repo_contents(mock_repo)
        assert contents[0]["content"] is None


class TestBitbucketHttp:
    def test_bitbucket_contents_use_timeout(self):
        fetcher = RepoFetcher(bitbucket_token="tok")
        fetcher._bitbucket_client = MagicMock()
        fetcher._bitbucket_client.repositories.get.return_value = {}

        response = MagicMock()
        response.status_code = 200
        response.json.return_value = {"values": []}

        with patch("repo_fetcher.requests.get", return_value=response) as mock_get:
            fetcher.get_repo_contents({
                "platform": "bitbucket",
                "repo_data": {},
                "owner": "someone",
                "repo_name": "sample",
            })
            assert mock_get.call_args.kwargs.get("timeout") == RepoFetcher.REQUEST_TIMEOUT


class TestRepoMetadata:
    def test_analyze_repo_shape(self):
        fetcher = RepoFetcher()
        mock_repo = _mock_repo()
        mock_repo.description = "a sample"
        mock_repo.default_branch = "main"
        mock_repo.stargazers_count = 3
        mock_repo.forks_count = 1
        mock_repo.language = "Python"
        mock_repo.get_languages.return_value = {"Python": 100}
        mock_repo.get_contents.return_value = []

        result = fetcher.analyze_repo(mock_repo)
        assert result["name"] == "sample"
        assert result["owner"] == "someone"
