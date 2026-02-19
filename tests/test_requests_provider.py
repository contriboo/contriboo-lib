import requests

from contriboo.integrations.github.requests_provider import RequestsGitHubProfileRepositoryProvider


class FakeResponse:
    def __init__(self, payload: dict[str, object], status_code: int = 200, headers: dict[str, str] | None = None):
        self._payload = payload
        self.status_code = status_code
        self.headers = headers or {}

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise requests.HTTPError("http error", response=self)

    def json(self) -> dict[str, object]:
        return self._payload


class FakeSession:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    def get(self, url: str, headers: dict[str, str], params: dict[str, object], timeout: int) -> FakeResponse:
        self.calls.append({"url": url, "headers": headers, "params": params, "timeout": timeout})
        page = params["page"]
        if page == 1:
            return FakeResponse(
                {
                    "items": [
                        {"repository": {"full_name": "a/repo1"}},
                        {"repository": {"full_name": "a/repo1"}},
                        {"repository": {"full_name": "b/repo2"}},
                    ]
                }
            )
        return FakeResponse({"items": []})


def test_find_repositories_for_author_deduplicates() -> None:
    session = FakeSession()
    provider = RequestsGitHubProfileRepositoryProvider(
        token="token",
        timeout_sec=30,
        retries=3,
        retry_delay_sec=0,
        max_search_pages=20,
        session=session,
    )

    repositories = provider.find_repositories_for_author(username="octocat", days=10)

    assert sorted(repositories) == ["a/repo1", "b/repo2"]
    assert len(session.calls) == 2
    assert session.calls[0]["headers"]["Authorization"] == "Bearer token"


def test_find_repositories_for_author_handles_rate_limit() -> None:
    class RateSession:
        def get(self, url: str, headers: dict[str, str], params: dict[str, object], timeout: int) -> FakeResponse:
            return FakeResponse(
                payload={"message": "rate limit exceeded"},
                status_code=403,
                headers={"X-RateLimit-Remaining": "0", "X-RateLimit-Reset": "9999999999"},
            )

    provider = RequestsGitHubProfileRepositoryProvider(
        token=None,
        timeout_sec=30,
        retries=1,
        retry_delay_sec=0,
        max_search_pages=1,
        session=RateSession(),
    )

    try:
        provider.find_repositories_for_author(username="octocat", days=1)
        assert False, "expected RuntimeError"
    except RuntimeError as exc:
        assert "rate limit" in str(exc).lower()
