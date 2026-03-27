"""Tests for EmergencyIdCharacteristic (2B2D)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.emergency_id import EmergencyIdCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestEmergencyId(CommonCharacteristicTests):
    """Test suite for EmergencyIdCharacteristic."""

    @pytest.fixture
    def characteristic(self) -> EmergencyIdCharacteristic:
        return EmergencyIdCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2B2D"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(bytearray(b"112"), "112", "Emergency ID 112"),
            CharacteristicTestData(bytearray(b""), "", "Empty string"),
        ]

    def test_roundtrip(self, characteristic: EmergencyIdCharacteristic) -> None:
        """Test encode/decode roundtrip."""
        for td in self.valid_test_data_list():
            encoded = characteristic.build_value(td.expected_value)
            result = characteristic.parse_value(encoded)
            assert result == td.expected_value

    def valid_test_data_list(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(bytearray(b"112"), "112", "Emergency ID 112"),
            CharacteristicTestData(bytearray(b""), "", "Empty string"),
        ]
