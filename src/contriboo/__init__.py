"""Contriboo public package API."""

from .client import ContribooClient
from .exceptions import (
    ContribooConfigurationError,
    ContribooError,
    GitHubApiError,
    GitHubConnectionError,
    GitHubRateLimitError,
    GitHubResponseSchemaError,
    GitOperationError,
    GitOperationTimeoutError,
    InvalidDaysRangeError,
    InvalidRepositoryNameError,
)
from .profile.models import ProfileCommitCountResult, RepositoryCommitCount
from .profile.types import DaysRange
from .repository_name import RepositoryName
from .settings import ContribooSettings

__version__ = "0.1.0"

__all__ = [
    "ContribooClient",
    "ContribooSettings",
    "DaysRange",
    "RepositoryName",
    "ProfileCommitCountResult",
    "RepositoryCommitCount",
    "ContribooError",
    "ContribooConfigurationError",
    "InvalidDaysRangeError",
    "InvalidRepositoryNameError",
    "GitHubApiError",
    "GitHubRateLimitError",
    "GitHubConnectionError",
    "GitHubResponseSchemaError",
    "GitOperationError",
    "GitOperationTimeoutError",
]
