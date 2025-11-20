"""Tests for Scan Parameters Service."""

import pytest

from bluetooth_sig.gatt.services.scan_parameters import ScanParametersService

from .test_service_common import CommonServiceTests


class TestScanParametersService(CommonServiceTests):
    """Test Scan Parameters Service implementation."""

    @pytest.fixture
    def service(self) -> ScanParametersService:
        """Provide the service instance."""
        return ScanParametersService()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for Scan Parameters Service."""
        return "1813"
