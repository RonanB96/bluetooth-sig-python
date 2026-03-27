"""Tests for Constant Tone Extension Enable characteristic (0x2BAD)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.constant_tone_extension_enable import (
    ConstantToneExtensionEnableCharacteristic,
    CTEEnableState,
)
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestConstantToneExtensionEnable(CommonCharacteristicTests):
    """Test suite for Constant Tone Extension Enable characteristic."""

    @pytest.fixture
    def characteristic(self) -> ConstantToneExtensionEnableCharacteristic:
        return ConstantToneExtensionEnableCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2BAD"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(bytearray([0x00]), CTEEnableState.DISABLED, "Disabled"),
            CharacteristicTestData(bytearray([0x01]), CTEEnableState.ENABLED, "Enabled"),
        ]

    def test_roundtrip(self, characteristic: ConstantToneExtensionEnableCharacteristic) -> None:
        for val in CTEEnableState:
            encoded = characteristic.build_value(val)
            assert characteristic.parse_value(encoded) == val
