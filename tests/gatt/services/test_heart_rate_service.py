"""Tests for Heart Rate Service."""

import pytest

from bluetooth_sig.gatt.services.heart_rate import HeartRateService

from .test_service_common import CommonServiceTests


class TestHeartRateService(CommonServiceTests):
    """Test Heart Rate Service implementation."""

    @pytest.fixture
    def service(self) -> HeartRateService:
        """Provide the service instance."""
        return HeartRateService()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for Heart Rate Service."""
        return "180D"
