"""Tests for RingerSettingCharacteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.ringer_setting import (
    RingerSetting,
    RingerSettingCharacteristic,
    RingerSettingData,
)
from bluetooth_sig.gatt.exceptions import CharacteristicParseError
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestRingerSettingCharacteristic(CommonCharacteristicTests):
    """Test suite for RingerSettingCharacteristic."""

    @pytest.fixture
    def characteristic(self) -> RingerSettingCharacteristic:
        return RingerSettingCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2A41"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00]),
                expected_value=RingerSettingData(setting=RingerSetting.RINGER_SILENT),
                description="Ringer silent",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x01]),
                expected_value=RingerSettingData(setting=RingerSetting.RINGER_NORMAL),
                description="Ringer normal",
            ),
        ]

    def test_reserved_value_rejected(self, characteristic: RingerSettingCharacteristic) -> None:
        """Test that reserved values (2-255) are rejected."""
        with pytest.raises(CharacteristicParseError):
            characteristic.parse_value(bytearray([0x02]))

    def test_reserved_high_value_rejected(self, characteristic: RingerSettingCharacteristic) -> None:
        """Test that high reserved value 0xFF is rejected."""
        with pytest.raises(CharacteristicParseError):
            characteristic.parse_value(bytearray([0xFF]))
