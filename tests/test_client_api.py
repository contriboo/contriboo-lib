from pathlib import Path
from typing import cast

from contriboo import ContribooClient, ContribooSettings
from contriboo.profile.service import ProfileAnalysisService


class FakeService:
    pass


def test_client_uses_injected_profile_service() -> None:
    fake_service = cast(ProfileAnalysisService, FakeService())
    client = ContribooClient(profile_service=fake_service)
    assert client.profile is fake_service


def test_client_builds_default_profile_service() -> None:
    settings = ContribooSettings(workspace_dir=Path("/tmp"))
    client = ContribooClient(settings=settings)
    result = client.profile
    assert result is not None
