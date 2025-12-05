"""Tests for Device Information Service."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.services.device_information import DeviceInformationService

from .test_service_common import CommonServiceTests


class TestDeviceInformationService(CommonServiceTests):
    """Test Device Information Service implementation."""

    @pytest.fixture
    def service(self) -> DeviceInformationService:
        """Provide the service instance."""
        return DeviceInformationService()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for Device Information Service."""
        return "180A"
