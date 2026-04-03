"""Tests for AudioInputDescriptionCharacteristic (2B7C)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.audio_input_description import AudioInputDescriptionCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestAudioInputDescription(CommonCharacteristicTests):
    """Test suite for AudioInputDescriptionCharacteristic."""

    @pytest.fixture
    def characteristic(self) -> AudioInputDescriptionCharacteristic:
        return AudioInputDescriptionCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2B7C"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(bytearray(b"Microphone"), "Microphone", "Microphone"),
            CharacteristicTestData(bytearray(b""), "", "Empty string"),
            CharacteristicTestData(bytearray(b"Line In"), "Line In", "Line In"),
        ]
