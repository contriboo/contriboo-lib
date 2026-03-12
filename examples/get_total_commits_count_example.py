

import logging
import os

from contriboo import ContribooClient, ContribooSettings

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    settings = ContribooSettings(github_token=os.getenv("GITHUB_TOKEN"))
    client = ContribooClient(settings=settings)

    username = "octocat"
    email = "octocat@example.com"
    days = 3

    result = client.profile.count_total_commits(
        username=username,
        email=email,
        days=days,
        show_progress=True,
    )

    logger.info(
        "Total commits by %s for period=%s: %s",
        username,
        days,
        result.total_commits,
    )
