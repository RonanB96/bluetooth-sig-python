"""Tests for GainSettingsAttributeCharacteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.gain_settings_attribute import (
    GainSettingsAttributeCharacteristic,
    GainSettingsAttributeData,
    GainSettingsUnits,
)
from tests.gatt.characteristics.test_characteristic_common import (
    CharacteristicTestData,
    CommonCharacteristicTests,
)


class TestGainSettingsAttributeCharacteristic(CommonCharacteristicTests):
    @pytest.fixture
    def characteristic(self) -> GainSettingsAttributeCharacteristic:
        return GainSettingsAttributeCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2B78"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x01, 0xF6, 0x0A]),
                expected_value=GainSettingsAttributeData(
                    gain_setting_units=GainSettingsUnits.DECIBELS,
                    gain_setting_minimum=-10,
                    gain_setting_maximum=10,
                ),
                description="Decibels, range -10 to +10",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x00, 0x64]),
                expected_value=GainSettingsAttributeData(
                    gain_setting_units=GainSettingsUnits.UNITLESS,
                    gain_setting_minimum=0,
                    gain_setting_maximum=100,
                ),
                description="Unitless, range 0 to 100",
            ),
        ]
