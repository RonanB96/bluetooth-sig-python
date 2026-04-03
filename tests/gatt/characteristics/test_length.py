"""Tests for Length characteristic (0x2C0A)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.length import LengthCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestLength(CommonCharacteristicTests):
    """Test suite for Length characteristic."""

    @pytest.fixture
    def characteristic(self) -> LengthCharacteristic:
        return LengthCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2C0A"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(bytearray([0x00, 0x00, 0x00, 0x00]), 0, "Zero length"),
            CharacteristicTestData(bytearray([0x40, 0x42, 0x0F, 0x00]), 1000000, "1000000 (0.1m)"),
            CharacteristicTestData(bytearray([0xFE, 0xFF, 0xFF, 0xFF]), 0xFFFFFFFE, "Max valid length"),
        ]

    def test_uint32_size(self, characteristic: LengthCharacteristic) -> None:
        """Verify it encodes as 4 bytes (uint32) per GSS YAML spec."""
        encoded = characteristic.build_value(1000000)
        assert len(encoded) == 4
