"""Tests for CallFriendlyNameCharacteristic (2BC2)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.call_friendly_name import CallFriendlyNameCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestCallFriendlyName(CommonCharacteristicTests):
    """Test suite for CallFriendlyNameCharacteristic."""

    @pytest.fixture
    def characteristic(self) -> CallFriendlyNameCharacteristic:
        return CallFriendlyNameCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2BC2"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(bytearray(b"John Doe"), "John Doe", "Caller name"),
            CharacteristicTestData(bytearray(b""), "", "Empty string"),
        ]

    def test_roundtrip(self, characteristic: CallFriendlyNameCharacteristic) -> None:
        """Test encode/decode roundtrip."""
        for td in self.valid_test_data_list():
            encoded = characteristic.build_value(td.expected_value)
            result = characteristic.parse_value(encoded)
            assert result == td.expected_value

    def valid_test_data_list(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(bytearray(b"John Doe"), "John Doe", "Caller name"),
            CharacteristicTestData(bytearray(b""), "", "Empty string"),
        ]
