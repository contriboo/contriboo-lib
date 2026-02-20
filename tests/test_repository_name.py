import pytest

from contriboo.exceptions import InvalidRepositoryNameError
from contriboo.repository_name import RepositoryName


def test_repository_name_parse_and_methods() -> None:
    repository = RepositoryName.parse("owner-name/repo-name")

    assert repository.owner() == "owner-name"
    assert repository.repo_name() == "repo-name"
    assert repository.as_full_name() == "owner-name/repo-name"
    assert str(repository) == "owner-name/repo-name"


def test_repository_name_invalid_format() -> None:
    with pytest.raises(InvalidRepositoryNameError):
        RepositoryName.parse("owner-only")

    with pytest.raises(InvalidRepositoryNameError):
        RepositoryName.parse("owner/")

    with pytest.raises(InvalidRepositoryNameError):
        RepositoryName.parse("/repo")
