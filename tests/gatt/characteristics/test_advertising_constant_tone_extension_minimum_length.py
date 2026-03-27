"""Tests for AdvertisingConstantToneExtensionMinimumLengthCharacteristic (2BAE)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.advertising_constant_tone_extension_minimum_length import (
    AdvertisingConstantToneExtensionMinimumLengthCharacteristic,
)
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestAdvertisingConstantToneExtensionMinimumLength(CommonCharacteristicTests):
    """Test suite for AdvertisingConstantToneExtensionMinimumLengthCharacteristic."""

    @pytest.fixture
    def characteristic(self) -> AdvertisingConstantToneExtensionMinimumLengthCharacteristic:
        return AdvertisingConstantToneExtensionMinimumLengthCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2BAE"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(bytearray([0x00]), 0, "Min length 0"),
            CharacteristicTestData(bytearray([0x14]), 20, "Min length 20"),
            CharacteristicTestData(bytearray([0xFF]), 255, "Max min length"),
        ]

    def test_roundtrip(self, characteristic: AdvertisingConstantToneExtensionMinimumLengthCharacteristic) -> None:
        """Test encode/decode roundtrip."""
        for td in self.valid_test_data_list():
            encoded = characteristic.build_value(td.expected_value)
            result = characteristic.parse_value(encoded)
            assert result == td.expected_value

    def valid_test_data_list(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(bytearray([0x00]), 0, "Min length 0"),
            CharacteristicTestData(bytearray([0x14]), 20, "Min length 20"),
            CharacteristicTestData(bytearray([0xFF]), 255, "Max min length"),
        ]
