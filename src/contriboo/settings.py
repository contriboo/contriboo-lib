from dataclasses import dataclass
from pathlib import Path

from .exceptions import ContribooConfigurationError


@dataclass(frozen=True, slots=True)
class ContribooSettings:
    """Configuration container for contriboo runtime behavior.

    Attributes:
        github_token: Optional GitHub token used for authenticated API calls.
        http_timeout_sec: Timeout for GitHub HTTP requests in seconds.
        http_retries: Number of retry attempts for transient HTTP errors.
        http_retry_delay_sec: Delay between retry attempts in seconds.
        git_timeout_sec: Timeout for git CLI commands in seconds.
        max_search_pages: Max number of GitHub commit-search pages to read.
        workspace_dir: Optional directory for temporary clone workspace.
    """

    github_token: str | None = None
    http_timeout_sec: int = 30
    http_retries: int = 3
    http_retry_delay_sec: int = 2
    git_timeout_sec: int = 180
    max_search_pages: int = 20
    workspace_dir: Path | None = None

    def __post_init__(self) -> None:
        """Validate settings values after dataclass initialization.

        Raises:
            ContribooConfigurationError: If any numeric setting is out of valid range.
        """
        if self.http_timeout_sec <= 0:
            raise ContribooConfigurationError("http_timeout_sec must be > 0")
        if self.http_retries <= 0:
            raise ContribooConfigurationError("http_retries must be > 0")
        if self.http_retry_delay_sec < 0:
            raise ContribooConfigurationError("http_retry_delay_sec must be >= 0")
        if self.git_timeout_sec <= 0:
            raise ContribooConfigurationError("git_timeout_sec must be > 0")
        if self.max_search_pages <= 0:
            raise ContribooConfigurationError("max_search_pages must be > 0")
