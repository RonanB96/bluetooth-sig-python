"""Gain Settings Attribute characteristic (0x2B78)."""

from __future__ import annotations

import msgspec

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class GainSettingsAttributeData(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods
    """Parsed data from Gain Settings Attribute characteristic.

    Contains gain settings units (step size in 0.1 dB), minimum, and maximum values.
    """

    gain_setting_units: int
    gain_setting_minimum: int
    gain_setting_maximum: int


class GainSettingsAttributeCharacteristic(BaseCharacteristic[GainSettingsAttributeData]):
    """Gain Settings Attribute characteristic (0x2B78).

    org.bluetooth.characteristic.gain_settings_attribute

    Reports the gain settings properties including units, minimum,
    and maximum values.
    """

    expected_length = 3

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> GainSettingsAttributeData:
        """Parse Gain Settings Attribute data.

        Format: units (uint8) + minimum (sint8) + maximum (sint8).
        """
        units = DataParser.parse_int8(data, 0, signed=False)
        minimum = DataParser.parse_int8(data, 1, signed=True)
        maximum = DataParser.parse_int8(data, 2, signed=True)
        return GainSettingsAttributeData(
            gain_setting_units=units,
            gain_setting_minimum=minimum,
            gain_setting_maximum=maximum,
        )

    def _encode_value(self, data: GainSettingsAttributeData) -> bytearray:
        """Encode Gain Settings Attribute data to bytes."""
        result = bytearray()
        result += DataParser.encode_int8(data.gain_setting_units)
        result += DataParser.encode_int8(data.gain_setting_minimum, signed=True)
        result += DataParser.encode_int8(data.gain_setting_maximum, signed=True)
        return result
