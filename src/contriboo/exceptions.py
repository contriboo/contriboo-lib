class ContribooError(Exception):
    """Base exception for contriboo."""


class ContribooConfigurationError(ContribooError):
    """Raised when settings/configuration are invalid."""


class InvalidDaysRangeError(ContribooError):
    """Raised when days parameter is invalid."""


class InvalidRepositoryNameError(ContribooError):
    """Raised when repository full name is invalid."""


class GitHubApiError(ContribooError):
    """Raised for generic GitHub API failures."""


class GitHubRateLimitError(GitHubApiError):
    """Raised when GitHub rate limit is exceeded."""


class GitHubConnectionError(GitHubApiError):
    """Raised for temporary network/DNS issues to GitHub API."""


class GitHubResponseSchemaError(GitHubApiError):
    """Raised when GitHub API response has unexpected schema."""


class GitOperationError(ContribooError):
    """Raised when git command exits with error."""


class GitOperationTimeoutError(GitOperationError):
    """Raised when git command times out."""
