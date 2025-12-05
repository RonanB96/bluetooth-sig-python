"""Tests for Phone Alert Status Service."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.services.phone_alert_status import PhoneAlertStatusService

from .test_service_common import CommonServiceTests


class TestPhoneAlertStatusService(CommonServiceTests):
    """Test Phone Alert Status Service implementation."""

    @pytest.fixture
    def service(self) -> PhoneAlertStatusService:
        """Provide the service instance."""
        return PhoneAlertStatusService()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for Phone Alert Status Service."""
        return "180E"
