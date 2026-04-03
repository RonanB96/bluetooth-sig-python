"""Tests for GenericTelephoneBearer Service."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.services.generic_telephone_bearer import GenericTelephoneBearerService
from bluetooth_sig.types.gatt_enums import CharacteristicName

from .test_service_common import CommonServiceTests


class TestGenericTelephoneBearerService(CommonServiceTests):
    """GenericTelephoneBearer Service tests."""

    @pytest.fixture
    def service(self) -> GenericTelephoneBearerService:
        """Provide the service instance."""
        return GenericTelephoneBearerService()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for GenericTelephoneBearer."""
        return "184C"

    def test_characteristics_defined(self, service: GenericTelephoneBearerService) -> None:
        """Test that service defines expected characteristics."""
        expected = service.get_expected_characteristics()
        assert len(expected) == 15

    def test_required_characteristics(self, service: GenericTelephoneBearerService) -> None:
        """Test that required characteristics are correctly marked."""
        required = service.get_required_characteristics()
        assert len(required) == 11
        assert CharacteristicName.BEARER_PROVIDER_NAME in required
        assert CharacteristicName.BEARER_TECHNOLOGY in required
