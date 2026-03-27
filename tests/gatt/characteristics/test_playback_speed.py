"""Tests for PlaybackSpeedCharacteristic (2B9A)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.playback_speed import PlaybackSpeedCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestPlaybackSpeed(CommonCharacteristicTests):
    """Test suite for PlaybackSpeedCharacteristic."""

    @pytest.fixture
    def characteristic(self) -> PlaybackSpeedCharacteristic:
        return PlaybackSpeedCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2B9A"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(bytearray([0x00]), 0, "Normal speed"),
            CharacteristicTestData(bytearray([0x01]), 1, "Speed +1"),
            CharacteristicTestData(bytearray([0xFF]), -1, "Speed -1"),
            CharacteristicTestData(bytearray([0x80]), -128, "Min speed"),
            CharacteristicTestData(bytearray([0x7F]), 127, "Max speed"),
        ]

    def test_roundtrip(self, characteristic: PlaybackSpeedCharacteristic) -> None:
        """Test encode/decode roundtrip."""
        for td in self.valid_test_data_list():
            encoded = characteristic.build_value(td.expected_value)
            result = characteristic.parse_value(encoded)
            assert result == td.expected_value

    def valid_test_data_list(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(bytearray([0x00]), 0, "Normal speed"),
            CharacteristicTestData(bytearray([0x01]), 1, "Speed +1"),
            CharacteristicTestData(bytearray([0xFF]), -1, "Speed -1"),
            CharacteristicTestData(bytearray([0x80]), -128, "Min speed"),
            CharacteristicTestData(bytearray([0x7F]), 127, "Max speed"),
        ]
