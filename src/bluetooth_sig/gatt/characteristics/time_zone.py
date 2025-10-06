"""Time Zone characteristic implementation."""

from __future__ import annotations

from typing import Any

from ...types.gatt_enums import ValueType
from ..constants import SINT8_MIN
from .base import BaseCharacteristic


class TimeZoneCharacteristic(BaseCharacteristic):
    """Time zone characteristic.

    Represents the time difference in 15-minute increments between local
    standard time and UTC.
    """

    _characteristic_name: str = "Time Zone"
    # Manual override: YAML indicates sint8->int but we return descriptive strings
    _manual_value_type: ValueType | str | None = ValueType.STRING

    def decode_value(self, data: bytearray, _ctx: Any | None = None) -> str:
        """Parse time zone data (sint8 in 15-minute increments from UTC)."""
        if len(data) < 1:
            raise ValueError("Time zone data must be at least 1 byte")

        # Parse sint8 value
        offset_raw = int.from_bytes(data[:1], byteorder="little", signed=True)

        # Handle special values
        if offset_raw == SINT8_MIN:
            return "Unknown"

        # Validate range (-48 to +56 per specification)
        if offset_raw < -48 or offset_raw > 56:
            return f"Reserved (value: {offset_raw})"

        # Convert 15-minute increments to hours and minutes
        total_minutes = offset_raw * 15
        hours = total_minutes // 60
        minutes = abs(total_minutes % 60)

        # Format as UTC offset
        sign = "+" if total_minutes >= 0 else "-"
        hours_abs = abs(hours)

        if minutes == 0:
            return f"UTC{sign}{hours_abs:02d}:00"
        return f"UTC{sign}{hours_abs:02d}:{minutes:02d}"

    def encode_value(self, data: str | int) -> bytearray:
        """Encode time zone value back to bytes.

        Args:
            data: Time zone offset either as string (e.g., "UTC+05:30") or as raw sint8 value

        Returns:
            Encoded bytes representing the time zone (sint8, 15-minute increments)
        """
        if isinstance(data, int):
            # Direct raw value
            offset_raw = data
        elif isinstance(data, str):
            # Parse string format
            if data == "Unknown":
                offset_raw = SINT8_MIN
            elif data.startswith("UTC"):
                # Parse UTC offset format like "UTC+05:30" or "UTC-03:00"
                try:
                    offset_str = data[3:]  # Remove "UTC" prefix
                    if offset_str[0] not in ["+", "-"]:
                        raise ValueError("Invalid timezone format")

                    sign = 1 if offset_str[0] == "+" else -1
                    time_part = offset_str[1:]

                    if ":" in time_part:
                        hours_str, minutes_str = time_part.split(":")
                        hours = int(hours_str)
                        minutes = int(minutes_str)
                    else:
                        hours = int(time_part)
                        minutes = 0

                    # Convert to 15-minute increments
                    total_minutes = sign * (hours * 60 + minutes)
                    offset_raw = total_minutes // 15

                except (ValueError, IndexError) as e:
                    raise ValueError(f"Invalid time zone format: {data}") from e
            else:
                raise ValueError(f"Invalid time zone format: {data}")
        else:
            raise TypeError("Time zone data must be a string or integer")

        # Validate range for sint8 (SINT8_MIN to SINT8_MAX, but spec says -48 to +56 + special SINT8_MIN)
        if offset_raw != SINT8_MIN and not -48 <= offset_raw <= 56:
            raise ValueError(
                f"Time zone offset {offset_raw} is outside valid range (-48 to +56, or SINT8_MIN for unknown)"
            )

        return bytearray(offset_raw.to_bytes(1, byteorder="little", signed=True))
