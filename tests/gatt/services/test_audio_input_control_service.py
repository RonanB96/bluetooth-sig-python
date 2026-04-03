"""Tests for AudioInputControl Service."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.services.audio_input_control import AudioInputControlService
from bluetooth_sig.types.gatt_enums import CharacteristicName

from .test_service_common import CommonServiceTests


class TestAudioInputControlService(CommonServiceTests):
    """AudioInputControl Service tests."""

    @pytest.fixture
    def service(self) -> AudioInputControlService:
        """Provide the service instance."""
        return AudioInputControlService()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for AudioInputControl."""
        return "1843"

    def test_characteristics_defined(self, service: AudioInputControlService) -> None:
        """Test that service defines expected characteristics."""
        expected = service.get_expected_characteristics()
        assert len(expected) == 6

    def test_required_characteristics(self, service: AudioInputControlService) -> None:
        """Test that required characteristics are correctly marked."""
        required = service.get_required_characteristics()
        assert len(required) == 6
        assert CharacteristicName.AUDIO_INPUT_STATE in required
