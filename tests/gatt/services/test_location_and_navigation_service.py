"""Tests for Location and Navigation Service."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.services.location_and_navigation import LocationAndNavigationService

from .test_service_common import CommonServiceTests


class TestLocationAndNavigationService(CommonServiceTests):
    """Test Location and Navigation Service implementation."""

    @pytest.fixture
    def service(self) -> LocationAndNavigationService:
        """Provide the service instance."""
        return LocationAndNavigationService()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for Location and Navigation Service."""
        return "1819"
