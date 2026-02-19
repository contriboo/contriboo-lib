import pytest

from contriboo.settings import ContribooSettings


def test_settings_validation_raises_for_invalid_values() -> None:
    with pytest.raises(ValueError):
        ContribooSettings(http_timeout_sec=0)

    with pytest.raises(ValueError):
        ContribooSettings(http_retries=0)

    with pytest.raises(ValueError):
        ContribooSettings(http_retry_delay_sec=-1)

    with pytest.raises(ValueError):
        ContribooSettings(git_timeout_sec=0)

    with pytest.raises(ValueError):
        ContribooSettings(max_search_pages=0)
