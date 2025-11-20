"""Time Update State characteristic (0x2A17) implementation."""

from __future__ import annotations

from enum import IntEnum

import msgspec

from bluetooth_sig.types.context import CharacteristicContext

from .base import BaseCharacteristic


class TimeUpdateState(msgspec.Struct, kw_only=True):
    """Time Update State data structure."""

    current_state: TimeUpdateCurrentState
    result: TimeUpdateResult


class TimeUpdateCurrentState(IntEnum):
    """Time Update Current State values."""

    IDLE = 0x00
    PENDING = 0x01
    UPDATING = 0x02


class TimeUpdateResult(IntEnum):
    """Time Update Result values."""

    SUCCESSFUL = 0x00
    CANCELED = 0x01
    NO_CONNECTION_TO_REFERENCE = 0x02
    REFERENCE_RESPONDED_WITH_ERROR = 0x03
    TIMEOUT = 0x04
    UPDATE_NOT_ATTEMPTED_AFTER_RESET = 0x05


class TimeUpdateStateCharacteristic(BaseCharacteristic):
    """Time Update State characteristic.

    Indicates the current state of time update operations.

    Value: 2 bytes
    - Current State: uint8 (0=Idle, 1=Pending, 2=Updating)
    - Result: uint8 (0=Successful, 1=Canceled, etc.)
    """

    def __init__(self) -> None:
        """Initialize the Time Update State characteristic."""
        super().__init__()

    def decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> TimeUpdateState:
        """Decode the raw data to TimeUpdateState."""
        if len(data) != 2:
            raise ValueError(f"Time Update State requires 2 bytes, got {len(data)}")

        current_state = TimeUpdateCurrentState(data[0])
        result = TimeUpdateResult(data[1])

        return TimeUpdateState(current_state=current_state, result=result)

    def encode_value(self, data: TimeUpdateState) -> bytearray:
        """Encode TimeUpdateState to bytes."""
        return bytearray([int(data.current_state), int(data.result)])
