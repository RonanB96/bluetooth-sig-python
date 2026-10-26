"""Object Properties characteristic implementation."""

from __future__ import annotations

from enum import IntFlag

from ...types.gatt_enums import CharacteristicRole
from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class ObjectProperties(IntFlag):
    """Object property flags as per OTS specification."""

    DELETE = 0x00000001
    EXECUTE = 0x00000002
    READ = 0x00000004
    WRITE = 0x00000008
    APPEND = 0x00000010
    TRUNCATE = 0x00000020
    PATCH = 0x00000040
    MARK = 0x00000080


class ObjectPropertiesCharacteristic(BaseCharacteristic[ObjectProperties]):
    """Object Properties characteristic (0x2AC4).

    org.bluetooth.characteristic.object_properties

    A 32-bit flags bitfield describing the properties of an object
    in the Object Transfer Service (OTS).
    """

    _manual_role = CharacteristicRole.INFO
    expected_length: int = 4  # uint32
    min_length: int = 4

    def _decode_value(
        self,
        data: bytearray,
        ctx: CharacteristicContext | None = None,
        *,
        validate: bool = True,
    ) -> ObjectProperties:
        """Parse object properties (uint32 flags).

        Args:
            data: Raw bytes (4 bytes).
            ctx: Optional CharacteristicContext.
            validate: Whether to validate ranges (default True).

        Returns:
            ObjectProperties flags.

        """
        raw = DataParser.parse_int32(data, 0, signed=False)
        return ObjectProperties(raw)

    def _encode_value(self, data: ObjectProperties) -> bytearray:
        """Encode object properties to bytes.

        Args:
            data: ObjectProperties flags.

        Returns:
            Encoded bytes (4 bytes).

        """
        return DataParser.encode_int32(int(data), signed=False)
