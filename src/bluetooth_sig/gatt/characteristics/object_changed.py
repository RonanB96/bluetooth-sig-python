"""Object Changed characteristic implementation."""

from __future__ import annotations

from enum import IntFlag

import msgspec

from ...types.gatt_enums import CharacteristicRole
from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class ObjectChangedFlags(IntFlag):
    """Object Changed flags per OTS specification."""

    SOURCE_OF_CHANGE = 0x01
    CHANGE_OCCURRED = 0x02
    OBJECT_CONTENTS_CHANGED = 0x04
    OBJECT_METADATA_CHANGED = 0x08
    OBJECT_CREATION = 0x10
    OBJECT_DELETION = 0x20


class ObjectChangedData(msgspec.Struct, frozen=True, kw_only=True):
    """Parsed data from Object Changed characteristic.

    Attributes:
        flags: Change flags indicating what changed.
        object_id: 48-bit object identifier.

    """

    flags: ObjectChangedFlags
    object_id: int


class ObjectChangedCharacteristic(BaseCharacteristic[ObjectChangedData]):
    """Object Changed characteristic (0x2AC8).

    org.bluetooth.characteristic.object_changed

    Notification-only characteristic indicating changes to objects in
    the Object Transfer Service (OTS). Contains flags describing the
    change and the 48-bit object ID of the affected object.
    """

    _manual_role = CharacteristicRole.STATUS
    expected_length: int = 7  # flags(1) + object_id(6)
    min_length: int = 7

    def _decode_value(
        self,
        data: bytearray,
        ctx: CharacteristicContext | None = None,
        *,
        validate: bool = True,
    ) -> ObjectChangedData:
        """Parse object changed data.

        Args:
            data: Raw bytes (7 bytes).
            ctx: Optional CharacteristicContext.
            validate: Whether to validate ranges (default True).

        Returns:
            ObjectChangedData with flags and object_id.

        """
        flags = ObjectChangedFlags(DataParser.parse_int8(data, 0, signed=False))
        object_id = DataParser.parse_int48(data, 1, signed=False)
        return ObjectChangedData(flags=flags, object_id=object_id)

    def _encode_value(self, data: ObjectChangedData) -> bytearray:
        """Encode object changed data to bytes.

        Args:
            data: ObjectChangedData to encode.

        Returns:
            Encoded bytes (7 bytes).

        """
        result = DataParser.encode_int8(int(data.flags), signed=False)
        result.extend(DataParser.encode_int48(data.object_id, signed=False))
        return result
