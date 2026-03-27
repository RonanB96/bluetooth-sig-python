"""Tests for CoordinatedSetIdentification Service."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.services.coordinated_set_identification import CoordinatedSetIdentificationService
from bluetooth_sig.types.gatt_enums import CharacteristicName

from .test_service_common import CommonServiceTests


class TestCoordinatedSetIdentificationService(CommonServiceTests):
    """CoordinatedSetIdentification Service tests."""

    @pytest.fixture
    def service(self) -> CoordinatedSetIdentificationService:
        """Provide the service instance."""
        return CoordinatedSetIdentificationService()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for CoordinatedSetIdentification."""
        return "1846"

    def test_characteristics_defined(self, service: CoordinatedSetIdentificationService) -> None:
        """Test that service defines expected characteristics."""
        expected = service.get_expected_characteristics()
        assert len(expected) == 4

    def test_required_characteristics(self, service: CoordinatedSetIdentificationService) -> None:
        """Test that required characteristics are correctly marked."""
        required = service.get_required_characteristics()
        assert len(required) == 1
        assert CharacteristicName.SET_IDENTITY_RESOLVING_KEY in required
