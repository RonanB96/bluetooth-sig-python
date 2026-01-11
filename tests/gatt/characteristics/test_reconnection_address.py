"""Tests for Reconnection Address characteristic (0x2A03)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import ReconnectionAddressCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestReconnectionAddressCharacteristic(CommonCharacteristicTests):
    """Test suite for Reconnection Address characteristic."""

    @pytest.fixture
    def characteristic(self) -> ReconnectionAddressCharacteristic:
        """Return a Reconnection Address characteristic instance."""
        return ReconnectionAddressCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Return the expected UUID for Reconnection Address characteristic."""
        return "2A03"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Return valid test data for reconnection address."""
        return [
            CharacteristicTestData(
                input_data=bytearray([0x01, 0x02, 0x03, 0x04, 0x05, 0x06]),
                expected_value="01:02:03:04:05:06",
                description="MAC address",
            ),
            CharacteristicTestData(
                input_data=bytearray([0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0xFF]),
                expected_value="AA:BB:CC:DD:EE:FF",
                description="Max value MAC address",
            ),
        ]

    def test_decode_address(self) -> None:
        """Test decoding reconnection address."""
        char = ReconnectionAddressCharacteristic()
        result = char.parse_value(bytearray([0x01, 0x02, 0x03, 0x04, 0x05, 0x06]))
        assert result == "01:02:03:04:05:06"

    def test_custom_round_trip(self) -> None:
        """Test encoding and decoding preserve address."""
        char = ReconnectionAddressCharacteristic()
        original = "AA:BB:CC:DD:EE:FF"
        encoded = char.build_value(original)
        decoded = char.parse_value(encoded)
        assert decoded == original
