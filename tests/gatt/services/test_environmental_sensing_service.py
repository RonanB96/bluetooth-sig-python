"""Tests for Environmental Sensing Service."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.services.environmental_sensing import EnvironmentalSensingService

from .test_service_common import CommonServiceTests


class TestEnvironmentalSensingService(CommonServiceTests):
    """Test Environmental Sensing Service implementation."""

    @pytest.fixture
    def service(self) -> EnvironmentalSensingService:
        """Provide the service instance."""
        return EnvironmentalSensingService()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for Environmental Sensing Service."""
        return "181A"
