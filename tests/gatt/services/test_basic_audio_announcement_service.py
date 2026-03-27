"""Tests for BasicAudioAnnouncement Service."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.services.basic_audio_announcement import BasicAudioAnnouncementService

from .test_service_common import CommonServiceTests


class TestBasicAudioAnnouncementService(CommonServiceTests):
    """BasicAudioAnnouncement Service tests."""

    @pytest.fixture
    def service(self) -> BasicAudioAnnouncementService:
        """Provide the service instance."""
        return BasicAudioAnnouncementService()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for BasicAudioAnnouncement."""
        return "1851"

    def test_characteristics_defined(self, service: BasicAudioAnnouncementService) -> None:
        """Test that this advertisement-only service has no characteristics."""
        expected = service.get_expected_characteristics()
        assert len(expected) == 0
