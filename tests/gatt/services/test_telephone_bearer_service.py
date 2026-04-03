"""Tests for TelephoneBearer Service."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.services.telephone_bearer import TelephoneBearerService
from bluetooth_sig.types.gatt_enums import CharacteristicName

from .test_service_common import CommonServiceTests


class TestTelephoneBearerService(CommonServiceTests):
    """TelephoneBearer Service tests."""

    @pytest.fixture
    def service(self) -> TelephoneBearerService:
        """Provide the service instance."""
        return TelephoneBearerService()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for TelephoneBearer."""
        return "184B"

    def test_characteristics_defined(self, service: TelephoneBearerService) -> None:
        """Test that service defines expected characteristics."""
        expected = service.get_expected_characteristics()
        assert len(expected) == 16

    def test_required_characteristics(self, service: TelephoneBearerService) -> None:
        """Test that required characteristics are correctly marked."""
        required = service.get_required_characteristics()
        assert len(required) == 12
        assert CharacteristicName.BEARER_PROVIDER_NAME in required
        assert CharacteristicName.BEARER_TECHNOLOGY in required
