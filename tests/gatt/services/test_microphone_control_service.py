"""Tests for MicrophoneControl Service."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.services.microphone_control import MicrophoneControlService
from bluetooth_sig.types.gatt_enums import CharacteristicName

from .test_service_common import CommonServiceTests


class TestMicrophoneControlService(CommonServiceTests):
    """MicrophoneControl Service tests."""

    @pytest.fixture
    def service(self) -> MicrophoneControlService:
        """Provide the service instance."""
        return MicrophoneControlService()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for MicrophoneControl."""
        return "184D"

    def test_characteristics_defined(self, service: MicrophoneControlService) -> None:
        """Test that service defines expected characteristics."""
        expected = service.get_expected_characteristics()
        assert len(expected) == 1

    def test_required_characteristics(self, service: MicrophoneControlService) -> None:
        """Test that required characteristics are correctly marked."""
        required = service.get_required_characteristics()
        assert len(required) == 1
        assert CharacteristicName.MUTE in required
