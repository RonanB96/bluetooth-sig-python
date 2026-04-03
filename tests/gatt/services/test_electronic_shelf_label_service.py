"""Tests for ElectronicShelfLabel Service."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.services.electronic_shelf_label import ElectronicShelfLabelService
from bluetooth_sig.types.gatt_enums import CharacteristicName

from .test_service_common import CommonServiceTests


class TestElectronicShelfLabelService(CommonServiceTests):
    """ElectronicShelfLabel Service tests."""

    @pytest.fixture
    def service(self) -> ElectronicShelfLabelService:
        """Provide the service instance."""
        return ElectronicShelfLabelService()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for ElectronicShelfLabel."""
        return "1857"

    def test_characteristics_defined(self, service: ElectronicShelfLabelService) -> None:
        """Test that service defines expected characteristics."""
        expected = service.get_expected_characteristics()
        assert len(expected) == 9

    def test_required_characteristics(self, service: ElectronicShelfLabelService) -> None:
        """Test that required characteristics are correctly marked."""
        required = service.get_required_characteristics()
        assert len(required) == 5
        assert CharacteristicName.ESL_ADDRESS in required
