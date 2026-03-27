"""GitHub API repository provider based on ``requests`` transport."""

import datetime
import time

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

from .dto import GitHubCommitSearchResponseDTO, GitHubUserDTO

type RequestScalar = str | bytes | int | float
type RequestValue = (
    RequestScalar | list[RequestScalar] | tuple[RequestScalar, ...] | None
)
type RequestParams = dict[str, RequestValue]

GITHUB_RATE_LIMIT_STATUS = 403
LOCAL_RATE_LIMIT_RETRY_WINDOW_SEC = 60


class GitHubProvider(ProfileRepositoryProvider):
    """GitHub repository provider based on `requests` client."""

    __slots__ = (
        "_base_url",
        "_max_search_pages",
        "_retries",
        "_retry_delay_sec",
        "_session",
        "_timeout_sec",
        "_token",
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
        """
        Initialize provider.

        Args:
            token: Optional GitHub token for authenticated requests.
            timeout_sec: Timeout for HTTP requests in seconds.
            retries: Number of retry attempts for transient errors.
            retry_delay_sec: Delay between retries in seconds.
            max_search_pages: Max commit-search pages to read.
            session: Optional preconfigured requests session.
            base_url: GitHub API base URL.

        """
        self._token = token
        self._base_url = base_url.rstrip("/")
        self._timeout_sec = timeout_sec
        self._retries = retries
        self._retry_delay_sec = retry_delay_sec
        self._max_search_pages = max_search_pages
        self._session = session or requests.Session()

    def find_repositories_for_author(
        self,
        username: str,
        days: DaysRange,
    ) -> list[RepositoryName]:
        """
        Return unique repositories where author has activity.

        Args:
            username: GitHub username used in search query.
            days: Positive day count or `"all"` for full history.

        Returns:
            list[RepositoryName]: Unique repository identifiers.

        """
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

    def count_followers(self, username: str) -> int:
        """
        Count the number of followers for a given user.

        Args:
            username: The username of the user.

        Returns:
            int: The number of followers.

        """
        raw_payload = GitHubUserDTO.model_validate(
            self._get_json(path=f"/users/{username}", params={})
        )
        return raw_payload.followers

    def count_writed_lines_codes(self, username: str, days: int) -> int:
        """
        Count the number of lines written at last n-days.

        Args:
            username: The username of the user.
            days: The number of days it takes to find the written lines of code.

        Returns:
            int: Count of lines written at last n-days.

        """
        query = self._build_query(username=username, days=days)
        total_lines = 0

        for page in range(1, self._max_search_pages + 1):
            dto = self._search_commits_page(
                "/search/commits",
                params={"q": query, "per_page": 100, "page": page},
            )
            if not dto.items:
                break

        for item in dto.items:
            if item.sha and item.repository and item.repository.full_name:
                commit_stats = self._get_commit_stats(
                    repo_full_name=item.repository.full_name,
                    sha=item.sha,
                )
                total_lines += commit_stats

        return total_lines

    def _get_commit_stats(self, repo_full_name: str, sha: str) -> int:
        """
        Fetch commit statistics (additions + deletions) for a specific commit.

        Args:
            repo_full_name: Repository full name (owner/repo).
            sha: Commit SHA.

        Returns:
            int: Total lines changed (additions + deletions).

        """
        path = f"/repos/{repo_full_name}/commits/{sha}"
        raw_payload = self._get_json(path=path, params={})

        additions = raw_payload.get("additions", 0) or 0
        deletions = raw_payload.get("deletions", 0) or 0

        return additions + deletions

    def _build_query(self, username: str, days: DaysRange) -> str:
        """
        Build GitHub commit-search query string.

        Args:
            username: GitHub username.
            days: Positive day count or `"all"`.

        Returns:
            str: Search query for GitHub commits endpoint.

        Raises:
            InvalidDaysRangeError: If `days` value is invalid.

        """
        if days == "all":
            return f"author:{username}"
        if not isinstance(days, int) or days <= 0:
            raise InvalidDaysRangeError.must_be_positive_or_all()

        since = (
            datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=days)
        ).date()
        return f"author:{username} committer-date:>={since.isoformat()}"

    def _search_commits_page(
        self,
        path: str,
        params: RequestParams,
    ) -> GitHubCommitSearchResponseDTO:
        """
        Fetch and parse one page of commit-search response.

        Args:
            path: API path part.
            params: Query parameters for request.

        Returns:
            GitHubCommitSearchResponseDTO: Parsed page DTO.

        """
        raw_payload = self._get_json(path=path, params=params)
        return GitHubCommitSearchResponseDTO.model_validate(raw_payload)

    def _get_json(self, path: str, params: RequestParams) -> dict[str, object]:
        """
        Perform GET request and return JSON object payload.

        Args:
            path: API path part.
            params: Query parameters for request.

        Returns:
            dict[str, object]: Decoded JSON object.

        Raises:
            GitHubResponseSchemaError: If response JSON is not an object.
            GitHubApiError: If request fails with non-rate-limit HTTP error.
            GitHubConnectionError: If network/DNS failures persist after retries.
            GitHubRateLimitError: If hard rate-limit was reached.

        """
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
                    raise GitHubResponseSchemaError.non_object()
            except requests.HTTPError as exc:
                if self._handle_rate_limit(exc):
                    continue
                raise GitHubApiError.request_failed() from exc
            except (requests.ConnectionError, requests.Timeout) as exc:
                if attempt < self._retries:
                    time.sleep(self._retry_delay_sec)
                    continue
                raise GitHubConnectionError.unreachable() from exc
            else:
                return raw_json

        raise GitHubApiError.request_failed()

    def _handle_rate_limit(self, exc: requests.HTTPError) -> bool:
        """
        Handle GitHub rate-limit HTTP error.

        Args:
            exc: HTTPError raised by `requests`.

        Returns:
            bool: `True` when request should be retried, otherwise `False`.

        Raises:
            GitHubRateLimitError: If reset wait time is too long for local retry.

        """
        response = exc.response
        if response is None:
            return False

        remaining = response.headers.get("X-RateLimit-Remaining")
        reset = response.headers.get("X-RateLimit-Reset")
        if (
            response.status_code != GITHUB_RATE_LIMIT_STATUS
            or remaining != "0"
            or reset is None
        ):
            return False

        try:
            reset_timestamp = int(reset)
        except (ValueError, TypeError):
            return False

        wait_seconds = reset_timestamp - int(time.time()) + 1
        if 0 < wait_seconds <= LOCAL_RATE_LIMIT_RETRY_WINDOW_SEC:
            time.sleep(wait_seconds)
            return True

        raise GitHubRateLimitError.exceeded(wait_seconds)
