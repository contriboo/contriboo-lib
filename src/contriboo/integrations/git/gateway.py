import subprocess
from pathlib import Path
from typing import Iterable

from contriboo.exceptions import GitOperationError, GitOperationTimeoutError
from contriboo.profile.interfaces import GitHistoryGateway
from contriboo.profile.models import CommitSignature
from contriboo.repository_name import RepositoryName


class GitGateway(GitHistoryGateway):
    """Git CLI adapter for clone and history operations."""

    __slots__ = ("_git_timeout_sec",)

    def __init__(self, git_timeout_sec: int) -> None:
        """Initialize gateway.

        Args:
            git_timeout_sec: Timeout for every git command in seconds.
        """
        self._git_timeout_sec = git_timeout_sec

    def clone_repository(
        self, repository_full_name: RepositoryName, target_root: Path
    ) -> Path:
        """Clone repository into target directory.

        Args:
            repository_full_name: Repository identifier (`owner/repo`).
            target_root: Root directory where clone should be created.

        Returns:
            Path: Local path to the cloned repository.
        """
        repository_url = f"https://github.com/{repository_full_name}.git"
        repository_dir = target_root / str(repository_full_name).replace("/", "__")
        self._run(
            [
                "git",
                "clone",
                "--filter=blob:none",
                "--no-checkout",
                repository_url,
                str(repository_dir),
            ]
        )
        return repository_dir

    def resolve_mainline_branch(self, repository_dir: Path) -> str | None:
        """Resolve mainline branch name.

        Args:
            repository_dir: Local repository path.

        Returns:
            str | None: `"main"` or `"master"` when exists, else `None`.
        """
        if self._has_branch(repository_dir, "main"):
            return "main"
        if self._has_branch(repository_dir, "master"):
            return "master"
        return None

    def iter_commit_signatures(
        self, repository_dir: Path, branch: str
    ) -> Iterable[CommitSignature]:
        """Read commit signatures from branch history.

        Args:
            repository_dir: Local repository path.
            branch: Branch name to inspect.

        Returns:
            Iterable[CommitSignature]: Parsed commit signatures.
        """
        raw = self._run(
            [
                "git",
                "log",
                f"origin/{branch}",
                "--pretty=format:%ae%x1f%an%x1f%ce%x1f%cn",
            ],
            cwd=repository_dir,
        )
        if not raw:
            return []

        signatures: list[CommitSignature] = []
        for line in raw.splitlines():
            parts = [part.strip().lower() for part in line.split("\x1f")]
            if len(parts) != 4:
                continue
            signatures.append(
                CommitSignature(
                    author_email=parts[0],
                    author_name=parts[1],
                    committer_email=parts[2],
                    committer_name=parts[3],
                )
            )

        return signatures

    def _has_branch(self, repository_dir: Path, branch: str) -> bool:
        """Check whether remote-tracking branch exists.

        Args:
            repository_dir: Local repository path.
            branch: Branch name to check.

        Returns:
            bool: `True` when branch exists, otherwise `False`.
        """
        try:
            self._run(
                ["git", "rev-parse", "--verify", f"origin/{branch}"], cwd=repository_dir
            )
            return True
        except GitOperationError:
            return False

    def _run(self, command: list[str], cwd: Path | None = None) -> str:
        """Execute git command.

        Args:
            command: Git command arguments.
            cwd: Optional working directory for command execution.

        Returns:
            str: Trimmed stdout output.

        Raises:
            GitOperationTimeoutError: If command exceeds timeout.
            GitOperationError: If command exits with non-zero code.
        """
        try:
            result = subprocess.run(
                command,
                cwd=str(cwd) if cwd else None,
                capture_output=True,
                text=True,
                timeout=self._git_timeout_sec,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            raise GitOperationTimeoutError(
                f"Command timeout after {self._git_timeout_sec}s: {' '.join(command)}"
            ) from exc

        if result.returncode != 0:
            message = (
                result.stderr.strip() or result.stdout.strip() or "Git command failed"
            )
            raise GitOperationError(message)

        return result.stdout.strip()
