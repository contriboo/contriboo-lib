from pathlib import Path
from typing import Iterable, Protocol

from contriboo.repository_name import RepositoryName

from .models import CommitSignature
from .types import DaysRange


class ProfileRepositoryProvider(Protocol):
    """Contract for fetching repositories related to one developer profile."""

    def find_repositories_for_author(
        self, username: str, days: DaysRange
    ) -> list[RepositoryName]:
        """Find repositories where author has activity for selected period.

        Args:
            username: GitHub username used in author filtering.
            days: Positive number of days or `"all"` for full history.

        Returns:
            list[RepositoryName]: Unique repository names matching the author filter.
        """
        ...


class GitHistoryGateway(Protocol):
    """Contract for git-history operations over repositories."""

    def clone_repository(
        self, repository_full_name: RepositoryName, target_root: Path
    ) -> Path:
        """Clone repository into target root.

        Args:
            repository_full_name: Repository identifier (`owner/repo`).
            target_root: Directory where repository clone should be created.

        Returns:
            Path: Absolute path to cloned repository directory.
        """
        ...

    def resolve_mainline_branch(self, repository_dir: Path) -> str | None:
        """Resolve repository mainline branch.

        Args:
            repository_dir: Local path to cloned repository.

        Returns:
            str | None: `"main"` or `"master"` when found, otherwise `None`.
        """
        ...

    def iter_commit_signatures(
        self, repository_dir: Path, branch: str
    ) -> Iterable[CommitSignature]:
        """Iterate commit signatures for selected branch.

        Args:
            repository_dir: Local path to cloned repository.
            branch: Branch name used to read commit history.

        Returns:
            Iterable[CommitSignature]: Stream of commit author/committer signatures.
        """
        ...
