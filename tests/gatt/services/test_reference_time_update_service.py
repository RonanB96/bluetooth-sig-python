"""Tests for Reference Time Update Service."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.services.reference_time_update import ReferenceTimeUpdateService

from .test_service_common import CommonServiceTests


class TestReferenceTimeUpdateService(CommonServiceTests):
    """Test Reference Time Update Service implementation."""

    @pytest.fixture
    def service(self) -> ReferenceTimeUpdateService:
        """Provide the service instance."""
        return ReferenceTimeUpdateService()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for Reference Time Update Service."""
        return "1806"
