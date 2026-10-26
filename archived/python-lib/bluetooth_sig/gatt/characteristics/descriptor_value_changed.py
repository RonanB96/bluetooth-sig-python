"""Descriptor Value Changed characteristic (0x2A7D)."""

from __future__ import annotations

from enum import IntFlag

import msgspec

from ...types.uuid import BluetoothUUID
from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class DescriptorValueChangedFlags(IntFlag):
    """Descriptor Value Changed flags."""

    SOURCE_OF_CHANGE_DEVICE = 0x0001
    SOURCE_OF_CHANGE_EXTERNAL = 0x0002


class DescriptorValueChangedData(msgspec.Struct, frozen=True, kw_only=True):
    """Parsed data from Descriptor Value Changed characteristic."""

    flags: DescriptorValueChangedFlags
    characteristic_uuid: BluetoothUUID
    value: bytes


_ADDITIONAL_DATA_START_OFFSET = 4


class DescriptorValueChangedCharacteristic(BaseCharacteristic[DescriptorValueChangedData]):
    """Descriptor Value Changed characteristic (0x2A7D).

    org.bluetooth.characteristic.descriptor_value_changed

    Indicates that a descriptor value has changed. Contains flags,
    the UUID of the changed characteristic, and the new value.
    """

    min_length = 4
    allow_variable_length = True

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> DescriptorValueChangedData:
        flags = DescriptorValueChangedFlags(DataParser.parse_int16(data, 0, signed=False))
        characteristic_uuid = BluetoothUUID(DataParser.parse_int16(data, 2, signed=False))
        value = bytes(data[_ADDITIONAL_DATA_START_OFFSET:]) if len(data) > _ADDITIONAL_DATA_START_OFFSET else b""

        return DescriptorValueChangedData(
            flags=flags,
            characteristic_uuid=characteristic_uuid,
            value=value,
        )

    def _encode_value(self, data: DescriptorValueChangedData) -> bytearray:
        result = bytearray()
        result.extend(DataParser.encode_int16(int(data.flags), signed=False))
        result.extend(DataParser.encode_int16(int(data.characteristic_uuid.short_form, 16), signed=False))
        result.extend(data.value)
        return result
