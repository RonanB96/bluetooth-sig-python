"""Tests for CoordinatedSetSizeCharacteristic (2B85)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.coordinated_set_size import CoordinatedSetSizeCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestCoordinatedSetSize(CommonCharacteristicTests):
    """Test suite for CoordinatedSetSizeCharacteristic."""

    @pytest.fixture
    def characteristic(self) -> CoordinatedSetSizeCharacteristic:
        return CoordinatedSetSizeCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2B85"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(bytearray([0x01]), 1, "Size 1"),
            CharacteristicTestData(bytearray([0x02]), 2, "Size 2"),
            CharacteristicTestData(bytearray([0xFF]), 255, "Max size"),
        ]

    def test_roundtrip(self, characteristic: CoordinatedSetSizeCharacteristic) -> None:
        """Test encode/decode roundtrip."""
        for td in self.valid_test_data_list():
            encoded = characteristic.build_value(td.expected_value)
            result = characteristic.parse_value(encoded)
            assert result == td.expected_value

    def valid_test_data_list(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(bytearray([0x01]), 1, "Size 1"),
            CharacteristicTestData(bytearray([0x02]), 2, "Size 2"),
            CharacteristicTestData(bytearray([0xFF]), 255, "Max size"),
        ]
