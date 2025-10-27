"""Temperature Measurement characteristic implementation."""

from __future__ import annotations

from datetime import datetime
from enum import IntFlag

import msgspec

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser, IEEE11073Parser


class TemperatureMeasurementFlags(IntFlag):
    """Temperature Measurement flags as per Bluetooth SIG specification."""

    CELSIUS_UNIT = 0x00
    FAHRENHEIT_UNIT = 0x01
    TIMESTAMP_PRESENT = 0x02
    TEMPERATURE_TYPE_PRESENT = 0x04


class TemperatureMeasurementData(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods
    """Parsed temperature measurement data."""

    temperature: float
    unit: str
    flags: TemperatureMeasurementFlags
    timestamp: datetime | None = None
    temperature_type: int | None = None


class TemperatureMeasurementCharacteristic(BaseCharacteristic):
    """Temperature Measurement characteristic (0x2A1C).

    Used in Health Thermometer Service for medical temperature readings.
    Different from Environmental Temperature (0x2A6E).
    """

    # Declarative validation attributes
    min_length: int | None = 3  # Flags(1) + Temperature(2) minimum
    max_length: int | None = 11  # + Timestamp(7) + TemperatureType(1) maximum
    allow_variable_length: bool = True  # Variable optional fields

    def decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> TemperatureMeasurementData:  # pylint: disable=too-many-locals
        """Parse temperature measurement data according to Bluetooth specification.

        Format: Flags(1) + Temperature Value(2) + [Timestamp(7)] + [Temperature Type(1)].
        Temperature is sint16 with 0.01 °C resolution.

        Args:
            data: Raw bytearray from BLE characteristic.
            ctx: Optional context providing surrounding characteristic metadata when available.

        Returns:
            TemperatureMeasurementData containing parsed temperature data with metadata.

        """
        if len(data) < 3:
            raise ValueError("Temperature Measurement data must be at least 3 bytes")

        flags = TemperatureMeasurementFlags(data[0])

        # Parse temperature value (sint16, 0.01 °C resolution)
        temp_value = DataParser.parse_int16(data, 1, signed=True) * 0.01

        # Check temperature unit flag (bit 0)
        unit = "°F" if TemperatureMeasurementFlags.FAHRENHEIT_UNIT in flags else "°C"

        # Parse optional fields
        timestamp: datetime | None = None
        temperature_type: int | None = None
        offset = 3

        if TemperatureMeasurementFlags.TIMESTAMP_PRESENT in flags and len(data) >= offset + 7:
            timestamp = IEEE11073Parser.parse_timestamp(data, offset)
            offset += 7

        if TemperatureMeasurementFlags.TEMPERATURE_TYPE_PRESENT in flags and len(data) >= offset + 1:
            temperature_type = data[offset]

        # Create immutable struct with all values
        return TemperatureMeasurementData(
            temperature=temp_value,
            unit=unit,
            flags=flags,
            timestamp=timestamp,
            temperature_type=temperature_type,
        )

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

        # Add temperature value (sint16, 0.01 °C resolution)
        temp_raw = int(data.temperature / 0.01)
        temp_bytes = DataParser.encode_int16(temp_raw, signed=True)
        result.extend(temp_bytes)

        # Add optional timestamp (7 bytes) if present
        if data.timestamp is not None:
            result.extend(IEEE11073Parser.encode_timestamp(data.timestamp))

        # Add optional temperature type (1 byte) if present
        if data.temperature_type is not None:
            result.append(int(data.temperature_type))

        return result
