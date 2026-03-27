"""Tests for EmergencyTextCharacteristic (2B2E)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.emergency_text import EmergencyTextCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestEmergencyText(CommonCharacteristicTests):
    """Test suite for EmergencyTextCharacteristic."""

    @pytest.fixture
    def characteristic(self) -> EmergencyTextCharacteristic:
        return EmergencyTextCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2B2E"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(bytearray(b"Emergency"), "Emergency", "Emergency text"),
            CharacteristicTestData(bytearray(b""), "", "Empty string"),
        ]

    def test_roundtrip(self, characteristic: EmergencyTextCharacteristic) -> None:
        """Test encode/decode roundtrip."""
        for td in self.valid_test_data_list():
            encoded = characteristic.build_value(td.expected_value)
            result = characteristic.parse_value(encoded)
            assert result == td.expected_value

    def valid_test_data_list(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(bytearray(b"Emergency"), "Emergency", "Emergency text"),
            CharacteristicTestData(bytearray(b""), "", "Empty string"),
        ]
