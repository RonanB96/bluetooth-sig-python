"""Object Size characteristic implementation."""

from __future__ import annotations

import msgspec

from ...types.gatt_enums import CharacteristicRole
from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class ObjectSizeData(msgspec.Struct, frozen=True, kw_only=True):
    """Parsed data from Object Size characteristic.

    Attributes:
        current_size: Current size of the object in bytes.
        allocated_size: Allocated size for the object in bytes.

    """

    current_size: int
    allocated_size: int


class ObjectSizeCharacteristic(BaseCharacteristic[ObjectSizeData]):
    """Object Size characteristic (0x2AC0).

    org.bluetooth.characteristic.object_size

    Two uint32 fields representing the current size and allocated size
    of an object in the Object Transfer Service (OTS).
    """

    _manual_role = CharacteristicRole.INFO
    expected_length: int = 8  # uint32 + uint32
    min_length: int = 8

    def _decode_value(
        self,
        data: bytearray,
        ctx: CharacteristicContext | None = None,
        *,
        validate: bool = True,
    ) -> ObjectSizeData:
        """Parse object size (two uint32 fields).

        Args:
            data: Raw bytes (8 bytes).
            ctx: Optional CharacteristicContext.
            validate: Whether to validate ranges (default True).

        Returns:
            ObjectSizeData with current_size and allocated_size.

        """
        current_size = DataParser.parse_int32(data, 0, signed=False)
        allocated_size = DataParser.parse_int32(data, 4, signed=False)
        return ObjectSizeData(current_size=current_size, allocated_size=allocated_size)

    def _encode_value(self, data: ObjectSizeData) -> bytearray:
        """Encode object size to bytes.

        Args:
            data: ObjectSizeData to encode.

        Returns:
            Encoded bytes (8 bytes).

        """
        result = DataParser.encode_int32(data.current_size, signed=False)
        result.extend(DataParser.encode_int32(data.allocated_size, signed=False))
        return result
