"""Tests for AudioOutputDescriptionCharacteristic (2B83)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.audio_output_description import AudioOutputDescriptionCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestAudioOutputDescription(CommonCharacteristicTests):
    """Test suite for AudioOutputDescriptionCharacteristic."""

    @pytest.fixture
    def characteristic(self) -> AudioOutputDescriptionCharacteristic:
        return AudioOutputDescriptionCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2B83"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(bytearray(b"Speaker"), "Speaker", "Speaker"),
            CharacteristicTestData(bytearray(b""), "", "Empty string"),
        ]

    def test_roundtrip(self, characteristic: AudioOutputDescriptionCharacteristic) -> None:
        """Test encode/decode roundtrip."""
        for td in self.valid_test_data_list():
            encoded = characteristic.build_value(td.expected_value)
            result = characteristic.parse_value(encoded)
            assert result == td.expected_value

    def valid_test_data_list(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(bytearray(b"Speaker"), "Speaker", "Speaker"),
            CharacteristicTestData(bytearray(b""), "", "Empty string"),
        ]
