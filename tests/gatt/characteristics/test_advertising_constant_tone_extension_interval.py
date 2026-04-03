"""Tests for AdvertisingConstantToneExtensionIntervalCharacteristic (2BB1)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.advertising_constant_tone_extension_interval import (
    AdvertisingConstantToneExtensionIntervalCharacteristic,
)
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestAdvertisingConstantToneExtensionInterval(CommonCharacteristicTests):
    """Test suite for AdvertisingConstantToneExtensionIntervalCharacteristic."""

    @pytest.fixture
    def characteristic(self) -> AdvertisingConstantToneExtensionIntervalCharacteristic:
        return AdvertisingConstantToneExtensionIntervalCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2BB1"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(bytearray([0x06, 0x00]), 6, "Min interval 0x0006"),
            CharacteristicTestData(bytearray([0x10, 0x00]), 16, "Interval 16"),
            CharacteristicTestData(bytearray([0xFF, 0xFF]), 65535, "Max interval 0xFFFF"),
        ]
