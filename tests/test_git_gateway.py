from pathlib import Path

from contriboo.integrations.git.subprocess_gateway import SubprocessGitHistoryGateway


def test_clone_repository_calls_git_clone(monkeypatch, tmp_path: Path) -> None:
    commands: list[list[str]] = []

    def fake_run(self: SubprocessGitHistoryGateway, command: list[str], cwd: Path | None = None) -> str:
        commands.append(command)
        return ""

    monkeypatch.setattr(SubprocessGitHistoryGateway, "_SubprocessGitHistoryGateway__run", fake_run)

    gateway = SubprocessGitHistoryGateway(git_timeout_sec=120)
    repo_dir = gateway.clone_repository("owner/repo", tmp_path)

    assert repo_dir == tmp_path / "owner__repo"
    assert commands[0][:4] == ["git", "clone", "--filter=blob:none", "--no-checkout"]


def test_iter_commit_signatures_parses_expected_format(monkeypatch) -> None:
    def fake_run(self: SubprocessGitHistoryGateway, command: list[str], cwd: Path | None = None) -> str:
        if command[:3] == ["git", "rev-parse", "--verify"]:
            return "ok"
        if command[:2] == ["git", "log"]:
            return "john@example.com\x1fjohn\x1fjohn@example.com\x1fjohn"
        raise RuntimeError("unexpected")

    monkeypatch.setattr(SubprocessGitHistoryGateway, "_SubprocessGitHistoryGateway__run", fake_run)

    gateway = SubprocessGitHistoryGateway(git_timeout_sec=120)
    branch = gateway.resolve_mainline_branch(Path("/tmp/repo"))
    signatures = list(gateway.iter_commit_signatures(Path("/tmp/repo"), branch or "main"))

    assert branch == "main"
    assert len(signatures) == 1
    assert signatures[0].author_name == "john"
