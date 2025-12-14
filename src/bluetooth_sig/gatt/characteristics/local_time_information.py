"""Local Time Information characteristic implementation."""

from __future__ import annotations

from enum import IntEnum

import msgspec

from ..constants import SINT8_MIN
from ..context import CharacteristicContext
from .base import BaseCharacteristic


class DSTOffset(IntEnum):
    """DST offset values as an IntEnum to avoid magic numbers.

    Values correspond to the Bluetooth SIG encoded DST offset values.
    """

    STANDARD = 0
    HALF_HOUR = 2
    DAYLIGHT = 4
    DOUBLE_DAYLIGHT = 8
    UNKNOWN = 255

    @property
    def description(self) -> str:
        """Human-readable description for this DST offset value."""
        return {
            DSTOffset.STANDARD: "Standard Time",
            DSTOffset.HALF_HOUR: "Half an hour Daylight Time",
            DSTOffset.DAYLIGHT: "Daylight Time",
            DSTOffset.DOUBLE_DAYLIGHT: "Double Daylight Time",
            DSTOffset.UNKNOWN: "DST offset unknown",
        }[self]

    @property
    def offset_hours(self) -> float | None:
        """Return the DST offset in hours (e.g. 0.5 for half hour), or None if unknown."""
        return {
            DSTOffset.STANDARD: 0.0,
            DSTOffset.HALF_HOUR: 0.5,
            DSTOffset.DAYLIGHT: 1.0,
            DSTOffset.DOUBLE_DAYLIGHT: 2.0,
            DSTOffset.UNKNOWN: None,
        }[self]


class TimezoneInfo(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods
    """Timezone information part of local time data."""

    description: str
    offset_hours: float | None
    raw_value: int


class DSTOffsetInfo(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods
    """DST offset information part of local time data."""

    description: str
    offset_hours: float | None
    raw_value: int


class LocalTimeInformationData(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods
    """Parsed data from Local Time Information characteristic."""

    timezone: TimezoneInfo
    dst_offset: DSTOffsetInfo
    total_offset_hours: float | None = None


class LocalTimeInformationCharacteristic(BaseCharacteristic):
    """Local Time Information characteristic (0x2A0F).

    org.bluetooth.characteristic.local_time_information

    Local time information characteristic.

    Represents the relation (offset) between local time and UTC.
    Contains time zone and Daylight Savings Time (DST) offset
    information.
    """

    expected_length: int = 2  # Timezone(1) + DST Offset(1)

    def decode_value(  # pylint: disable=too-many-locals
        self,
        data: bytearray,
        ctx: CharacteristicContext | None = None,
    ) -> LocalTimeInformationData:
        """Parse local time information data (2 bytes: time zone + DST offset).

        Args:
            data: Raw bytearray from BLE characteristic.
            ctx: Optional CharacteristicContext providing surrounding context (may be None).

        """
        if len(data) < 2:
            raise ValueError("Local time information data must be at least 2 bytes")

        # Parse time zone (sint8)
        timezone_raw = int.from_bytes(data[:1], byteorder="little", signed=True)

        # Parse DST offset (uint8)
        dst_offset_raw = data[1]

        # Process time zone
        if timezone_raw == SINT8_MIN:
            timezone_desc = "Unknown"
            timezone_hours = None
        elif -48 <= timezone_raw <= 56:
            # pylint: disable=duplicate-code
            # NOTE: UTC offset formatting is shared with TimeZoneCharacteristic.
            # Both use identical 15-minute increment conversion per Bluetooth SIG time spec.
            # Consolidation not practical as they're independent characteristics with different data structures.
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
        try:
            dst_enum = DSTOffset(dst_offset_raw)
            dst_desc = dst_enum.description
            dst_hours: float | None = dst_enum.offset_hours
        except ValueError:
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
        timezone_byte = data.timezone.raw_value.to_bytes(1, byteorder="little", signed=True)

        # Encode DST offset (use raw value directly)
        dst_offset_byte = data.dst_offset.raw_value.to_bytes(1, byteorder="little", signed=False)

        return bytearray(timezone_byte + dst_offset_byte)
