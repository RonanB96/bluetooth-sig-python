"""Tests for PlayingOrdersSupportedCharacteristic (2BA2)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.playing_orders_supported import (
    PlayingOrdersSupported,
    PlayingOrdersSupportedCharacteristic,
)
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestPlayingOrdersSupported(CommonCharacteristicTests):
    """Test suite for PlayingOrdersSupportedCharacteristic."""

    @pytest.fixture
    def characteristic(self) -> PlayingOrdersSupportedCharacteristic:
        return PlayingOrdersSupportedCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2BA2"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(bytearray([0x00, 0x00]), PlayingOrdersSupported(0), "None supported"),
            CharacteristicTestData(bytearray([0x01, 0x00]), PlayingOrdersSupported.SINGLE_ONCE, "Single once"),
            CharacteristicTestData(
                bytearray([0xFF, 0x03]),
                PlayingOrdersSupported.SINGLE_ONCE
                | PlayingOrdersSupported.SINGLE_REPEAT
                | PlayingOrdersSupported.IN_ORDER_ONCE
                | PlayingOrdersSupported.IN_ORDER_REPEAT
                | PlayingOrdersSupported.OLDEST_ONCE
                | PlayingOrdersSupported.OLDEST_REPEAT
                | PlayingOrdersSupported.NEWEST_ONCE
                | PlayingOrdersSupported.NEWEST_REPEAT
                | PlayingOrdersSupported.SHUFFLE_ONCE
                | PlayingOrdersSupported.SHUFFLE_REPEAT,
                "All orders",
            ),
        ]
