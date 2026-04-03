"""Tests for GenericHealthSensor Service."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.services.generic_health_sensor import GenericHealthSensorService

from .test_service_common import CommonServiceTests


class TestGenericHealthSensorService(CommonServiceTests):
    """GenericHealthSensor Service tests."""

    @pytest.fixture
    def service(self) -> GenericHealthSensorService:
        """Provide the service instance."""
        return GenericHealthSensorService()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for GenericHealthSensor."""
        return "1840"

    def test_characteristics_defined(self, service: GenericHealthSensorService) -> None:
        """Test that service defines expected characteristics."""
        expected = service.get_expected_characteristics()
        assert len(expected) == 6

    def test_required_characteristics(self, service: GenericHealthSensorService) -> None:
        """Test that required characteristics are correctly marked."""
        required = service.get_required_characteristics()
        assert len(required) == 0
