from dataclasses import dataclass

from .exceptions import InvalidRepositoryNameError


@dataclass(frozen=True, slots=True)
class RepositoryName:
    """Value object for repository full name in `owner/repo` format.

    Attributes:
        _owner: Repository owner part.
        _repo: Repository name part.
    """

    _owner: str
    _repo: str

    def __post_init__(self) -> None:
        """Validate parsed repository parts.

        Raises:
            InvalidRepositoryNameError: If owner/repo parts are empty or contain `/`.
        """
        if not self._owner or not self._repo:
            raise InvalidRepositoryNameError(
                "repository name must be in format 'owner/repo'"
            )
        if "/" in self._owner or "/" in self._repo:
            raise InvalidRepositoryNameError("owner and repo must not contain '/'")

    @classmethod
    def parse(cls, value: str) -> "RepositoryName":
        """Parse repository full name string.

        Args:
            value: Repository name in `owner/repo` format.

        Returns:
            RepositoryName: Parsed repository value object.

        Raises:
            InvalidRepositoryNameError: If input is not in `owner/repo` format.
        """
        parts = value.split("/", maxsplit=1)
        if len(parts) != 2:
            raise InvalidRepositoryNameError(
                "repository name must be in format 'owner/repo'"
            )

        owner = parts[0].strip()
        repo = parts[1].strip()
        return cls(owner, repo)

    def owner(self) -> str:
        """Return repository owner.

        Returns:
            str: Owner part from `owner/repo`.
        """
        return self._owner

    def repo_name(self) -> str:
        """Return repository short name.

        Returns:
            str: Repo part from `owner/repo`.
        """
        return self._repo

    def as_full_name(self) -> str:
        """Return canonical repository full name.

        Returns:
            str: Repository full name formatted as `owner/repo`.
        """
        return f"{self._owner}/{self._repo}"

    def __str__(self) -> str:
        """Return repository full name as string.

        Returns:
            str: Repository full name formatted as `owner/repo`.
        """
        return self.as_full_name()

    def __repr__(self) -> str:
        """Return debug representation.

        Returns:
            str: Debug-friendly `RepositoryName('owner/repo')` representation.
        """
        return f"RepositoryName('{self.as_full_name()}')"
