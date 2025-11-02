"""Tests for Blood Pressure Service."""

import pytest

from bluetooth_sig.gatt.services.blood_pressure import BloodPressureService

from .test_service_common import CommonServiceTests


class TestBloodPressureService(CommonServiceTests):
    """Test Blood Pressure Service implementation."""

    @pytest.fixture
    def service(self) -> BloodPressureService:
        """Provide the service instance."""
        return BloodPressureService()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for Blood Pressure Service."""
        return "1810"
