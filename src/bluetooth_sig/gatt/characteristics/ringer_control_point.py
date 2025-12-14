"""Ringer Control Point characteristic implementation."""

from __future__ import annotations

from enum import IntEnum

import msgspec

from .base import BaseCharacteristic


class RingerControlCommand(IntEnum):
    """Ringer Control Point command values."""

    SILENT_MODE = 1
    MUTE_ONCE = 2
    CANCEL_SILENT_MODE = 3


class RingerControlPointData(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods
    """Data for Ringer Control Point characteristic commands."""

    command: RingerControlCommand


class RingerControlPointCharacteristic(BaseCharacteristic):
    """Ringer Control Point characteristic (0x2A40).

    org.bluetooth.characteristic.ringer_control_point

    The Ringer Control Point characteristic defines the Control Point of Ringer.
    This is a write-only characteristic used to control ringer behaviour.

    Commands:
    - 1: Silent Mode (sets ringer to silent)
    - 2: Mute Once (silences ringer once)
    - 3: Cancel Silent Mode (sets ringer to normal)
    - 0, 4-255: Reserved for future use
    """

    min_length = 1
    expected_type = bytes

    def encode_value(self, data: RingerControlPointData) -> bytearray:
        """Encode RingerControlPointData command to bytes.

        Args:
            data: RingerControlPointData instance to encode

        Returns:
            Encoded bytes representing the ringer control command

        """
        return bytearray([data.command.value])

    # Note: This characteristic is write-only, so decode_value is not implemented
    # Reading this characteristic is not supported per Bluetooth SIG specification
