"""Tests for AdvertisingConstantToneExtensionTransmitDurationCharacteristic (2BB0)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.advertising_constant_tone_extension_transmit_duration import (
    AdvertisingConstantToneExtensionTransmitDurationCharacteristic,
)
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestAdvertisingConstantToneExtensionTransmitDuration(CommonCharacteristicTests):
    """Test suite for AdvertisingConstantToneExtensionTransmitDurationCharacteristic."""

    @pytest.fixture
    def characteristic(self) -> AdvertisingConstantToneExtensionTransmitDurationCharacteristic:
        return AdvertisingConstantToneExtensionTransmitDurationCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2BB0"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(bytearray([0x00]), 0, "Duration 0"),
            CharacteristicTestData(bytearray([0x0A]), 10, "Duration 10"),
            CharacteristicTestData(bytearray([0xFF]), 255, "Max duration"),
        ]
