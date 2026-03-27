"""Tests for BearerSignalStrengthCharacteristic (2BB7)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.bearer_signal_strength import BearerSignalStrengthCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestBearerSignalStrength(CommonCharacteristicTests):
    """Test suite for BearerSignalStrengthCharacteristic."""

    @pytest.fixture
    def characteristic(self) -> BearerSignalStrengthCharacteristic:
        return BearerSignalStrengthCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2BB7"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(bytearray([0x00]), 0, "No signal"),
            CharacteristicTestData(bytearray([0x64]), 100, "Signal 100"),
            CharacteristicTestData(bytearray([0xFF]), 255, "Max signal"),
        ]

    def test_roundtrip(self, characteristic: BearerSignalStrengthCharacteristic) -> None:
        """Test encode/decode roundtrip."""
        for td in self.valid_test_data_list():
            encoded = characteristic.build_value(td.expected_value)
            result = characteristic.parse_value(encoded)
            assert result == td.expected_value

    def valid_test_data_list(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(bytearray([0x00]), 0, "No signal"),
            CharacteristicTestData(bytearray([0x64]), 100, "Signal 100"),
            CharacteristicTestData(bytearray([0xFF]), 255, "Max signal"),
        ]
