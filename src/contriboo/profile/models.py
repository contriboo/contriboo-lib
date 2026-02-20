from dataclasses import dataclass
from datetime import datetime
from typing import Literal

from contriboo.repository_name import RepositoryName


@dataclass(frozen=True, slots=True)
class CommitSignature:
    author_email: str
    author_name: str
    committer_email: str
    committer_name: str


@dataclass(frozen=True, slots=True)
class RepositoryCommitCount:
    full_name: RepositoryName
    branch: str | None
    commit_count: int
    status: Literal["ok", "skipped"]
    error: str | None = None


@dataclass(frozen=True, slots=True)
class ProfileCommitCountResult:
    total_commits: int
    repos_scanned: int
    repos_skipped: int
    started_at: datetime
    finished_at: datetime
    repo_results: tuple[RepositoryCommitCount, ...]
