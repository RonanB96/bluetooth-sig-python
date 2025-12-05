"""Tests for Automation IO Service."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.services.automation_io import AutomationIOService

from .test_service_common import CommonServiceTests


class TestAutomationIOService(CommonServiceTests):
    """Test Automation IO Service implementation."""

    @pytest.fixture
    def service(self) -> AutomationIOService:
        """Provide the service instance."""
        return AutomationIOService()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for Automation IO Service."""
        return "1815"
