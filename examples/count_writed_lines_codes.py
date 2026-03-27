"""Minimal example of running get totall count or writed lines of codes."""

import logging
import os

from contriboo import ContribooClient, ContribooSettings

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    settings = ContribooSettings(github_token=os.getenv("GITHUB_TOKEN"))
    client = ContribooClient(settings=settings)

    username = "octocat"
    days = 3

    result = client.profile.count_writed_lines_codes(username=username, days=days)
    print(result)
