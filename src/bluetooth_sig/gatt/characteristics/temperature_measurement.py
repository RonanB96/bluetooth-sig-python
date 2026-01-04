"""Temperature Measurement characteristic implementation."""

from __future__ import annotations

from datetime import datetime
from enum import IntFlag

import msgspec

from bluetooth_sig.types.units import TemperatureUnit

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import IEEE11073Parser


class TemperatureMeasurementFlags(IntFlag):
    """Temperature Measurement flags as per Bluetooth SIG specification."""

    CELSIUS_UNIT = 0x00
    FAHRENHEIT_UNIT = 0x01
    TIMESTAMP_PRESENT = 0x02
    TEMPERATURE_TYPE_PRESENT = 0x04


class TemperatureMeasurementData(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods
    """Parsed temperature measurement data."""

    temperature: float
    unit: TemperatureUnit
    flags: TemperatureMeasurementFlags
    timestamp: datetime | None = None
    temperature_type: int | None = None

    def __post_init__(self) -> None:
        """Validate temperature measurement data."""
        if self.unit not in (TemperatureUnit.CELSIUS, TemperatureUnit.FAHRENHEIT):
            raise ValueError(f"Temperature unit must be CELSIUS or FAHRENHEIT, got {self.unit}")


class TemperatureMeasurementCharacteristic(BaseCharacteristic[TemperatureMeasurementData]):
    """Temperature Measurement characteristic (0x2A1C).

    Used in Health Thermometer Service for medical temperature readings.
    Different from Environmental Temperature (0x2A6E).
    """

    # Declarative validation attributes
    min_length: int | None = 5  # Flags(1) + Temperature(4) minimum
    max_length: int | None = 13  # + Timestamp(7) + TemperatureType(1) maximum
    allow_variable_length: bool = True  # Variable optional fields

    def _decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> TemperatureMeasurementData:  # pylint: disable=too-many-locals
        """Parse temperature measurement data according to Bluetooth specification.

        Format: Flags(1) + Temperature Value(4) + [Timestamp(7)] + [Temperature Type(1)].
        Temperature is medfloat32 (IEEE 11073 medical float format).

        Args:
            data: Raw bytearray from BLE characteristic.
            ctx: Optional context providing surrounding characteristic metadata when available.

        Returns:
            TemperatureMeasurementData containing parsed temperature data with metadata.

        """
        if len(data) < 5:
            raise ValueError("Temperature Measurement data must be at least 5 bytes")

        flags = TemperatureMeasurementFlags(data[0])

        # Parse temperature value (medfloat32 - IEEE 11073 medical float format)
        temp_value = IEEE11073Parser.parse_float32(data, 1)

        # Check temperature unit flag (bit 0)
        unit = (
            TemperatureUnit.FAHRENHEIT
            if TemperatureMeasurementFlags.FAHRENHEIT_UNIT in flags
            else TemperatureUnit.CELSIUS
        )

        # Parse optional fields
        timestamp: datetime | None = None
        temperature_type: int | None = None
        offset = 5

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

    def _encode_value(self, data: TemperatureMeasurementData) -> bytearray:
        """Encode temperature measurement value back to bytes.

        Args:
            data: TemperatureMeasurementData containing temperature measurement data

        Returns:
            Encoded bytes representing the temperature measurement

        """
        # Build flags
        flags = TemperatureMeasurementFlags(0)
        if data.unit == TemperatureUnit.FAHRENHEIT:
            flags |= TemperatureMeasurementFlags.FAHRENHEIT_UNIT
        if data.timestamp is not None:
            flags |= TemperatureMeasurementFlags.TIMESTAMP_PRESENT
        if data.temperature_type is not None:
            flags |= TemperatureMeasurementFlags.TEMPERATURE_TYPE_PRESENT

        # Start with flags byte
        result = bytearray([int(flags)])

        # Add temperature value (medfloat32 - IEEE 11073 medical float format)
        temp_bytes = IEEE11073Parser.encode_float32(data.temperature)
        result.extend(temp_bytes)

        # Add optional timestamp (7 bytes) if present
        if data.timestamp is not None:
            result.extend(IEEE11073Parser.encode_timestamp(data.timestamp))

        # Add optional temperature type (1 byte) if present
        if data.temperature_type is not None:
            result.append(int(data.temperature_type))

        return result
