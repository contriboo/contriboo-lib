from dataclasses import dataclass
from datetime import datetime
from typing import Literal

from contriboo.repository_name import RepositoryName


@dataclass(frozen=True, slots=True)
class CommitSignature:
    """Author/committer identity snapshot for one commit.

    Attributes:
        author_email: Author email from commit metadata.
        author_name: Author name from commit metadata.
        committer_email: Committer email from commit metadata.
        committer_name: Committer name from commit metadata.
    """

    author_email: str
    author_name: str
    committer_email: str
    committer_name: str


@dataclass(frozen=True, slots=True)
class RepositoryCommitCount:
    """Per-repository commit counting result.

    Attributes:
        full_name: Repository identifier in `owner/repo` form.
        branch: Branch used for counting (`main`/`master`) or `None`.
        commit_count: Number of matching commits in this repository.
        status: Processing status (`ok` or `skipped`).
        error: Optional error/skip description.
    """

    full_name: RepositoryName
    branch: str | None
    commit_count: int
    status: Literal["ok", "skipped"]
    error: str | None = None


@dataclass(frozen=True, slots=True)
class ProfileCommitCountResult:
    """Aggregated commit-count result for one profile query.

    Attributes:
        total_commits: Sum of matching commits across scanned repositories.
        repos_scanned: Number of repositories attempted for scan.
        repos_skipped: Number of repositories skipped due to errors/branch absence.
        started_at: UTC timestamp when counting started.
        finished_at: UTC timestamp when counting finished.
        repo_results: Per-repository counting results.
    """

    total_commits: int
    repos_scanned: int
    repos_skipped: int
    started_at: datetime
    finished_at: datetime
    repo_results: tuple[RepositoryCommitCount, ...]
