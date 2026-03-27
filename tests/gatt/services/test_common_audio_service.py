"""Tests for CommonAudio Service."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.services.common_audio import CommonAudioService

from .test_service_common import CommonServiceTests


class TestCommonAudioService(CommonServiceTests):
    """CommonAudio Service tests."""

    @pytest.fixture
    def service(self) -> CommonAudioService:
        """Provide the service instance."""
        return CommonAudioService()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for CommonAudio."""
        return "1853"

    def test_characteristics_defined(self, service: CommonAudioService) -> None:
        """Test that this presence-only service has no characteristics."""
        expected = service.get_expected_characteristics()
        assert len(expected) == 0
