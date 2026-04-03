"""Tests for MediaControl Service."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.services.media_control import MediaControlService
from bluetooth_sig.types.gatt_enums import CharacteristicName

from .test_service_common import CommonServiceTests


class TestMediaControlService(CommonServiceTests):
    """MediaControl Service tests."""

    @pytest.fixture
    def service(self) -> MediaControlService:
        """Provide the service instance."""
        return MediaControlService()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for MediaControl."""
        return "1848"

    def test_characteristics_defined(self, service: MediaControlService) -> None:
        """Test that service defines expected characteristics."""
        expected = service.get_expected_characteristics()
        assert len(expected) == 22

    def test_required_characteristics(self, service: MediaControlService) -> None:
        """Test that required characteristics are correctly marked."""
        required = service.get_required_characteristics()
        assert len(required) == 7
        assert CharacteristicName.MEDIA_PLAYER_NAME in required
        assert CharacteristicName.MEDIA_STATE in required
        assert CharacteristicName.TRACK_CHANGED in required
        assert CharacteristicName.TRACK_TITLE in required
        assert CharacteristicName.TRACK_DURATION in required
        assert CharacteristicName.TRACK_POSITION in required
        assert CharacteristicName.CONTENT_CONTROL_ID in required
