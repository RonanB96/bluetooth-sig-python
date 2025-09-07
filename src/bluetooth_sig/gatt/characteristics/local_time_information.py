"""Local Time Information characteristic implementation."""

from __future__ import annotations

from dataclasses import dataclass

from .base import BaseCharacteristic


@dataclass
class TimezoneInfo:
    """Timezone information part of local time data."""

    description: str
    offset_hours: float | None
    raw_value: int


@dataclass
class DSTOffsetInfo:
    """DST offset information part of local time data."""

    description: str
    offset_hours: float | None
    raw_value: int


@dataclass
class LocalTimeInformationData:
    """Parsed data from Local Time Information characteristic."""

    timezone: TimezoneInfo
    dst_offset: DSTOffsetInfo
    total_offset_hours: float | None = None


@dataclass
class LocalTimeInformationCharacteristic(BaseCharacteristic):
    """Local time information characteristic.

    Represents the relation (offset) between local time and UTC.
    Contains time zone and Daylight Savings Time (DST) offset information.
    """

    _characteristic_name: str = "Local Time Information"

    # DST offset mappings
    DST_OFFSET_VALUES = {
        0: {"description": "Standard Time", "offset_hours": 0.0},
        2: {"description": "Half an hour Daylight Time", "offset_hours": 0.5},
        4: {"description": "Daylight Time", "offset_hours": 1.0},
        8: {"description": "Double Daylight Time", "offset_hours": 2.0},
        255: {"description": "DST offset unknown", "offset_hours": None},
    }

    def decode_value(self, data: bytearray) -> LocalTimeInformationData:  # pylint: disable=too-many-locals
        """Parse local time information data (2 bytes: time zone + DST offset)."""
        if len(data) < 2:
            raise ValueError("Local time information data must be at least 2 bytes")

        # Parse time zone (sint8)
        timezone_raw = int.from_bytes(data[:1], byteorder="little", signed=True)

        # Parse DST offset (uint8)
        dst_offset_raw = data[1]

        # Process time zone
        if timezone_raw == -128:
            timezone_desc = "Unknown"
            timezone_hours = None
        elif -48 <= timezone_raw <= 56:
            total_minutes = timezone_raw * 15
            hours = total_minutes // 60
            minutes = abs(total_minutes % 60)
            sign = "+" if total_minutes >= 0 else "-"
            hours_abs = abs(hours)

            if minutes == 0:
                timezone_desc = f"UTC{sign}{hours_abs:02d}:00"
            else:
                timezone_desc = f"UTC{sign}{hours_abs:02d}:{minutes:02d}"
            timezone_hours = total_minutes / 60
        else:
            timezone_desc = f"Reserved (value: {timezone_raw})"
            timezone_hours = None

        # Process DST offset
        if dst_offset_raw in self.DST_OFFSET_VALUES:
            dst_info = self.DST_OFFSET_VALUES[dst_offset_raw]
            dst_desc = dst_info["description"]
            dst_hours = dst_info["offset_hours"]
        else:
            dst_desc = f"Reserved (value: {dst_offset_raw})"
            dst_hours = None

        # Create timezone info
        timezone_info = TimezoneInfo(
            description=timezone_desc,
            offset_hours=timezone_hours,
            raw_value=timezone_raw,
        )

        # Create DST offset info
        dst_offset_info = DSTOffsetInfo(
            description=dst_desc,
            offset_hours=dst_hours,
            raw_value=dst_offset_raw,
        )

        # Calculate total offset if both are known
        total_offset = None
        if timezone_hours is not None and dst_hours is not None:
            total_offset = timezone_hours + dst_hours

        return LocalTimeInformationData(
            timezone=timezone_info,
            dst_offset=dst_offset_info,
            total_offset_hours=total_offset,
        )

    def encode_value(self, data: LocalTimeInformationData) -> bytearray:
        """Encode LocalTimeInformationData back to bytes.

        Args:
            data: LocalTimeInformationData instance to encode

        Returns:
            Encoded bytes representing the local time information
        """
        # Encode timezone (use raw value directly)
        timezone_byte = data.timezone.raw_value.to_bytes(
            1, byteorder="little", signed=True
        )

        # Encode DST offset (use raw value directly)
        dst_offset_byte = data.dst_offset.raw_value.to_bytes(
            1, byteorder="little", signed=False
        )

        return bytearray(timezone_byte + dst_offset_byte)

    @property
    def unit(self) -> str:
        """Get the unit of measurement."""
        return ""  # No unit for time information
