"""Tests for Indoor Positioning Service."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.services.indoor_positioning_service import IndoorPositioningService
from bluetooth_sig.types.gatt_enums import CharacteristicName

from .test_service_common import CommonServiceTests


class TestIndoorPositioningService(CommonServiceTests):
    """Test Indoor Positioning Service implementation."""

    @pytest.fixture
    def service(self) -> IndoorPositioningService:
        """Provide the service instance."""
        return IndoorPositioningService()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for Indoor Positioning Service."""
        return "1821"

    def test_service_includes_new_characteristics(self, service: IndoorPositioningService) -> None:
        """Test that the service now includes the newly implemented characteristics."""
        expected_characteristics = service.get_expected_characteristics()

        # Check that the new optional characteristics are included

        assert CharacteristicName.LOCAL_NORTH_COORDINATE in expected_characteristics
        assert CharacteristicName.LOCAL_EAST_COORDINATE in expected_characteristics
        assert CharacteristicName.ALTITUDE in expected_characteristics
        assert CharacteristicName.UNCERTAINTY in expected_characteristics

        # Verify they are marked as optional (required=False)
        assert expected_characteristics[CharacteristicName.LOCAL_NORTH_COORDINATE].required is False
        assert expected_characteristics[CharacteristicName.LOCAL_EAST_COORDINATE].required is False
        assert expected_characteristics[CharacteristicName.ALTITUDE].required is False
        assert expected_characteristics[CharacteristicName.UNCERTAINTY].required is False

    def test_service_mandatory_characteristics_unchanged(self, service: IndoorPositioningService) -> None:
        """Test that mandatory characteristics remain unchanged."""
        expected_characteristics = service.get_expected_characteristics()

        assert CharacteristicName.LATITUDE in expected_characteristics
        assert CharacteristicName.LONGITUDE in expected_characteristics
        assert expected_characteristics[CharacteristicName.LATITUDE].required is True
        assert expected_characteristics[CharacteristicName.LONGITUDE].required is True
