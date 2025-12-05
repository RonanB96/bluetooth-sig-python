"""Tests for Cycling Speed and Cadence Service."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.services.cycling_speed_and_cadence import CyclingSpeedAndCadenceService

from .test_service_common import CommonServiceTests


class TestCyclingSpeedAndCadenceService(CommonServiceTests):
    """Test Cycling Speed and Cadence Service implementation."""

    @pytest.fixture
    def service(self) -> CyclingSpeedAndCadenceService:
        """Provide the service instance."""
        return CyclingSpeedAndCadenceService()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for Cycling Speed and Cadence Service."""
        return "1816"
