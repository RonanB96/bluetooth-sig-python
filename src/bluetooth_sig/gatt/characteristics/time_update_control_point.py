"""Time Update Control Point characteristic (0x2A16) implementation."""

from __future__ import annotations

from enum import IntEnum

from bluetooth_sig.types.context import CharacteristicContext

from .base import BaseCharacteristic
from .templates import Uint8Template


class TimeUpdateControlPointCommand(IntEnum):
    """Time Update Control Point commands."""

    GET_REFERENCE_UPDATE = 0x01
    CANCEL_REFERENCE_UPDATE = 0x02


class TimeUpdateControlPointCharacteristic(BaseCharacteristic[TimeUpdateControlPointCommand]):
    """Time Update Control Point characteristic.

    Allows a client to request or cancel reference time updates.

    Value: uint8 command
    - 0x01: Get Reference Time Update
    - 0x02: Cancel Reference Time Update
    """

    def __init__(self) -> None:
        """Initialize the Time Update Control Point characteristic."""
        super().__init__()
        self._template = Uint8Template()

    def _decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> TimeUpdateControlPointCommand:
        """Decode the raw data to TimeUpdateControlPointCommand."""
        if self._template is None:
            raise RuntimeError("Template not initialized")
        value = self._template._decode_value(data)  # pylint: disable=protected-access
        try:
            return TimeUpdateControlPointCommand(value)
        except ValueError as e:
            raise ValueError(f"Invalid Time Update Control Point command: {value}") from e

    def _encode_value(self, data: TimeUpdateControlPointCommand) -> bytearray:
        """Encode TimeUpdateControlPointCommand to bytes."""
        if self._template is None:
            raise RuntimeError("Template not initialized")
        return self._template._encode_value(int(data))  # pylint: disable=protected-access
