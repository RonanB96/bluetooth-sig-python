"""Tests for Ranging Service."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.services.ranging import RangingService
from bluetooth_sig.types.gatt_enums import CharacteristicName

from .test_service_common import CommonServiceTests


class TestRangingService(CommonServiceTests):
    """Ranging Service tests."""

    @pytest.fixture
    def service(self) -> RangingService:
        """Provide the service instance."""
        return RangingService()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for Ranging."""
        return "185B"

    def test_characteristics_defined(self, service: RangingService) -> None:
        """Test that service defines expected characteristics."""
        expected = service.get_expected_characteristics()
        assert len(expected) == 6

    def test_required_characteristics(self, service: RangingService) -> None:
        """Test that required characteristics are correctly marked."""
        required = service.get_required_characteristics()
        assert len(required) == 1
        assert CharacteristicName.RAS_FEATURES in required
