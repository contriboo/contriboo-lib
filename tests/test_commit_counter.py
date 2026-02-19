import urllib.error

import contriboo.commit_counter as cc


def test_get_repos_with_activity_collects_unique_repositories(monkeypatch):
    calls = {"n": 0}

    def fake_get(url, token=None):
        calls["n"] += 1
        if calls["n"] == 1:
            return {
                "items": [
                    {"repository": {"full_name": "a/repo1"}},
                    {"repository": {"full_name": "a/repo1"}},
                    {"repository": {"full_name": "b/repo2"}},
                ]
            }
        return {"items": []}

    monkeypatch.setattr(cc, "_github_get", fake_get)

    repos = cc.get_repos_with_activity("octocat", 7, token="x")
    assert sorted(repos) == ["a/repo1", "b/repo2"]


def test_count_in_cloned_repo_filters_by_email_or_username(monkeypatch):
    def fake_pick_branch(repo_dir):
        return "main"

    def fake_run(cmd, cwd=None, timeout_sec=None):
        return """john@x.com|John|john@x.com|John
another@x.com|octocat|another@x.com|octocat
nobody@x.com|NoBody|nobody@x.com|NoBody"""

    monkeypatch.setattr(cc, "_pick_branch", fake_pick_branch)
    monkeypatch.setattr(cc, "_run", fake_run)

    total = cc._count_in_cloned_repo(
        "/tmp/repo", username="octocat", email="john@x.com"
    )
    assert total == 2


def test_get_total_commits_count_sums_repositories_and_skips_errors(monkeypatch):
    def fake_get_repos_with_activity(username, days, token=None):
        return ["a/repo1", "a/repo2", "a/repo3"]

    def fake_count(repo_full_name, username, email, temp_root, git_timeout_sec=None):
        if repo_full_name == "a/repo2":
            raise RuntimeError("fail clone")
        if repo_full_name == "a/repo1":
            return 3
        return 5

    monkeypatch.setattr(cc, "get_repos_with_activity", fake_get_repos_with_activity)
    monkeypatch.setattr(cc, "count_commits_for_repo", fake_count)

    total = cc.get_total_commits_count("octocat", "octocat@github.com", 30, token=None)
    assert total == 8


def test_github_get_rate_limit_error_is_readable(monkeypatch):
    def fake_urlopen(req):
        raise urllib.error.HTTPError(
            req.full_url,
            403,
            "rate limit exceeded",
            {"X-RateLimit-Remaining": "0", "X-RateLimit-Reset": "9999999999"},
            None,
        )

    monkeypatch.setattr(cc.urllib.request, "urlopen", fake_urlopen)
    monkeypatch.setattr(cc.time, "time", lambda: 100)

    try:
        cc._github_get("https://api.github.com/whatever", token=None)
        assert False, "expected RuntimeError"
    except RuntimeError as e:
        assert "rate limit exceeded" in str(e)
