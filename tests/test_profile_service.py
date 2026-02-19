from pathlib import Path

from contriboo.profile.models import CommitSignature
from contriboo.profile.service import ProfileAnalysisService


class FakeRepositoryProvider:
    def __init__(self, repositories: list[str]) -> None:
        self._repositories = repositories

    def find_repositories_for_author(self, username: str, days: int) -> list[str]:
        return list(self._repositories)


class FakeGitGateway:
    def __init__(self, fail_repository: str | None = None) -> None:
        self._fail_repository = fail_repository

    def clone_repository(self, repository_full_name: str, target_root: Path) -> Path:
        if repository_full_name == self._fail_repository:
            raise RuntimeError("clone failed")
        return target_root / repository_full_name.replace("/", "__")

    def resolve_mainline_branch(self, repository_dir: Path) -> str | None:
        if repository_dir.name.endswith("repo3"):
            return None
        return "main"

    def iter_commit_signatures(self, repository_dir: Path, branch: str) -> list[CommitSignature]:
        if repository_dir.name.endswith("repo1"):
            return [
                CommitSignature("john@example.com", "john", "john@example.com", "john"),
                CommitSignature("x@example.com", "octocat", "x@example.com", "octocat"),
            ]
        return [CommitSignature("none@example.com", "none", "none@example.com", "none")]


def test_count_total_commits_returns_structured_result() -> None:
    service = ProfileAnalysisService(
        repository_provider=FakeRepositoryProvider(["a/repo1", "a/repo2", "a/repo3"]),
        git_gateway=FakeGitGateway(fail_repository="a/repo2"),
    )

    result = service.count_total_commits(
        username="octocat",
        email="john@example.com",
        days=30,
        show_progress=False,
    )

    assert result.total_commits == 2
    assert result.repos_scanned == 3
    assert result.repos_skipped == 2
    assert len(result.repo_results) == 3


def test_count_total_commits_validates_days() -> None:
    service = ProfileAnalysisService(
        repository_provider=FakeRepositoryProvider([]),
        git_gateway=FakeGitGateway(),
    )

    try:
        service.count_total_commits(username="octocat", email=None, days=0)
        assert False, "expected ValueError"
    except ValueError as exc:
        assert "days" in str(exc)
