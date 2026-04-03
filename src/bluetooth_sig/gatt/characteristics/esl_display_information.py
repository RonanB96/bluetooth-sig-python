"""ESL Display Information characteristic implementation."""

from __future__ import annotations

from enum import IntEnum

import msgspec

from ...types.gatt_enums import CharacteristicRole
from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class ESLDisplayType(IntEnum):
    """ESL display type values per ESL specification."""

    BLACK_WHITE = 0x01
    THREE_GRAY = 0x02
    FOUR_GRAY = 0x03
    EIGHT_GRAY = 0x04
    SIXTEEN_GRAY = 0x05
    COLOR_RGB = 0x06


class ESLDisplayInformationData(msgspec.Struct, frozen=True, kw_only=True):
    """Parsed data from ESL Display Information characteristic.

    Attributes:
        display_index: Index of the display (0-based).
        width: Display width in pixels.
        height: Display height in pixels.
        display_type: Type of display technology.

    """

    display_index: int
    width: int
    height: int
    display_type: ESLDisplayType


class ESLDisplayInformationCharacteristic(BaseCharacteristic[ESLDisplayInformationData]):
    """ESL Display Information characteristic (0x2BFA).

    org.bluetooth.characteristic.esl_display_information

    Describes an ESL display: index, width, height, and display type.
    """

    _manual_role = CharacteristicRole.INFO
    expected_length: int = 6  # display_index(1) + width(2) + height(2) + display_type(1)
    min_length: int = 6

    def _decode_value(
        self,
        data: bytearray,
        ctx: CharacteristicContext | None = None,
        *,
        validate: bool = True,
    ) -> ESLDisplayInformationData:
        """Parse ESL display information.

        Args:
            data: Raw bytes (6 bytes).
            ctx: Optional CharacteristicContext.
            validate: Whether to validate ranges (default True).

        Returns:
            ESLDisplayInformationData with display details.

        """
        display_index = DataParser.parse_int8(data, 0, signed=False)
        width = DataParser.parse_int16(data, 1, signed=False)
        height = DataParser.parse_int16(data, 3, signed=False)
        display_type = ESLDisplayType(DataParser.parse_int8(data, 5, signed=False))
        return ESLDisplayInformationData(
            display_index=display_index,
            width=width,
            height=height,
            display_type=display_type,
        )

    def _encode_value(self, data: ESLDisplayInformationData) -> bytearray:
        """Encode ESL display information to bytes.

        Args:
            data: ESLDisplayInformationData to encode.

        Returns:
            Encoded bytes (6 bytes).

        """
        result = DataParser.encode_int8(data.display_index, signed=False)
        result.extend(DataParser.encode_int16(data.width, signed=False))
        result.extend(DataParser.encode_int16(data.height, signed=False))
        result.extend(DataParser.encode_int8(int(data.display_type), signed=False))
        return result
