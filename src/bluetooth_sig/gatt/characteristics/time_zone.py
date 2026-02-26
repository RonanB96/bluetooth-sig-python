"""Time Zone characteristic implementation."""

from __future__ import annotations

from ..constants import SINT8_MIN
from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser

# Timezone offsets (15-minute increments from UTC)
TIMEZONE_OFFSET_MIN = -48  # Minimum timezone offset in 15-minute increments (UTC-12:00)
TIMEZONE_OFFSET_MAX = 56  # Maximum timezone offset in 15-minute increments (UTC+14:00)


class TimeZoneCharacteristic(BaseCharacteristic[str]):
    """Time Zone characteristic (0x2A0E).

    org.bluetooth.characteristic.time_zone

    Time zone characteristic.

    Represents the time difference in 15-minute increments between local
    standard time and UTC.
    """

    # Manual override: YAML indicates sint8->int but we return descriptive strings
    _python_type: type | str | None = str
    min_length: int = 1

    def _decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True) -> str:
        """Parse time zone data (sint8 in 15-minute increments from UTC)."""
        # Parse sint8 value
        offset_raw = DataParser.parse_int8(data, 0, signed=True)

        # Handle special values
        if offset_raw == SINT8_MIN:
            return "Unknown"

        # Validate range (TIMEZONE_OFFSET_MIN to TIMEZONE_OFFSET_MAX per specification)
        if offset_raw < TIMEZONE_OFFSET_MIN or offset_raw > TIMEZONE_OFFSET_MAX:
            return f"Reserved (value: {offset_raw})"

        # Convert 15-minute increments to hours and minutes
        # pylint: disable=duplicate-code
        # NOTE: UTC offset formatting is shared with LocalTimeInformationCharacteristic.
        # Both use identical 15-minute increment conversion and formatting per Bluetooth SIG time spec.
        # Consolidation not practical as they're independent characteristics with different data structures.
        total_minutes = offset_raw * 15
        hours = total_minutes // 60
        minutes = abs(total_minutes % 60)

        # Format as UTC offset
        sign = "+" if total_minutes >= 0 else "-"
        hours_abs = abs(hours)

        if minutes == 0:
            return f"UTC{sign}{hours_abs:02d}:00"
        return f"UTC{sign}{hours_abs:02d}:{minutes:02d}"

    def _encode_value(self, data: str | int) -> bytearray:
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
                offset_str = data[3:]  # Remove "UTC" prefix
                if not offset_str or offset_str[0] not in ["+", "-"]:
                    raise ValueError("Invalid timezone format")

                try:
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

        # Validate range for sint8 (SINT8_MIN to SINT8_MAX)
        # Spec allows TIMEZONE_OFFSET_MIN to TIMEZONE_OFFSET_MAX + special SINT8_MIN for unknown
        if offset_raw != SINT8_MIN and not TIMEZONE_OFFSET_MIN <= offset_raw <= TIMEZONE_OFFSET_MAX:
            raise ValueError(
                f"Time zone offset {offset_raw} is outside valid range "
                f"({TIMEZONE_OFFSET_MIN} to {TIMEZONE_OFFSET_MAX}, or SINT8_MIN for unknown)"
            )

        return bytearray(DataParser.encode_int8(offset_raw, signed=True))
