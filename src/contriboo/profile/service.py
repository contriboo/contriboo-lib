import datetime
import tempfile
from pathlib import Path

from contriboo.exceptions import InvalidDaysRangeError
from contriboo.repository_name import RepositoryName

from .interfaces import GitHistoryGateway, ProfileRepositoryProvider
from .models import ProfileCommitCountResult, RepositoryCommitCount
from .types import DaysRange


class ProfileAnalysisService:
    __slots__ = ("_repository_provider", "_git_gateway", "_workspace_dir")

    def __init__(
        self,
        repository_provider: ProfileRepositoryProvider,
        git_gateway: GitHistoryGateway,
        workspace_dir: Path | None = None,
    ) -> None:
        self._repository_provider = repository_provider
        self._git_gateway = git_gateway
        self._workspace_dir = workspace_dir

    def count_total_commits(
        self,
        username: str,
        email: str | None,
        days: DaysRange,
        show_progress: bool = False,
    ) -> ProfileCommitCountResult:
        self._validate_days(days)
        started_at = datetime.datetime.now(datetime.UTC)

        repositories = self._repository_provider.find_repositories_for_author(
            username=username,
            days=days,
        )
        if not repositories:
            return self._empty_result(started_at)

        normalized_username, normalized_email = self._normalize_identity(
            username, email
        )
        repo_results = self._scan_repositories(
            repositories=repositories,
            normalized_username=normalized_username,
            normalized_email=normalized_email,
            show_progress=show_progress,
        )
        return self._build_result(started_at, repositories, repo_results)

    def _scan_repositories(
        self,
        repositories: list[RepositoryName],
        normalized_username: str,
        normalized_email: str,
        show_progress: bool,
    ) -> list[RepositoryCommitCount]:
        results: list[RepositoryCommitCount] = []

        with tempfile.TemporaryDirectory(
            prefix="contriboo-", dir=self._workspace_dir
        ) as tmp_dir:
            target_root = Path(tmp_dir)
            total = len(repositories)

            for index, repository_name in enumerate(repositories, start=1):
                if show_progress:
                    print(f"[{index}/{total}] cloning {repository_name} ...")

                result = self._scan_single_repository(
                    repository_name=repository_name,
                    target_root=target_root,
                    normalized_username=normalized_username,
                    normalized_email=normalized_email,
                    index=index,
                    total=total,
                    show_progress=show_progress,
                )
                results.append(result)

        return results

    def _scan_single_repository(
        self,
        repository_name: RepositoryName,
        target_root: Path,
        normalized_username: str,
        normalized_email: str,
        index: int,
        total: int,
        show_progress: bool,
    ) -> RepositoryCommitCount:
        try:
            repo_dir = self._git_gateway.clone_repository(repository_name, target_root)
            branch = self._git_gateway.resolve_mainline_branch(repo_dir)
            if branch is None:
                if show_progress:
                    print(f"[{index}/{total}] skip {repository_name}: no main/master")
                return RepositoryCommitCount(
                    full_name=repository_name,
                    branch=None,
                    commit_count=0,
                    status="skipped",
                    error="main/master branch not found",
                )

            commit_count = self._count_matching_commits(
                repo_dir=repo_dir,
                branch=branch,
                normalized_username=normalized_username,
                normalized_email=normalized_email,
            )
            if show_progress:
                print(f"[{index}/{total}] {repository_name}: +{commit_count}")
            return RepositoryCommitCount(
                full_name=repository_name,
                branch=branch,
                commit_count=commit_count,
                status="ok",
            )
        except Exception as exc:
            if show_progress:
                print(f"[{index}/{total}] skip {repository_name}: {exc}")
            return RepositoryCommitCount(
                full_name=repository_name,
                branch=None,
                commit_count=0,
                status="skipped",
                error=str(exc),
            )

    def _count_matching_commits(
        self,
        repo_dir: Path,
        branch: str,
        normalized_username: str,
        normalized_email: str,
    ) -> int:
        commit_count = 0
        for signature in self._git_gateway.iter_commit_signatures(repo_dir, branch):
            matches_email = normalized_email and (
                signature.author_email == normalized_email
                or signature.committer_email == normalized_email
            )
            if matches_email:
                commit_count += 1
                continue

            matches_username = normalized_username and (
                signature.author_name == normalized_username
                or signature.committer_name == normalized_username
            )
            if matches_username:
                commit_count += 1

        return commit_count

    def _build_result(
        self,
        started_at: datetime.datetime,
        repositories: list[RepositoryName],
        repo_results: list[RepositoryCommitCount],
    ) -> ProfileCommitCountResult:
        finished_at = datetime.datetime.now(datetime.UTC)
        total_commits = sum(item.commit_count for item in repo_results)
        repos_skipped = sum(1 for item in repo_results if item.status == "skipped")

        return ProfileCommitCountResult(
            total_commits=total_commits,
            repos_scanned=len(repositories),
            repos_skipped=repos_skipped,
            started_at=started_at,
            finished_at=finished_at,
            repo_results=tuple(repo_results),
        )

    def _empty_result(self, started_at: datetime.datetime) -> ProfileCommitCountResult:
        finished_at = datetime.datetime.now(datetime.UTC)
        return ProfileCommitCountResult(
            total_commits=0,
            repos_scanned=0,
            repos_skipped=0,
            started_at=started_at,
            finished_at=finished_at,
            repo_results=(),
        )

    def _normalize_identity(self, username: str, email: str | None) -> tuple[str, str]:
        return username.strip().lower(), (email or "").strip().lower()

    def _validate_days(self, days: DaysRange) -> None:
        if days == "all":
            return
        if isinstance(days, bool) or not isinstance(days, int) or days <= 0:
            raise InvalidDaysRangeError("days must be positive int or 'all'")
