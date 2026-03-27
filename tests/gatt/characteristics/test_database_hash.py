"""Tests for Database Hash characteristic (0x2B2A)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.database_hash import DatabaseHashCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestDatabaseHash(CommonCharacteristicTests):
    """Test suite for Database Hash characteristic."""

    @pytest.fixture
    def characteristic(self) -> DatabaseHashCharacteristic:
        return DatabaseHashCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2B2A"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                bytearray(16),
                bytes(16),
                "All zeros",
            ),
            CharacteristicTestData(
                bytearray(range(16)),
                bytes(range(16)),
                "Sequential bytes",
            ),
        ]

    def test_roundtrip(self, characteristic: DatabaseHashCharacteristic) -> None:
        data = bytes(range(16))
        encoded = characteristic.build_value(data)
        result = characteristic.parse_value(encoded)
        assert result == data

    def test_expected_length(self, characteristic: DatabaseHashCharacteristic) -> None:
        assert characteristic.expected_length == 16

    def test_truncates_to_16_bytes(self, characteristic: DatabaseHashCharacteristic) -> None:
        """Test that encoding truncates to 16 bytes."""
        data = bytes(range(20))
        encoded = characteristic.build_value(data)
        assert len(encoded) == 16

    def test_pads_short_data(self, characteristic: DatabaseHashCharacteristic) -> None:
        """Test that encoding pads short data to 16 bytes."""
        data = bytes(range(8))
        encoded = characteristic.build_value(data)
        assert len(encoded) == 16
        assert encoded[:8] == bytearray(range(8))
        assert encoded[8:] == bytearray(8)
