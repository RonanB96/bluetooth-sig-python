"""Reference Time Information characteristic (0x2A14) implementation.

Provides information about the reference time source, including its type,
accuracy, and time since last update.

Based on Bluetooth SIG GATT Specification:
- Reference Time Information: 4 bytes (Time Source + Time Accuracy + Days Since Update + Hours Since Update)
- Time Source: uint8 (0=Unknown, 1=NTP, 2=GPS, etc.)
- Time Accuracy: uint8 (0-253 in 125ms steps, 254=out of range, 255=unknown)
- Days Since Update: uint8 (0-254, 255 means >=255 days)
- Hours Since Update: uint8 (0-23, 255 means >=255 days)
"""

from __future__ import annotations

from enum import IntEnum

import msgspec

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser

# Bluetooth SIG Reference Time Information characteristic constants
REFERENCE_TIME_INFO_LENGTH = 4  # Total characteristic length in bytes
TIME_SOURCE_MAX = 7  # Maximum valid time source value (0-7)
HOURS_SINCE_UPDATE_MAX = 23  # Maximum valid hours value (0-23)
HOURS_SINCE_UPDATE_OUT_OF_RANGE = 255  # Special value indicating >=255 days


class TimeSource(IntEnum):
    """Time source enumeration per Bluetooth SIG specification."""

    UNKNOWN = 0
    NETWORK_TIME_PROTOCOL = 1
    GPS = 2
    RADIO_TIME_SIGNAL = 3
    MANUAL = 4
    ATOMIC_CLOCK = 5
    CELLULAR_NETWORK = 6
    NOT_SYNCHRONIZED = 7


class ReferenceTimeInformationData(msgspec.Struct):
    """Reference Time Information characteristic data structure."""

    time_source: TimeSource
    time_accuracy: int  # 0-253 (in 125ms steps), 254=out of range, 255=unknown
    days_since_update: int  # 0-254, 255 means >=255 days
    hours_since_update: int  # 0-23, 255 means >=255 days


class ReferenceTimeInformationCharacteristic(BaseCharacteristic[ReferenceTimeInformationData]):
    """Reference Time Information characteristic (0x2A14).

    Represents information about the reference time source including type,
    accuracy, and time elapsed since last synchronization.

    Structure (4 bytes):
    - Time Source: uint8 (0=Unknown, 1=NTP, 2=GPS, 3=Radio, 4=Manual, 5=Atomic, 6=Cellular, 7=Not Sync)
    - Time Accuracy: uint8 (0-253 in 125ms steps, 254=out of range >31.625s, 255=unknown)
    - Days Since Update: uint8 (0-254 days, 255 means >=255 days)
    - Hours Since Update: uint8 (0-23 hours, 255 means >=255 days)

    Used by Current Time Service (0x1805).
    """

    expected_length: int = 4  # Time Source(1) + Time Accuracy(1) + Days(1) + Hours(1)

    def _decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> ReferenceTimeInformationData:
        """Decode Reference Time Information data from bytes.

        Args:
            data: Raw characteristic data (4 bytes)
            ctx: Optional characteristic context

        Returns:
            ReferenceTimeInformationData with all fields

        Raises:
            ValueError: If data is insufficient or contains invalid values

        """
        if len(data) < REFERENCE_TIME_INFO_LENGTH:
            raise ValueError(
                f"Insufficient data for Reference Time Information: "
                f"expected {REFERENCE_TIME_INFO_LENGTH} bytes, got {len(data)}"
            )

        # Parse Time Source (1 byte)
        time_source_raw = DataParser.parse_int8(data, 0, signed=False)
        time_source = _validate_time_source(time_source_raw)

        # Parse Time Accuracy (1 byte) - no validation needed, all values 0-255 valid
        time_accuracy = DataParser.parse_int8(data, 1, signed=False)

        # Parse Days Since Update (1 byte) - no validation needed, all values 0-255 valid
        days_since_update = DataParser.parse_int8(data, 2, signed=False)

        # Parse Hours Since Update (1 byte)
        hours_since_update = DataParser.parse_int8(data, 3, signed=False)
        _validate_hours_since_update(hours_since_update)

        return ReferenceTimeInformationData(
            time_source=time_source,
            time_accuracy=time_accuracy,
            days_since_update=days_since_update,
            hours_since_update=hours_since_update,
        )

    def _encode_value(self, data: ReferenceTimeInformationData) -> bytearray:
        """Encode Reference Time Information data to bytes.

        Args:
            data: ReferenceTimeInformationData to encode

        Returns:
            Encoded reference time information (4 bytes)

        Raises:
            ValueError: If data contains invalid values

        """
        result = bytearray()

        # Encode Time Source (1 byte)
        time_source_value = int(data.time_source)
        _validate_time_source(time_source_value)  # Validate before encoding
        result.append(time_source_value)

        # Encode Time Accuracy (1 byte) - all values 0-255 valid
        result.append(data.time_accuracy)

        # Encode Days Since Update (1 byte) - all values 0-255 valid
        result.append(data.days_since_update)

        # Encode Hours Since Update (1 byte)
        _validate_hours_since_update(data.hours_since_update)
        result.append(data.hours_since_update)

        return result


def _validate_time_source(time_source_raw: int) -> TimeSource:
    """Validate time source value.

    Args:
        time_source_raw: Raw time source value (0-255)

    Returns:
        TimeSource enum value

    Raises:
        ValueError: If time source is in reserved range (8-254)

    """
    if TIME_SOURCE_MAX < time_source_raw < HOURS_SINCE_UPDATE_OUT_OF_RANGE:
        raise ValueError(f"Invalid time source: {time_source_raw} (valid range: 0-{TIME_SOURCE_MAX})")
    return TimeSource(time_source_raw) if time_source_raw <= TIME_SOURCE_MAX else TimeSource.UNKNOWN


def _validate_hours_since_update(hours: int) -> None:
    """Validate hours since update value.

    Args:
        hours: Hours since update value (0-255)

    Raises:
        ValueError: If hours is invalid (24-254)

    """
    if hours > HOURS_SINCE_UPDATE_MAX and hours != HOURS_SINCE_UPDATE_OUT_OF_RANGE:
        raise ValueError(
            f"Invalid hours since update: {hours} "
            f"(valid range: 0-{HOURS_SINCE_UPDATE_MAX} or {HOURS_SINCE_UPDATE_OUT_OF_RANGE} for >=255 days)"
        )
