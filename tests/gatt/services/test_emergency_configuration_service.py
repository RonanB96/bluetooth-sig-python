"""Tests for EmergencyConfiguration Service."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.services.emergency_configuration import EmergencyConfigurationService

from .test_service_common import CommonServiceTests


class TestEmergencyConfigurationService(CommonServiceTests):
    """EmergencyConfiguration Service tests."""

    @pytest.fixture
    def service(self) -> EmergencyConfigurationService:
        """Provide the service instance."""
        return EmergencyConfigurationService()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for EmergencyConfiguration."""
        return "183C"

    def test_characteristics_defined(self, service: EmergencyConfigurationService) -> None:
        """Test that service defines expected characteristics."""
        expected = service.get_expected_characteristics()
        assert len(expected) == 2
