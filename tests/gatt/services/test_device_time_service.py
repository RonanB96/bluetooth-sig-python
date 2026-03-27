"""Tests for DeviceTime Service."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.services.device_time import DeviceTimeService
from bluetooth_sig.types.gatt_enums import CharacteristicName

from .test_service_common import CommonServiceTests


class TestDeviceTimeService(CommonServiceTests):
    """DeviceTime Service tests."""

    @pytest.fixture
    def service(self) -> DeviceTimeService:
        """Provide the service instance."""
        return DeviceTimeService()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for DeviceTime."""
        return "1847"

    def test_characteristics_defined(self, service: DeviceTimeService) -> None:
        """Test that service defines expected characteristics."""
        expected = service.get_expected_characteristics()
        assert len(expected) == 6

    def test_required_characteristics(self, service: DeviceTimeService) -> None:
        """Test that required characteristics are correctly marked."""
        required = service.get_required_characteristics()
        assert len(required) == 4
        assert CharacteristicName.DEVICE_TIME_FEATURE in required
        assert CharacteristicName.DEVICE_TIME_PARAMETERS in required
        assert CharacteristicName.DEVICE_TIME in required
        assert CharacteristicName.DEVICE_TIME_CONTROL_POINT in required
