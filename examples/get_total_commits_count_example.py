import os

from contriboo import ContribooClient, ContribooSettings


if __name__ == "__main__":
    settings = ContribooSettings(github_token=os.getenv("GITHUB_TOKEN"))
    client = ContribooClient(settings=settings)

    username = "octocat"
    email = "octocat@github.com"
    days = 3

    result = client.profile.count_total_commits(
        username=username,
        email=email,
        days=days,
        show_progress=True,
    )

    print(f"Total commits by {username} for period={days}: {result.total_commits}")
