"""Time Zone characteristic implementation."""

from dataclasses import dataclass

from .base import BaseCharacteristic


@dataclass
class TimeZoneCharacteristic(BaseCharacteristic):
    """Time zone characteristic.

    Represents the time difference in 15-minute increments between
    local standard time and UTC.
    """

    _characteristic_name: str = "Time Zone"
    # Manual override: YAML indicates sint8->int but we return descriptive strings
    _manual_value_type: str = "string"

    def parse_value(self, data: bytearray) -> str:
        """Parse time zone data (sint8 in 15-minute increments from UTC)."""
        if len(data) < 1:
            raise ValueError("Time zone data must be at least 1 byte")

        # Parse sint8 value
        offset_raw = int.from_bytes(data[:1], byteorder="little", signed=True)

        # Handle special values
        if offset_raw == -128:
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

    def encode_value(self, data) -> bytearray:
        """Encode value back to bytes - basic stub implementation."""
        # TODO: Implement proper encoding
        raise NotImplementedError(
            "encode_value not yet implemented for this characteristic"
        )

    @property
    def unit(self) -> str:
        """Get the unit of measurement."""
        return ""  # No unit for time zone offset
