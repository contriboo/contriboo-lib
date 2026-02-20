import pytest

from contriboo.exceptions import ContribooConfigurationError
from contriboo.settings import ContribooSettings


def test_settings_validation_raises_for_invalid_values() -> None:
    with pytest.raises(ContribooConfigurationError):
        ContribooSettings(http_timeout_sec=0)

    with pytest.raises(ContribooConfigurationError):
        ContribooSettings(http_retries=0)

    with pytest.raises(ContribooConfigurationError):
        ContribooSettings(http_retry_delay_sec=-1)

    with pytest.raises(ContribooConfigurationError):
        ContribooSettings(git_timeout_sec=0)

    with pytest.raises(ContribooConfigurationError):
        ContribooSettings(max_search_pages=0)
