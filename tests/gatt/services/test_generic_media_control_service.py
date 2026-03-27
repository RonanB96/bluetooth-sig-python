"""Tests for GenericMediaControl Service."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.services.generic_media_control import GenericMediaControlService
from bluetooth_sig.types.gatt_enums import CharacteristicName

from .test_service_common import CommonServiceTests


class TestGenericMediaControlService(CommonServiceTests):
    """GenericMediaControl Service tests."""

    @pytest.fixture
    def service(self) -> GenericMediaControlService:
        """Provide the service instance."""
        return GenericMediaControlService()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for GenericMediaControl."""
        return "1849"

    def test_characteristics_defined(self, service: GenericMediaControlService) -> None:
        """Test that service defines expected characteristics."""
        expected = service.get_expected_characteristics()
        assert len(expected) == 22

    def test_required_characteristics(self, service: GenericMediaControlService) -> None:
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
