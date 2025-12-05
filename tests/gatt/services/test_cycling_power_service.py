"""Tests for Cycling Power Service."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.services.cycling_power import CyclingPowerService

from .test_service_common import CommonServiceTests


class TestCyclingPowerService(CommonServiceTests):
    """Test Cycling Power Service implementation."""

    @pytest.fixture
    def service(self) -> CyclingPowerService:
        """Provide the service instance."""
        return CyclingPowerService()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for Cycling Power Service."""
        return "1818"
