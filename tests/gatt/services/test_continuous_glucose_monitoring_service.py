"""Tests for ContinuousGlucoseMonitoring Service."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.services.continuous_glucose_monitoring import ContinuousGlucoseMonitoringService
from bluetooth_sig.types.gatt_enums import CharacteristicName

from .test_service_common import CommonServiceTests


class TestContinuousGlucoseMonitoringService(CommonServiceTests):
    """ContinuousGlucoseMonitoring Service tests."""

    @pytest.fixture
    def service(self) -> ContinuousGlucoseMonitoringService:
        """Provide the service instance."""
        return ContinuousGlucoseMonitoringService()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for ContinuousGlucoseMonitoring."""
        return "181F"

    def test_characteristics_defined(self, service: ContinuousGlucoseMonitoringService) -> None:
        """Test that service defines expected characteristics."""
        expected = service.get_expected_characteristics()
        assert len(expected) == 7

    def test_required_characteristics(self, service: ContinuousGlucoseMonitoringService) -> None:
        """Test that required characteristics are correctly marked."""
        required = service.get_required_characteristics()
        assert len(required) == 2
        assert CharacteristicName.CGM_MEASUREMENT in required
        assert CharacteristicName.CGM_FEATURE in required
