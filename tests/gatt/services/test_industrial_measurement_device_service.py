"""Tests for IndustrialMeasurementDevice Service."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.services.industrial_measurement_device import IndustrialMeasurementDeviceService
from bluetooth_sig.types.gatt_enums import CharacteristicName

from .test_service_common import CommonServiceTests


class TestIndustrialMeasurementDeviceService(CommonServiceTests):
    """IndustrialMeasurementDevice Service tests."""

    @pytest.fixture
    def service(self) -> IndustrialMeasurementDeviceService:
        """Provide the service instance."""
        return IndustrialMeasurementDeviceService()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for IndustrialMeasurementDevice."""
        return "185A"

    def test_characteristics_defined(self, service: IndustrialMeasurementDeviceService) -> None:
        """Test that service defines expected characteristics."""
        expected = service.get_expected_characteristics()
        assert len(expected) == 8

    def test_required_characteristics(self, service: IndustrialMeasurementDeviceService) -> None:
        """Test that required characteristics are correctly marked."""
        required = service.get_required_characteristics()
        assert len(required) == 1
        assert CharacteristicName.IMD_STATUS in required
