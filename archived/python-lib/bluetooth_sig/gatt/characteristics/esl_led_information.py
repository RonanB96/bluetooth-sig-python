"""ESL LED Information characteristic implementation."""

from __future__ import annotations

from enum import IntFlag

import msgspec

from ...types.gatt_enums import CharacteristicRole
from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class ESLColorGamut(IntFlag):
    """ESL LED colour gamut flags per ESL specification."""

    RED = 0x01
    GREEN = 0x02
    BLUE = 0x04


class ESLLEDInformationData(msgspec.Struct, frozen=True, kw_only=True):
    """Parsed data from ESL LED Information characteristic.

    Attributes:
        led_index: Index of the LED (0-based).
        color_gamut: Colour gamut bitfield indicating supported colours.

    """

    led_index: int
    color_gamut: ESLColorGamut


class ESLLEDInformationCharacteristic(BaseCharacteristic[ESLLEDInformationData]):
    """ESL LED Information characteristic (0x2BFD).

    org.bluetooth.characteristic.esl_led_information

    Describes an ESL LED: index and colour gamut bitfield (Red, Green, Blue).
    """

    _characteristic_name = "ESL LED Information"
    _manual_role = CharacteristicRole.INFO
    expected_length: int = 2  # led_index(1) + color_gamut(1)
    min_length: int = 2

    def _decode_value(
        self,
        data: bytearray,
        ctx: CharacteristicContext | None = None,
        *,
        validate: bool = True,
    ) -> ESLLEDInformationData:
        """Parse ESL LED information.

        Args:
            data: Raw bytes (2 bytes).
            ctx: Optional CharacteristicContext.
            validate: Whether to validate ranges (default True).

        Returns:
            ESLLEDInformationData with LED details.

        """
        led_index = DataParser.parse_int8(data, 0, signed=False)
        color_gamut = ESLColorGamut(DataParser.parse_int8(data, 1, signed=False))
        return ESLLEDInformationData(led_index=led_index, color_gamut=color_gamut)

    def _encode_value(self, data: ESLLEDInformationData) -> bytearray:
        """Encode ESL LED information to bytes.

        Args:
            data: ESLLEDInformationData to encode.

        Returns:
            Encoded bytes (2 bytes).

        """
        result = DataParser.encode_int8(data.led_index, signed=False)
        result.extend(DataParser.encode_int8(int(data.color_gamut), signed=False))
        return result
