"""Temperature Measurement characteristic implementation."""

from __future__ import annotations

from datetime import datetime
from enum import IntFlag

import msgspec

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import IEEE11073Parser


class TemperatureMeasurementFlags(IntFlag):
    """Temperature Measurement flags as per Bluetooth SIG specification."""

    FAHRENHEIT_UNIT = 0x01
    TIMESTAMP_PRESENT = 0x02
    TEMPERATURE_TYPE_PRESENT = 0x04


class TemperatureMeasurementData(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods
    """Parsed temperature measurement data."""

    temperature: float
    unit: str
    flags: int
    timestamp: datetime | None = None
    temperature_type: int | None = None


class TemperatureMeasurementCharacteristic(BaseCharacteristic):
    """Temperature Measurement characteristic (0x2A1C).

    Used in Health Thermometer Service for medical temperature readings.
    Different from Environmental Temperature (0x2A6E).
    """

    # Declarative validation attributes
    min_length: int | None = 5  # Flags(1) + Temperature(4) minimum
    max_length: int | None = 13  # + Timestamp(7) + TemperatureType(1) maximum
    allow_variable_length: bool = True  # Variable optional fields

    def decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> TemperatureMeasurementData:  # pylint: disable=too-many-locals
        """Parse temperature measurement data according to Bluetooth
        specification.

        Format: Flags(1) + Temperature Value(4) + [Timestamp(7)] + [Temperature Type(1)]
        Temperature is IEEE-11073 32-bit float.

        Args:
            data: Raw bytearray from BLE characteristic

        Returns:
            TemperatureMeasurementData containing parsed temperature data with metadata
        """
        if len(data) < 5:
            raise ValueError("Temperature Measurement data must be at least 5 bytes")

        flags = TemperatureMeasurementFlags(data[0])

        # Parse temperature value (IEEE-11073 32-bit float)
        temp_value = IEEE11073Parser.parse_float32(data, 1)

        # Check temperature unit flag (bit 0)
        unit = "°F" if TemperatureMeasurementFlags.FAHRENHEIT_UNIT in flags else "°C"

        result = TemperatureMeasurementData(temperature=temp_value, unit=unit, flags=int(flags))

        # Parse optional timestamp (7 bytes) if present
        offset = 5
        if TemperatureMeasurementFlags.TIMESTAMP_PRESENT in flags and len(data) >= offset + 7:
            result.timestamp = IEEE11073Parser.parse_timestamp(data, offset)
            offset += 7

        # Parse optional temperature type (1 byte) if present
        if TemperatureMeasurementFlags.TEMPERATURE_TYPE_PRESENT in flags and len(data) >= offset + 1:
            result.temperature_type = data[offset]

        return result

    def encode_value(self, data: TemperatureMeasurementData) -> bytearray:
        """Encode temperature measurement value back to bytes.

        Args:
            data: TemperatureMeasurementData containing temperature measurement data

        Returns:
            Encoded bytes representing the temperature measurement
        """
        # Build flags
        flags = TemperatureMeasurementFlags(0)
        if data.unit == "°F":
            flags |= TemperatureMeasurementFlags.FAHRENHEIT_UNIT
        if data.timestamp is not None:
            flags |= TemperatureMeasurementFlags.TIMESTAMP_PRESENT
        if data.temperature_type is not None:
            flags |= TemperatureMeasurementFlags.TEMPERATURE_TYPE_PRESENT

        # Start with flags byte
        result = bytearray([int(flags)])

        # Add temperature value (IEEE-11073 32-bit float)
        temp_bytes = IEEE11073Parser.encode_float32(data.temperature)
        result.extend(temp_bytes)

        # Add optional timestamp (7 bytes) if present
        if data.timestamp is not None:
            result.extend(IEEE11073Parser.encode_timestamp(data.timestamp))

        # Add optional temperature type (1 byte) if present
        if data.temperature_type is not None:
            result.append(int(data.temperature_type))

        return result
