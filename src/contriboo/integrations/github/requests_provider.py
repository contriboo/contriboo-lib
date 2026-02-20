import datetime
import time
from typing import TypeAlias

import requests

from contriboo.exceptions import (
    GitHubApiError,
    GitHubConnectionError,
    GitHubRateLimitError,
    GitHubResponseSchemaError,
    InvalidDaysRangeError,
)
from contriboo.profile.interfaces import ProfileRepositoryProvider
from contriboo.profile.types import DaysRange
from contriboo.repository_name import RepositoryName

from .dto import GitHubCommitSearchResponseDTO

RequestScalar: TypeAlias = str | bytes | int | float
RequestValue: TypeAlias = (
    RequestScalar | list[RequestScalar] | tuple[RequestScalar, ...] | None
)
RequestParams: TypeAlias = dict[str, RequestValue]


class GitHubProvider(ProfileRepositoryProvider):
    __slots__ = (
        "_token",
        "_base_url",
        "_timeout_sec",
        "_retries",
        "_retry_delay_sec",
        "_max_search_pages",
        "_session",
    )

    def __init__(
        self,
        token: str | None,
        timeout_sec: int,
        retries: int,
        retry_delay_sec: int,
        max_search_pages: int,
        session: requests.Session | None = None,
        base_url: str = "https://api.github.com",
    ) -> None:
        self._token = token
        self._base_url = base_url.rstrip("/")
        self._timeout_sec = timeout_sec
        self._retries = retries
        self._retry_delay_sec = retry_delay_sec
        self._max_search_pages = max_search_pages
        self._session = session or requests.Session()

    def find_repositories_for_author(
        self, username: str, days: DaysRange
    ) -> list[RepositoryName]:
        query = self._build_query(username=username, days=days)

        repositories: dict[RepositoryName, bool] = {}
        for page in range(1, self._max_search_pages + 1):
            dto = self._search_commits_page(
                "/search/commits",
                params={"q": query, "per_page": 100, "page": page},
            )
            if not dto.items:
                break

            for item in dto.items:
                if item.repository and item.repository.full_name:
                    repository_name = RepositoryName.parse(item.repository.full_name)
                    repositories[repository_name] = True

        return list(repositories.keys())

    def _build_query(self, username: str, days: DaysRange) -> str:
        if days == "all":
            return f"author:{username}"
        if isinstance(days, bool) or days <= 0:
            raise InvalidDaysRangeError("days must be > 0 or 'all'")

        since = (
            datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=days)
        ).date()
        return f"author:{username} committer-date:>={since.isoformat()}"

    def _search_commits_page(
        self,
        path: str,
        params: RequestParams,
    ) -> GitHubCommitSearchResponseDTO:
        raw_payload = self._get_json(path=path, params=params)
        return GitHubCommitSearchResponseDTO.model_validate(raw_payload)

    def _get_json(self, path: str, params: RequestParams) -> dict[str, object]:
        url = f"{self._base_url}{path}"
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"

        for attempt in range(1, self._retries + 1):
            try:
                response = self._session.get(
                    url,
                    headers=headers,
                    params=params,
                    timeout=self._timeout_sec,
                )
                response.raise_for_status()
                raw_json = response.json()
                if not isinstance(raw_json, dict):
                    raise GitHubResponseSchemaError(
                        "GitHub API returned non-object response"
                    )
                return raw_json
            except requests.HTTPError as exc:
                if self._handle_rate_limit(exc):
                    continue
                raise GitHubApiError("GitHub API request failed") from exc
            except (requests.ConnectionError, requests.Timeout) as exc:
                if attempt < self._retries:
                    time.sleep(self._retry_delay_sec)
                    continue
                raise GitHubConnectionError(
                    "GitHub API is unreachable (DNS/network issue). "
                    "Check internet/VPN/DNS and try again."
                ) from exc

        raise GitHubApiError("GitHub API request failed")

    def _handle_rate_limit(self, exc: requests.HTTPError) -> bool:
        response = exc.response
        if response is None:
            return False

        remaining = response.headers.get("X-RateLimit-Remaining")
        reset = response.headers.get("X-RateLimit-Reset")
        if response.status_code != 403 or remaining != "0" or reset is None:
            return False

        wait_seconds = int(reset) - int(time.time()) + 1
        if 0 < wait_seconds <= 60:
            time.sleep(wait_seconds)
            return True

        raise GitHubRateLimitError(
            f"GitHub rate limit exceeded. Wait about {max(wait_seconds, 0)}s or use token."
        )
