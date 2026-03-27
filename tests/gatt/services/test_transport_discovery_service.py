"""Tests for TransportDiscovery Service."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.services.transport_discovery import TransportDiscoveryService

from .test_service_common import CommonServiceTests


class TestTransportDiscoveryService(CommonServiceTests):
    """TransportDiscovery Service tests."""

    @pytest.fixture
    def service(self) -> TransportDiscoveryService:
        """Provide the service instance."""
        return TransportDiscoveryService()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for TransportDiscovery."""
        return "1824"

    def test_characteristics_defined(self, service: TransportDiscoveryService) -> None:
        """Test that service defines expected characteristics."""
        expected = service.get_expected_characteristics()
        assert len(expected) == 3
