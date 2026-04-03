"""Tests for PhysicalActivityMonitor Service."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.services.physical_activity_monitor import PhysicalActivityMonitorService
from bluetooth_sig.types.gatt_enums import CharacteristicName

from .test_service_common import CommonServiceTests


class TestPhysicalActivityMonitorService(CommonServiceTests):
    """PhysicalActivityMonitor Service tests."""

    @pytest.fixture
    def service(self) -> PhysicalActivityMonitorService:
        """Provide the service instance."""
        return PhysicalActivityMonitorService()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for PhysicalActivityMonitor."""
        return "183E"

    def test_characteristics_defined(self, service: PhysicalActivityMonitorService) -> None:
        """Test that service defines expected characteristics."""
        expected = service.get_expected_characteristics()
        assert len(expected) == 11

    def test_required_characteristics(self, service: PhysicalActivityMonitorService) -> None:
        """Test that required characteristics are correctly marked."""
        required = service.get_required_characteristics()
        assert len(required) == 6
        assert CharacteristicName.PHYSICAL_ACTIVITY_MONITOR_FEATURES in required
        assert CharacteristicName.GENERAL_ACTIVITY_INSTANTANEOUS_DATA in required
        assert CharacteristicName.GENERAL_ACTIVITY_SUMMARY_DATA in required
        assert CharacteristicName.PHYSICAL_ACTIVITY_MONITOR_CONTROL_POINT in required
        assert CharacteristicName.PHYSICAL_ACTIVITY_CURRENT_SESSION in required
        assert CharacteristicName.PHYSICAL_ACTIVITY_SESSION_DESCRIPTOR in required
