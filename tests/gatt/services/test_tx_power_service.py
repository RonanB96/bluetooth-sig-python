"""Tests for Tx Power Service."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.services.tx_power import TxPowerService

from .test_service_common import CommonServiceTests


class TestTxPowerService(CommonServiceTests):
    """Test Tx Power Service implementation."""

    @pytest.fixture
    def service(self) -> TxPowerService:
        """Provide the service instance."""
        return TxPowerService()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for Tx Power Service."""
        return "1804"
