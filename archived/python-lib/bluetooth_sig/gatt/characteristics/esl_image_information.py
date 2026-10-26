"""ESL Image Information characteristic implementation."""

from __future__ import annotations

from enum import IntEnum

import msgspec

from ...types.gatt_enums import CharacteristicRole
from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class ESLImageType(IntEnum):
    """ESL image type identifiers per ESL Service spec."""

    BLACK_WHITE = 0x00
    THREE_GRAY_SCALE = 0x01
    FOUR_GRAY_SCALE = 0x02
    EIGHT_GRAY_SCALE = 0x03
    SIXTEEN_GRAY_SCALE = 0x04
    RED_BLACK_WHITE = 0x05
    YELLOW_BLACK_WHITE = 0x06
    FULL_COLOR = 0x07


class ESLImageInformationData(msgspec.Struct, frozen=True, kw_only=True):
    """Parsed data from ESL Image Information characteristic.

    Attributes:
        image_index: Index of the image slot (0-based).
        max_width: Maximum image width in pixels.
        max_height: Maximum image height in pixels.
        image_type: Image type identifier (codec/format).

    """

    image_index: int
    max_width: int
    max_height: int
    image_type: ESLImageType


class ESLImageInformationCharacteristic(BaseCharacteristic[ESLImageInformationData]):
    """ESL Image Information characteristic (0x2BFB).

    org.bluetooth.characteristic.esl_image_information

    Describes an ESL image slot: index, maximum width, maximum height,
    and image type.
    """

    _manual_role = CharacteristicRole.INFO
    expected_length: int = 6  # image_index(1) + max_width(2) + max_height(2) + image_type(1)
    min_length: int = 6

    def _decode_value(
        self,
        data: bytearray,
        ctx: CharacteristicContext | None = None,
        *,
        validate: bool = True,
    ) -> ESLImageInformationData:
        """Parse ESL image information.

        Args:
            data: Raw bytes (6 bytes).
            ctx: Optional CharacteristicContext.
            validate: Whether to validate ranges (default True).

        Returns:
            ESLImageInformationData with image slot details.

        """
        image_index = DataParser.parse_int8(data, 0, signed=False)
        max_width = DataParser.parse_int16(data, 1, signed=False)
        max_height = DataParser.parse_int16(data, 3, signed=False)
        image_type = DataParser.parse_int8(data, 5, signed=False)
        return ESLImageInformationData(
            image_index=image_index,
            max_width=max_width,
            max_height=max_height,
            image_type=ESLImageType(image_type),
        )

    def _encode_value(self, data: ESLImageInformationData) -> bytearray:
        """Encode ESL image information to bytes.

        Args:
            data: ESLImageInformationData to encode.

        Returns:
            Encoded bytes (6 bytes).

        """
        result = DataParser.encode_int8(data.image_index, signed=False)
        result.extend(DataParser.encode_int16(data.max_width, signed=False))
        result.extend(DataParser.encode_int16(data.max_height, signed=False))
        result.extend(DataParser.encode_int8(int(data.image_type), signed=False))
        return result
