import os

from contriboo import get_total_commits_count


if __name__ == "__main__":
    # Лучше задать export GITHUB_TOKEN=... чтобы не упереться в rate-limit.
    days = 1
    total = get_total_commits_count(
        username="octocat",
        email="octocat@github.com",
        days=days,
        token=os.getenv("GITHUB_TOKEN"),
        show_progress=True,
    )
    print(f"Totall commits: {total} for last {days} days")
