import subprocess
from pathlib import Path
from typing import Iterable

from contriboo.exceptions import GitOperationError, GitOperationTimeoutError
from contriboo.profile.interfaces import GitHistoryGateway
from contriboo.profile.models import CommitSignature
from contriboo.repository_name import RepositoryName


class GitGateway(GitHistoryGateway):
    __slots__ = ("_git_timeout_sec",)

    def __init__(self, git_timeout_sec: int) -> None:
        self._git_timeout_sec = git_timeout_sec

    def clone_repository(
        self, repository_full_name: RepositoryName, target_root: Path
    ) -> Path:
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
        if self._has_branch(repository_dir, "main"):
            return "main"
        if self._has_branch(repository_dir, "master"):
            return "master"
        return None

    def iter_commit_signatures(
        self, repository_dir: Path, branch: str
    ) -> Iterable[CommitSignature]:
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
        try:
            self._run(
                ["git", "rev-parse", "--verify", f"origin/{branch}"], cwd=repository_dir
            )
            return True
        except GitOperationError:
            return False

    def _run(self, command: list[str], cwd: Path | None = None) -> str:
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
