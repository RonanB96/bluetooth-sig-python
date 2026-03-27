"""Tests for BinarySensor Service."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.services.binary_sensor import BinarySensorService
from bluetooth_sig.types.gatt_enums import CharacteristicName

from .test_service_common import CommonServiceTests


class TestBinarySensorService(CommonServiceTests):
    """BinarySensor Service tests."""

    @pytest.fixture
    def service(self) -> BinarySensorService:
        """Provide the service instance."""
        return BinarySensorService()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for BinarySensor."""
        return "183B"

    def test_characteristics_defined(self, service: BinarySensorService) -> None:
        """Test that service defines expected characteristics."""
        expected = service.get_expected_characteristics()
        assert len(expected) == 2

    def test_required_characteristics(self, service: BinarySensorService) -> None:
        """Test that required characteristics are correctly marked."""
        required = service.get_required_characteristics()
        assert len(required) == 2
        assert CharacteristicName.BSS_CONTROL_POINT in required
        assert CharacteristicName.BSS_RESPONSE in required
