"""Tests for PlayingOrderCharacteristic (2BA1)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.playing_order import PlayingOrder, PlayingOrderCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestPlayingOrder(CommonCharacteristicTests):
    """Test suite for PlayingOrderCharacteristic."""

    @pytest.fixture
    def characteristic(self) -> PlayingOrderCharacteristic:
        return PlayingOrderCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2BA1"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(bytearray([0x01]), PlayingOrder.SINGLE_ONCE, "Single once"),
            CharacteristicTestData(bytearray([0x02]), PlayingOrder.SINGLE_REPEAT, "Single repeat"),
            CharacteristicTestData(bytearray([0x09]), PlayingOrder.SHUFFLE_ONCE, "Shuffle once"),
            CharacteristicTestData(bytearray([0x0A]), PlayingOrder.SHUFFLE_REPEAT, "Shuffle repeat"),
        ]

    def test_roundtrip(self, characteristic: PlayingOrderCharacteristic) -> None:
        """Test encode/decode roundtrip."""
        for td in self.valid_test_data_list():
            encoded = characteristic.build_value(td.expected_value)
            result = characteristic.parse_value(encoded)
            assert result == td.expected_value

    def valid_test_data_list(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(bytearray([0x01]), PlayingOrder.SINGLE_ONCE, "Single once"),
            CharacteristicTestData(bytearray([0x02]), PlayingOrder.SINGLE_REPEAT, "Single repeat"),
            CharacteristicTestData(bytearray([0x09]), PlayingOrder.SHUFFLE_ONCE, "Shuffle once"),
            CharacteristicTestData(bytearray([0x0A]), PlayingOrder.SHUFFLE_REPEAT, "Shuffle repeat"),
        ]
