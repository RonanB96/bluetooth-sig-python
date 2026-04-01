"""Intermediate Temperature characteristic (0x2A1E).

Reports the intermediate temperature measurement.

References:
    Bluetooth SIG Assigned Numbers / GATT Service Specifications
"""

from __future__ import annotations

from datetime import datetime
from enum import IntFlag

import msgspec

from bluetooth_sig.types.units import TemperatureUnit

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import IEEE11073Parser


class IntermediateTemperatureFlags(IntFlag):
    """Intermediate Temperature flags as per Bluetooth SIG specification."""

    CELSIUS_UNIT = 0x00
    FAHRENHEIT_UNIT = 0x01
    TIMESTAMP_PRESENT = 0x02
    TEMPERATURE_TYPE_PRESENT = 0x04


class IntermediateTemperatureData(msgspec.Struct, frozen=True, kw_only=True):
    """Parsed intermediate temperature data."""

    temperature: float
    unit: TemperatureUnit
    flags: IntermediateTemperatureFlags
    timestamp: datetime | None = None
    temperature_type: int | None = None


class IntermediateTemperatureCharacteristic(BaseCharacteristic[IntermediateTemperatureData]):
    """Intermediate Temperature characteristic (0x2A1E).

    org.bluetooth.characteristic.intermediate_temperature

    Same structure as Temperature Measurement: Flags(1) + Temperature(4) + [Timestamp(7)] + [Type(1)].
    """

    min_length: int | None = 5
    max_length: int | None = 13
    allow_variable_length: bool = True

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> IntermediateTemperatureData:
        """Parse intermediate temperature data.

        Format: Flags(1) + Temperature Value(4) + [Timestamp(7)] + [Temperature Type(1)].
        """
        flags = IntermediateTemperatureFlags(data[0])
        temp_value = IEEE11073Parser.parse_float32(data, 1)
        unit = (
            TemperatureUnit.FAHRENHEIT
            if IntermediateTemperatureFlags.FAHRENHEIT_UNIT in flags
            else TemperatureUnit.CELSIUS
        )

        timestamp: datetime | None = None
        temperature_type: int | None = None
        offset = 5

        if IntermediateTemperatureFlags.TIMESTAMP_PRESENT in flags and len(data) >= offset + 7:
            timestamp = IEEE11073Parser.parse_timestamp(data, offset)
            offset += 7

        if IntermediateTemperatureFlags.TEMPERATURE_TYPE_PRESENT in flags and len(data) >= offset + 1:
            temperature_type = data[offset]

        return IntermediateTemperatureData(
            temperature=temp_value,
            unit=unit,
            flags=flags,
            timestamp=timestamp,
            temperature_type=temperature_type,
        )

    def _encode_value(self, data: IntermediateTemperatureData) -> bytearray:
        """Encode intermediate temperature value back to bytes."""
        flags = IntermediateTemperatureFlags(0)
        if data.unit == TemperatureUnit.FAHRENHEIT:
            flags |= IntermediateTemperatureFlags.FAHRENHEIT_UNIT
        if data.timestamp is not None:
            flags |= IntermediateTemperatureFlags.TIMESTAMP_PRESENT
        if data.temperature_type is not None:
            flags |= IntermediateTemperatureFlags.TEMPERATURE_TYPE_PRESENT

        result = bytearray([int(flags)])
        result.extend(IEEE11073Parser.encode_float32(data.temperature))

        if data.timestamp is not None:
            result.extend(IEEE11073Parser.encode_timestamp(data.timestamp))

        if data.temperature_type is not None:
            result.append(int(data.temperature_type))

        return result
