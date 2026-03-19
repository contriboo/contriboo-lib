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

    result = client.profile.percent_of_dev_changes_in_main(
        username=username,
        email=email,
        repo=repository,
        days=days,
        show_progress=True,
        code_changes=True
        merged_commits=False,
    )

    logger.info(
        "Percent of changes in main %s for %s days: %s",
        username,
        days,
        result,
    )