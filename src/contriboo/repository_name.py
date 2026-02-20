from dataclasses import dataclass

from .exceptions import InvalidRepositoryNameError


@dataclass(frozen=True, slots=True)
class RepositoryName:
    _owner: str
    _repo: str

    def __post_init__(self) -> None:
        if not self._owner or not self._repo:
            raise InvalidRepositoryNameError(
                "repository name must be in format 'owner/repo'"
            )
        if "/" in self._owner or "/" in self._repo:
            raise InvalidRepositoryNameError("owner and repo must not contain '/'")

    @classmethod
    def parse(cls, value: str) -> "RepositoryName":
        parts = value.split("/", maxsplit=1)
        if len(parts) != 2:
            raise InvalidRepositoryNameError(
                "repository name must be in format 'owner/repo'"
            )

        owner = parts[0].strip()
        repo = parts[1].strip()
        return cls(owner, repo)

    def owner(self) -> str:
        return self._owner

    def repo_name(self) -> str:
        return self._repo

    def as_full_name(self) -> str:
        return f"{self._owner}/{self._repo}"

    def __str__(self) -> str:
        return self.as_full_name()
