"""Tests for System ID characteristic (0x2A23)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import SystemIdCharacteristic, SystemIdData
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestSystemIdCharacteristic(CommonCharacteristicTests):
    """Test suite for System ID characteristic."""

    @pytest.fixture
    def characteristic(self) -> SystemIdCharacteristic:
        """Return a System ID characteristic instance."""
        return SystemIdCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Return the expected UUID for System ID characteristic."""
        return "2A23"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Return valid test data for system ID."""
        return [
            CharacteristicTestData(
                input_data=bytearray([0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08]),
                expected_value=SystemIdData(
                    manufacturer_id=bytes([0x01, 0x02, 0x03, 0x04, 0x05]), oui=bytes([0x06, 0x07, 0x08])
                ),
                description="System ID with manufacturer and OUI",
            ),
            CharacteristicTestData(
                input_data=bytearray([0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0x11, 0x22, 0x33]),
                expected_value=SystemIdData(
                    manufacturer_id=bytes([0xAA, 0xBB, 0xCC, 0xDD, 0xEE]), oui=bytes([0x11, 0x22, 0x33])
                ),
                description="Different System ID",
            ),
        ]

    def test_decode_system_id(self) -> None:
        """Test decoding system ID."""
        char = SystemIdCharacteristic()
        result = char.parse_value(bytearray([0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08]))
        assert result is not None
        assert result.manufacturer_id == bytes([0x01, 0x02, 0x03, 0x04, 0x05])
        assert result.oui == bytes([0x06, 0x07, 0x08])

    def test_custom_round_trip(self) -> None:
        """Test encoding and decoding preserve data."""
        char = SystemIdCharacteristic()
        original = SystemIdData(manufacturer_id=bytes([0xAA, 0xBB, 0xCC, 0xDD, 0xEE]), oui=bytes([0x11, 0x22, 0x33]))
        encoded = char.build_value(original)
        decoded = char.parse_value(encoded)
        assert decoded == original
