"""Tests for InsulinDelivery Service."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.services.insulin_delivery import InsulinDeliveryService
from bluetooth_sig.types.gatt_enums import CharacteristicName

from .test_service_common import CommonServiceTests


class TestInsulinDeliveryService(CommonServiceTests):
    """InsulinDelivery Service tests."""

    @pytest.fixture
    def service(self) -> InsulinDeliveryService:
        """Provide the service instance."""
        return InsulinDeliveryService()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for InsulinDelivery."""
        return "183A"

    def test_characteristics_defined(self, service: InsulinDeliveryService) -> None:
        """Test that service defines expected characteristics."""
        expected = service.get_expected_characteristics()
        assert len(expected) == 9

    def test_required_characteristics(self, service: InsulinDeliveryService) -> None:
        """Test that required characteristics are correctly marked."""
        required = service.get_required_characteristics()
        assert len(required) == 5
        assert CharacteristicName.IDD_STATUS_CHANGED in required
        assert CharacteristicName.IDD_STATUS in required
        assert CharacteristicName.IDD_ANNUNCIATION_STATUS in required
        assert CharacteristicName.IDD_FEATURES in required
        assert CharacteristicName.IDD_STATUS_READER_CONTROL_POINT in required
