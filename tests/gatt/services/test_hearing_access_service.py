"""Tests for HearingAccess Service."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.services.hearing_access import HearingAccessService
from bluetooth_sig.types.gatt_enums import CharacteristicName

from .test_service_common import CommonServiceTests


class TestHearingAccessService(CommonServiceTests):
    """HearingAccess Service tests."""

    @pytest.fixture
    def service(self) -> HearingAccessService:
        """Provide the service instance."""
        return HearingAccessService()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for HearingAccess."""
        return "1854"

    def test_characteristics_defined(self, service: HearingAccessService) -> None:
        """Test that service defines expected characteristics."""
        expected = service.get_expected_characteristics()
        assert len(expected) == 3

    def test_required_characteristics(self, service: HearingAccessService) -> None:
        """Test that required characteristics are correctly marked."""
        required = service.get_required_characteristics()
        assert len(required) == 1
        assert CharacteristicName.HEARING_AID_FEATURES in required
