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
            CharacteristicTestData(bytearray(b"A"), "A", "Single character (min length)"),
        ]

    def test_max_length_20(self, characteristic: EmergencyTextCharacteristic) -> None:
        """Test 20-byte string (max per spec)."""
        text = "A" * 20
        encoded = characteristic.build_value(text)
        result = characteristic.parse_value(encoded)
        assert result == text

    def test_single_char(self, characteristic: EmergencyTextCharacteristic) -> None:
        """Test single-character string (min per spec)."""
        encoded = characteristic.build_value("X")
        result = characteristic.parse_value(encoded)
        assert result == "X"

    def test_utf8_multibyte(self, characteristic: EmergencyTextCharacteristic) -> None:
        """Test UTF-8 multi-byte characters within 20-byte limit."""
        text = "\u00e9\u00e8"  # 2 chars, 4 bytes UTF-8
        encoded = characteristic.build_value(text)
        result = characteristic.parse_value(encoded)
        assert result == text
