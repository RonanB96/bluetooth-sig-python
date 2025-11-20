"""Tests for Current Time Service."""

import pytest

from bluetooth_sig.gatt.services.current_time_service import CurrentTimeService

from .test_service_common import CommonServiceTests


class TestCurrentTimeService(CommonServiceTests):
    """Test Current Time Service implementation."""

    @pytest.fixture
    def service(self) -> CurrentTimeService:
        """Provide the service instance."""
        return CurrentTimeService()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for Current Time Service."""
        return "1805"
