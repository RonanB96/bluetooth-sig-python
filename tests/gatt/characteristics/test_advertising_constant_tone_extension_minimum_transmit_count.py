"""Tests for AdvertisingConstantToneExtensionMinimumTransmitCountCharacteristic (2BAF)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.advertising_constant_tone_extension_minimum_transmit_count import (
    AdvertisingConstantToneExtensionMinimumTransmitCountCharacteristic,
)
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestAdvertisingConstantToneExtensionMinimumTransmitCount(CommonCharacteristicTests):
    """Test suite for AdvertisingConstantToneExtensionMinimumTransmitCountCharacteristic."""

    @pytest.fixture
    def characteristic(self) -> AdvertisingConstantToneExtensionMinimumTransmitCountCharacteristic:
        return AdvertisingConstantToneExtensionMinimumTransmitCountCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2BAF"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(bytearray([0x00]), 0, "Count 0"),
            CharacteristicTestData(bytearray([0x05]), 5, "Count 5"),
            CharacteristicTestData(bytearray([0xFF]), 255, "Max count"),
        ]
