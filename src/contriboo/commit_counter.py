import datetime
import os
import shutil
import subprocess
import tempfile
import time
import requests


GITHUB_API = "https://api.github.com"
DEFAULT_GIT_TIMEOUT_SEC = 180
DEFAULT_HTTP_RETRIES = 3


def _run(cmd, cwd=None, timeout_sec=None):
    try:
        p = subprocess.run(
            cmd,
            cwd=cwd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout_sec,
        )
    except subprocess.TimeoutExpired:
        raise RuntimeError(f"command timeout after {timeout_sec}s: {cmd}")
    if p.returncode != 0:
        raise RuntimeError(p.stderr.strip() or p.stdout.strip() or "command failed")
    return p.stdout.strip()


def _github_get(url, token=None, params=None):
    for attempt in range(1, DEFAULT_HTTP_RETRIES + 1):
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if token:
            headers["Authorization"] = f"Bearer {token}"
        try:
            r = requests.get(url, headers=headers, params=params, timeout=30)
            r.raise_for_status()
            return r.json()
        except requests.HTTPError as e:
            response = e.response
            if response is None:
                raise
            remaining = response.headers.get("X-RateLimit-Remaining")
            reset = response.headers.get("X-RateLimit-Reset")
            if response.status_code == 403 and remaining == "0" and reset:
                wait_sec = int(reset) - int(time.time()) + 1
                if wait_sec > 0 and wait_sec <= 60:
                    time.sleep(wait_sec)
                    continue
                raise RuntimeError(
                    f"github rate limit exceeded; wait about {max(wait_sec, 0)}s or use token"
                )
            raise
        except (requests.ConnectionError, requests.Timeout) as e:
            if attempt < DEFAULT_HTTP_RETRIES:
                time.sleep(2)
                continue
            raise RuntimeError(
                "github api is unreachable (dns/network issue). "
                "Check internet/VPN/DNS and try again"
            ) from e
    raise RuntimeError("github api request failed")


def get_repos_with_activity(username, days, token=None):
    dt = datetime.datetime.utcnow() - datetime.timedelta(days=days)
    since = dt.strftime("%Y-%m-%d")
    q = f"author:{username} committer-date:>={since}"

    repos = {}
    page = 1
    while True:
        url = f"{GITHUB_API}/search/commits"
        data = _github_get(
            url,
            token=token,
            params={"q": q, "per_page": 100, "page": page},
        )
        items = data.get("items") or []
        if not items:
            break
        for i in items:
            repo = i.get("repository") or {}
            full_name = repo.get("full_name")
            if full_name:
                repos[full_name] = True
        page += 1
        if page > 20:
            break

    return list(repos.keys())


def _pick_branch(repo_dir):
    try:
        _run("git rev-parse --verify origin/main", cwd=repo_dir)
        return "main"
    except Exception:
        pass

    try:
        _run("git rev-parse --verify origin/master", cwd=repo_dir)
        return "master"
    except Exception:
        pass

    return None


def _count_in_cloned_repo(repo_dir, username, email):
    branch = _pick_branch(repo_dir)
    if not branch:
        return 0

    text = _run(
        f"git log origin/{branch} --pretty=format:'%ae|%an|%ce|%cn'",
        cwd=repo_dir,
    )
    if not text:
        return 0

    username = (username or "").strip().lower()
    email = (email or "").strip().lower()
    total = 0

    for line in text.split("\n"):
        parts = line.split("|")
        if len(parts) < 4:
            continue

        ae = parts[0].strip().lower()
        an = parts[1].strip().lower()
        ce = parts[2].strip().lower()
        cn = parts[3].strip().lower()

        if email and (ae == email or ce == email):
            total += 1
            continue
        if username and (an == username or cn == username):
            total += 1
            continue

    return total


def count_commits_for_repo(repo_full_name, username, email, temp_root, git_timeout_sec=None):
    repo_url = f"https://github.com/{repo_full_name}.git"
    repo_dir = os.path.join(temp_root, repo_full_name.replace("/", "__"))

    _run(
        f"git clone --filter=blob:none --no-checkout {repo_url} {repo_dir}",
        timeout_sec=git_timeout_sec,
    )
    return _count_in_cloned_repo(repo_dir, username, email)


def get_total_commits_count(
    username,
    email,
    days,
    token=None,
    show_progress=False,
    git_timeout_sec=DEFAULT_GIT_TIMEOUT_SEC,
):
    repos = get_repos_with_activity(username=username, days=days, token=token)
    if not repos:
        return 0

    tmp = tempfile.mkdtemp(prefix="contriboo-")
    total = 0

    try:
        count = len(repos)
        for idx, repo in enumerate(repos, start=1):
            if show_progress:
                print(f"[{idx}/{count}] cloning {repo} ...")
            try:
                c = count_commits_for_repo(
                    repo,
                    username,
                    email,
                    tmp,
                    git_timeout_sec=git_timeout_sec,
                )
                total += c
                if show_progress:
                    print(f"[{idx}/{count}] {repo}: +{c}")
            except Exception as e:
                if show_progress:
                    print(f"[{idx}/{count}] skip {repo}: {e}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    return total
