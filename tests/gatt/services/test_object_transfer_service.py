"""Tests for ObjectTransfer Service."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.services.object_transfer import ObjectTransferService
from bluetooth_sig.types.gatt_enums import CharacteristicName

from .test_service_common import CommonServiceTests


class TestObjectTransferService(CommonServiceTests):
    """ObjectTransfer Service tests."""

    @pytest.fixture
    def service(self) -> ObjectTransferService:
        """Provide the service instance."""
        return ObjectTransferService()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for ObjectTransfer."""
        return "1825"

    def test_characteristics_defined(self, service: ObjectTransferService) -> None:
        """Test that service defines expected characteristics."""
        expected = service.get_expected_characteristics()
        assert len(expected) == 12

    def test_required_characteristics(self, service: ObjectTransferService) -> None:
        """Test that required characteristics are correctly marked."""
        required = service.get_required_characteristics()
        assert len(required) == 1
        assert CharacteristicName.OTS_FEATURE in required
