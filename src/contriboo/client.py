from contriboo.integrations.git.gateway import GitGateway
from contriboo.integrations.github.requests_provider import GitHubProvider
from contriboo.profile.service import ProfileAnalysisService
from contriboo.settings import ContribooSettings


class ContribooClient:
    __slots__ = ("_settings", "_profile_service")

    def __init__(
        self,
        settings: ContribooSettings | None = None,
        profile_service: ProfileAnalysisService | None = None,
    ) -> None:
        self._settings = settings or ContribooSettings()

        if profile_service is not None:
            self._profile_service = profile_service
            return

        repository_provider = GitHubProvider(
            token=self._settings.github_token,
            timeout_sec=self._settings.http_timeout_sec,
            retries=self._settings.http_retries,
            retry_delay_sec=self._settings.http_retry_delay_sec,
            max_search_pages=self._settings.max_search_pages,
        )
        git_gateway = GitGateway(git_timeout_sec=self._settings.git_timeout_sec)
        self._profile_service = ProfileAnalysisService(
            repository_provider=repository_provider,
            git_gateway=git_gateway,
            workspace_dir=self._settings.workspace_dir,
        )

    @property
    def profile(self) -> ProfileAnalysisService:
        return self._profile_service
