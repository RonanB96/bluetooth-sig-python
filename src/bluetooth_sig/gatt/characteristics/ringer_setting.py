"""Ringer Setting characteristic implementation."""

from __future__ import annotations

from enum import IntEnum

import msgspec

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class RingerSetting(IntEnum):
    """Ringer Setting enumeration values."""

    RINGER_SILENT = 0
    RINGER_NORMAL = 1


class RingerSettingData(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods
    """Parsed data from Ringer Setting characteristic."""

    setting: RingerSetting


class RingerSettingCharacteristic(BaseCharacteristic[RingerSettingData]):
    """Ringer Setting characteristic (0x2A41).

    org.bluetooth.characteristic.ringer_setting

    The Ringer Setting characteristic defines the Setting of the Ringer.
    Value 0: Ringer Silent
    Value 1: Ringer Normal
    Values 2-255: Reserved for future use
    """

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> RingerSettingData:
        """Parse ringer setting data according to Bluetooth specification.

        Args:
            data: Raw bytearray from BLE characteristic.
            ctx: Optional CharacteristicContext (unused)

        Returns:
            RingerSettingData containing parsed ringer setting.

        Raises:
            ValueError: If data format is invalid.

        """
        setting_byte = DataParser.parse_int8(data, 0, signed=False)

        try:
            setting = RingerSetting(setting_byte)
        except ValueError as e:
            raise ValueError(f"Invalid ringer setting value: {setting_byte}") from e

        return RingerSettingData(setting=setting)

    def _encode_value(self, data: RingerSettingData) -> bytearray:
        """Encode RingerSettingData back to bytes.

        Args:
            data: RingerSettingData instance to encode

        Returns:
            Encoded bytes representing the ringer setting

        """
        return bytearray([data.setting.value])
