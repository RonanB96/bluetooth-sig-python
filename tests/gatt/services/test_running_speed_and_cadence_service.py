"""Tests for Running Speed and Cadence Service."""

import pytest

from bluetooth_sig.gatt.services.running_speed_and_cadence import RunningSpeedAndCadenceService

from .test_service_common import CommonServiceTests


class TestRunningSpeedAndCadenceService(CommonServiceTests):
    """Test Running Speed and Cadence Service implementation."""

    @pytest.fixture
    def service(self) -> RunningSpeedAndCadenceService:
        """Provide the service instance."""
        return RunningSpeedAndCadenceService()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for Running Speed and Cadence Service."""
        return "1814"
