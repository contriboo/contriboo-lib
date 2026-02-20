from pathlib import Path

from pytest import MonkeyPatch

from contriboo.exceptions import GitOperationError
from contriboo.integrations.git.gateway import GitGateway
from contriboo.repository_name import RepositoryName


def test_clone_repository_calls_git_clone(
    monkeypatch: MonkeyPatch, tmp_path: Path
) -> None:
    commands: list[list[str]] = []

    def fake_run(self: GitGateway, command: list[str], cwd: Path | None = None) -> str:
        commands.append(command)
        return ""

    monkeypatch.setattr(GitGateway, "_run", fake_run)

    gateway = GitGateway(git_timeout_sec=120)
    repo_dir = gateway.clone_repository(RepositoryName.parse("owner/repo"), tmp_path)

    assert repo_dir == tmp_path / "owner__repo"
    assert commands[0][:4] == ["git", "clone", "--filter=blob:none", "--no-checkout"]


def test_iter_commit_signatures_parses_expected_format(
    monkeypatch: MonkeyPatch,
) -> None:
    def fake_run(self: GitGateway, command: list[str], cwd: Path | None = None) -> str:
        if command[:3] == ["git", "rev-parse", "--verify"]:
            return "ok"
        if command[:2] == ["git", "log"]:
            return "john@example.com\x1fjohn\x1fjohn@example.com\x1fjohn"
        raise GitOperationError("unexpected")

    monkeypatch.setattr(GitGateway, "_run", fake_run)

    gateway = GitGateway(git_timeout_sec=120)
    branch = gateway.resolve_mainline_branch(Path("/tmp/repo"))
    signatures = list(
        gateway.iter_commit_signatures(Path("/tmp/repo"), branch or "main")
    )

    assert branch == "main"
    assert len(signatures) == 1
    assert signatures[0].author_name == "john"
