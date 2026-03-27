"""Tests for BroadcastAudioAnnouncement Service."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.services.broadcast_audio_announcement import BroadcastAudioAnnouncementService

from .test_service_common import CommonServiceTests


class TestBroadcastAudioAnnouncementService(CommonServiceTests):
    """BroadcastAudioAnnouncement Service tests."""

    @pytest.fixture
    def service(self) -> BroadcastAudioAnnouncementService:
        """Provide the service instance."""
        return BroadcastAudioAnnouncementService()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for BroadcastAudioAnnouncement."""
        return "1852"

    def test_characteristics_defined(self, service: BroadcastAudioAnnouncementService) -> None:
        """Test that this advertisement-only service has no characteristics."""
        expected = service.get_expected_characteristics()
        assert len(expected) == 0
