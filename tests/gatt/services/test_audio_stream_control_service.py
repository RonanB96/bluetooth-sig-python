"""Tests for AudioStreamControl Service."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.services.audio_stream_control import AudioStreamControlService
from bluetooth_sig.types.gatt_enums import CharacteristicName

from .test_service_common import CommonServiceTests


class TestAudioStreamControlService(CommonServiceTests):
    """AudioStreamControl Service tests."""

    @pytest.fixture
    def service(self) -> AudioStreamControlService:
        """Provide the service instance."""
        return AudioStreamControlService()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for AudioStreamControl."""
        return "184E"

    def test_characteristics_defined(self, service: AudioStreamControlService) -> None:
        """Test that service defines expected characteristics."""
        expected = service.get_expected_characteristics()
        assert len(expected) == 3

    def test_required_characteristics(self, service: AudioStreamControlService) -> None:
        """Test that required characteristics are correctly marked."""
        required = service.get_required_characteristics()
        assert len(required) == 1
        assert CharacteristicName.ASE_CONTROL_POINT in required
