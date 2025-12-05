"""Tests for Health Thermometer Service."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.services.health_thermometer import HealthThermometerService

from .test_service_common import CommonServiceTests


class TestHealthThermometerService(CommonServiceTests):
    """Test Health Thermometer Service implementation."""

    @pytest.fixture
    def service(self) -> HealthThermometerService:
        """Provide the service instance."""
        return HealthThermometerService()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for Health Thermometer Service."""
        return "1809"
