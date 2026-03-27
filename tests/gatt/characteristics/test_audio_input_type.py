"""Tests for AudioInputTypeCharacteristic (2B79)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.audio_input_type import AudioInputType, AudioInputTypeCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestAudioInputType(CommonCharacteristicTests):
    """Test suite for AudioInputTypeCharacteristic."""

    @pytest.fixture
    def characteristic(self) -> AudioInputTypeCharacteristic:
        return AudioInputTypeCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2B79"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(bytearray([0x00]), AudioInputType.UNSPECIFIED, "Unspecified"),
            CharacteristicTestData(bytearray([0x01]), AudioInputType.BLUETOOTH, "Bluetooth"),
            CharacteristicTestData(bytearray([0x02]), AudioInputType.MICROPHONE, "Microphone"),
            CharacteristicTestData(bytearray([0x03]), AudioInputType.ANALOG, "Analog"),
            CharacteristicTestData(bytearray([0x04]), AudioInputType.DIGITAL, "Digital"),
            CharacteristicTestData(bytearray([0x05]), AudioInputType.RADIO, "Radio"),
            CharacteristicTestData(bytearray([0x06]), AudioInputType.STREAMING, "Streaming"),
            CharacteristicTestData(bytearray([0x07]), AudioInputType.AMBIENT, "Ambient"),
        ]

    def test_roundtrip(self, characteristic: AudioInputTypeCharacteristic) -> None:
        """Test encode/decode roundtrip."""
        for td in self.valid_test_data_list():
            encoded = characteristic.build_value(td.expected_value)
            result = characteristic.parse_value(encoded)
            assert result == td.expected_value

    def valid_test_data_list(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(bytearray([0x00]), AudioInputType.UNSPECIFIED, "Unspecified"),
            CharacteristicTestData(bytearray([0x01]), AudioInputType.BLUETOOTH, "Bluetooth"),
            CharacteristicTestData(bytearray([0x02]), AudioInputType.MICROPHONE, "Microphone"),
            CharacteristicTestData(bytearray([0x03]), AudioInputType.ANALOG, "Analog"),
            CharacteristicTestData(bytearray([0x04]), AudioInputType.DIGITAL, "Digital"),
            CharacteristicTestData(bytearray([0x05]), AudioInputType.RADIO, "Radio"),
            CharacteristicTestData(bytearray([0x06]), AudioInputType.STREAMING, "Streaming"),
            CharacteristicTestData(bytearray([0x07]), AudioInputType.AMBIENT, "Ambient"),
        ]
