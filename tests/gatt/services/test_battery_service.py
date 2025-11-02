"""Tests for Battery Service."""

import pytest

from bluetooth_sig.gatt.services.battery_service import BatteryService

from .test_service_common import CommonServiceTests


class TestBatteryService(CommonServiceTests):
    """Test Battery Service implementation."""

    @pytest.fixture
    def service(self) -> BatteryService:
        """Provide the service instance."""
        return BatteryService()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for Battery Service."""
        return "180F"
