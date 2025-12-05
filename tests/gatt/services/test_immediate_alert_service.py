"""Tests for Immediate Alert Service."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.services.immediate_alert import ImmediateAlertService

from .test_service_common import CommonServiceTests


class TestImmediateAlertService(CommonServiceTests):
    """Test Immediate Alert Service implementation."""

    @pytest.fixture
    def service(self) -> ImmediateAlertService:
        """Provide the service instance."""
        return ImmediateAlertService()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for Immediate Alert Service."""
        return "1802"
