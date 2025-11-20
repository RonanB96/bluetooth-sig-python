"""Tests for Alert Notification Service."""

import pytest

from bluetooth_sig.gatt.services.alert_notification import AlertNotificationService

from .test_service_common import CommonServiceTests


class TestAlertNotificationService(CommonServiceTests):
    """Test Alert Notification Service implementation."""

    @pytest.fixture
    def service(self) -> AlertNotificationService:
        """Provide the service instance."""
        return AlertNotificationService()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for Alert Notification Service."""
        return "1811"
