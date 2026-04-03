"""Tests for Constant Tone Extension Enable characteristic (0x2BAD)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.constant_tone_extension_enable import (
    ConstantToneExtensionEnableCharacteristic,
    CTEEnableFlags,
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
            CharacteristicTestData(bytearray([0x00]), CTEEnableFlags(0), "All disabled"),
            CharacteristicTestData(bytearray([0x01]), CTEEnableFlags.AOA_ACL, "AoA on ACL only"),
            CharacteristicTestData(bytearray([0x02]), CTEEnableFlags.AOD_ADVERTISING, "AoD advertising only"),
            CharacteristicTestData(
                bytearray([0x03]),
                CTEEnableFlags.AOA_ACL | CTEEnableFlags.AOD_ADVERTISING,
                "Both AoA and AoD enabled",
            ),
        ]
