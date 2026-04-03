"""Tests for AuthorizationControl Service."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.services.authorization_control import AuthorizationControlService
from bluetooth_sig.types.gatt_enums import CharacteristicName

from .test_service_common import CommonServiceTests


class TestAuthorizationControlService(CommonServiceTests):
    """AuthorizationControl Service tests."""

    @pytest.fixture
    def service(self) -> AuthorizationControlService:
        """Provide the service instance."""
        return AuthorizationControlService()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for AuthorizationControl."""
        return "183D"

    def test_characteristics_defined(self, service: AuthorizationControlService) -> None:
        """Test that service defines expected characteristics."""
        expected = service.get_expected_characteristics()
        assert len(expected) == 5

    def test_required_characteristics(self, service: AuthorizationControlService) -> None:
        """Test that mandatory ACS characteristics are required."""
        required = service.get_required_characteristics()
        assert CharacteristicName.ACS_STATUS in required
        assert CharacteristicName.ACS_CONTROL_POINT in required
