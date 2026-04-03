"""Tests for ElapsedTime Service."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.services.elapsed_time import ElapsedTimeService
from bluetooth_sig.types.gatt_enums import CharacteristicName

from .test_service_common import CommonServiceTests


class TestElapsedTimeService(CommonServiceTests):
    """ElapsedTime Service tests."""

    @pytest.fixture
    def service(self) -> ElapsedTimeService:
        """Provide the service instance."""
        return ElapsedTimeService()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for ElapsedTime."""
        return "183F"

    def test_characteristics_defined(self, service: ElapsedTimeService) -> None:
        """Test that service defines expected characteristics."""
        expected = service.get_expected_characteristics()
        assert len(expected) == 1

    def test_required_characteristics(self, service: ElapsedTimeService) -> None:
        """Test that required characteristics are correctly marked."""
        required = service.get_required_characteristics()
        assert len(required) == 1
        assert CharacteristicName.ELAPSED_TIME in required
