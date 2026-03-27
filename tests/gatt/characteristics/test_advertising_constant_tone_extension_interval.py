"""Tests for AdvertisingConstantToneExtensionIntervalCharacteristic (2BB1)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.advertising_constant_tone_extension_interval import (
    AdvertisingConstantToneExtensionIntervalCharacteristic,
)
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestAdvertisingConstantToneExtensionInterval(CommonCharacteristicTests):
    """Test suite for AdvertisingConstantToneExtensionIntervalCharacteristic."""

    @pytest.fixture
    def characteristic(self) -> AdvertisingConstantToneExtensionIntervalCharacteristic:
        return AdvertisingConstantToneExtensionIntervalCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2BB1"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(bytearray([0x00]), 0, "Interval 0"),
            CharacteristicTestData(bytearray([0x10]), 16, "Interval 16"),
            CharacteristicTestData(bytearray([0xFF]), 255, "Max interval"),
        ]

    def test_roundtrip(self, characteristic: AdvertisingConstantToneExtensionIntervalCharacteristic) -> None:
        """Test encode/decode roundtrip."""
        for td in self.valid_test_data_list():
            encoded = characteristic.build_value(td.expected_value)
            result = characteristic.parse_value(encoded)
            assert result == td.expected_value

    def valid_test_data_list(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(bytearray([0x00]), 0, "Interval 0"),
            CharacteristicTestData(bytearray([0x10]), 16, "Interval 16"),
            CharacteristicTestData(bytearray([0xFF]), 255, "Max interval"),
        ]
