"""Tests for PublicBroadcastAnnouncement Service."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.services.public_broadcast_announcement import PublicBroadcastAnnouncementService

from .test_service_common import CommonServiceTests


class TestPublicBroadcastAnnouncementService(CommonServiceTests):
    """PublicBroadcastAnnouncement Service tests."""

    @pytest.fixture
    def service(self) -> PublicBroadcastAnnouncementService:
        """Provide the service instance."""
        return PublicBroadcastAnnouncementService()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for PublicBroadcastAnnouncement."""
        return "1856"

    def test_characteristics_defined(self, service: PublicBroadcastAnnouncementService) -> None:
        """Test that this advertisement-only service has no characteristics."""
        expected = service.get_expected_characteristics()
        assert len(expected) == 0
