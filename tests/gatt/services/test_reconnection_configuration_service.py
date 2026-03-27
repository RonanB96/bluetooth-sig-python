"""Tests for ReconnectionConfiguration Service."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.services.reconnection_configuration import ReconnectionConfigurationService
from bluetooth_sig.types.gatt_enums import CharacteristicName

from .test_service_common import CommonServiceTests


class TestReconnectionConfigurationService(CommonServiceTests):
    """ReconnectionConfiguration Service tests."""

    @pytest.fixture
    def service(self) -> ReconnectionConfigurationService:
        """Provide the service instance."""
        return ReconnectionConfigurationService()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for ReconnectionConfiguration."""
        return "1829"

    def test_characteristics_defined(self, service: ReconnectionConfigurationService) -> None:
        """Test that service defines expected characteristics."""
        expected = service.get_expected_characteristics()
        assert len(expected) == 3

    def test_required_characteristics(self, service: ReconnectionConfigurationService) -> None:
        """Test that required characteristics are correctly marked."""
        required = service.get_required_characteristics()
        assert len(required) == 1
        assert CharacteristicName.RC_FEATURE in required
