"""Training Status characteristic (0x2AD3)."""

from __future__ import annotations

from enum import IntEnum, IntFlag

import msgspec

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser

_MIN_STRING_OFFSET = 2  # Flags(1) + TrainingStatus(1)


class TrainingStatusFlags(IntFlag):
    """Training Status flags (uint8)."""

    TRAINING_STATUS_STRING_PRESENT = 0x01
    EXTENDED_STRING_PRESENT = 0x02


class TrainingStatusValue(IntEnum):
    """Training Status values per FTMS specification."""

    OTHER = 0x00
    IDLE = 0x01
    WARMING_UP = 0x02
    LOW_INTENSITY_INTERVAL = 0x03
    HIGH_INTENSITY_INTERVAL = 0x04
    RECOVERY_INTERVAL = 0x05
    ISOMETRIC = 0x06
    HEART_RATE_CONTROL = 0x07
    FITNESS_TEST = 0x08
    SPEED_OUTSIDE_OF_CONTROL_REGION_LOW = 0x09
    SPEED_OUTSIDE_OF_CONTROL_REGION_HIGH = 0x0A
    COOL_DOWN = 0x0B
    WATT_CONTROL = 0x0C
    MANUAL_MODE = 0x0D
    PRE_WORKOUT = 0x0E
    POST_WORKOUT = 0x0F


class TrainingStatusData(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods
    """Parsed data from Training Status characteristic.

    Contains flags, training status value, and an optional status string.
    """

    flags: TrainingStatusFlags
    training_status: TrainingStatusValue
    training_status_string: str | None = None


class TrainingStatusCharacteristic(BaseCharacteristic[TrainingStatusData]):
    """Training Status characteristic (0x2AD3).

    org.bluetooth.characteristic.training_status

    Reports the current training status of the fitness machine,
    including an optional descriptive string.
    """

    min_length = 2
    allow_variable_length = True

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> TrainingStatusData:
        """Parse Training Status data.

        Format: Flags (uint8) + Training Status (uint8) + optional string.

        Args:
            data: Raw bytearray from BLE characteristic.
            ctx: Optional CharacteristicContext (may be None).
            validate: Whether to validate ranges (default True).

        Returns:
            TrainingStatusData containing parsed training status.

        """
        flags_raw = DataParser.parse_int8(data, 0, signed=False)
        flags = TrainingStatusFlags(flags_raw)

        status_raw = DataParser.parse_int8(data, 1, signed=False)
        training_status = TrainingStatusValue(status_raw)

        training_status_string: str | None = None
        if flags & TrainingStatusFlags.TRAINING_STATUS_STRING_PRESENT and len(data) > _MIN_STRING_OFFSET:
            training_status_string = DataParser.parse_utf8_string(data[_MIN_STRING_OFFSET:])

        return TrainingStatusData(
            flags=flags,
            training_status=training_status,
            training_status_string=training_status_string,
        )

    def _encode_value(self, data: TrainingStatusData) -> bytearray:
        """Encode Training Status data to bytes.

        Args:
            data: TrainingStatusData instance.

        Returns:
            Encoded bytes representing the training status.

        """
        result = bytearray()
        result.extend(DataParser.encode_int8(int(data.flags), signed=False))
        result.extend(DataParser.encode_int8(int(data.training_status), signed=False))

        if data.training_status_string is not None:
            result.extend(data.training_status_string.encode("utf-8"))

        return result
