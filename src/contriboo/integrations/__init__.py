"""Infrastructure adapters for external systems."""

from .git import GitGateway
from .github import GitHubProvider

__all__ = ["GitGateway", "GitHubProvider"]
