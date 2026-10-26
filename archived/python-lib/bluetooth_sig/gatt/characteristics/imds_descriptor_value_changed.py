"""IMDS Descriptor Value Changed characteristic (0x2C0D).

Indicates changes to descriptors in the Industrial Monitoring Device Service.

References:
    Bluetooth SIG Industrial Monitoring Device Service
"""

from __future__ import annotations

from enum import IntFlag

import msgspec

from ...types.gatt_enums import CharacteristicRole
from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class IMDSDescriptorChangeFlags(IntFlag):
    """IMDS Descriptor Value Changed flags (uint16)."""

    SOURCE_OF_CHANGE = 0x0001
    CHARACTERISTIC_VALUE_CHANGED = 0x0002
    DESCRIPTOR_VALUE_CHANGED = 0x0004
    ADDITIONAL_DESCRIPTORS_CHANGED = 0x0008


class IMDSDescriptorValueChangedData(msgspec.Struct, frozen=True, kw_only=True):
    """Parsed data from IMDS Descriptor Value Changed characteristic.

    Attributes:
        flags: Change indication flags.
        characteristic_uuid: UUID of the changed characteristic (uint16).
    """

    flags: IMDSDescriptorChangeFlags
    characteristic_uuid: int


class IMDSDescriptorValueChangedCharacteristic(BaseCharacteristic[IMDSDescriptorValueChangedData]):
    """IMDS Descriptor Value Changed characteristic (0x2C0D).

    org.bluetooth.characteristic.imds_descriptor_value_changed

    Indicates which descriptors have changed and for which characteristic.
    """

    _manual_role = CharacteristicRole.STATUS
    min_length = 4  # flags(2) + uuid(2)

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> IMDSDescriptorValueChangedData:
        """Parse IMDS Descriptor Value Changed data.

        Format: Flags (uint16 LE) + Characteristic_UUID (uint16 LE).
        """
        flags = IMDSDescriptorChangeFlags(DataParser.parse_int16(data, 0, signed=False))
        characteristic_uuid = DataParser.parse_int16(data, 2, signed=False)

        return IMDSDescriptorValueChangedData(
            flags=flags,
            characteristic_uuid=characteristic_uuid,
        )

    def _encode_value(self, data: IMDSDescriptorValueChangedData) -> bytearray:
        """Encode IMDS Descriptor Value Changed data."""
        result = bytearray()
        result.extend(DataParser.encode_int16(int(data.flags), signed=False))
        result.extend(DataParser.encode_int16(data.characteristic_uuid, signed=False))
        return result
