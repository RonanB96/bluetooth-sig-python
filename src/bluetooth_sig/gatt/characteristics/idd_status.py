"""IDD Status characteristic (0x2B21).

Reports the current status of the Insulin Delivery Device including
therapy control state, operational state, and reservoir remaining.

References:
    Bluetooth SIG Insulin Delivery Service 1.0
"""

from __future__ import annotations

from enum import IntEnum

import msgspec

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class TherapyControlState(IntEnum):
    """IDD therapy control state."""

    UNDETERMINED = 0x00
    STOP = 0x01
    PAUSE = 0x02
    RUN = 0x03


class IDDOperationalState(IntEnum):
    """IDD operational state."""

    PREPARING = 0x00
    IDLE = 0x01
    DELIVERING = 0x02
    PAUSED = 0x03
    STOPPED = 0x04
    ERROR = 0x05


class IDDStatusData(msgspec.Struct, frozen=True, kw_only=True):
    """Parsed data from IDD Status characteristic.

    Attributes:
        therapy_control_state: Current therapy control state.
        operational_state: Current operational state.
        reservoir_remaining: Reservoir remaining in insulin units (IU x 100).

    """

    therapy_control_state: TherapyControlState
    operational_state: IDDOperationalState
    reservoir_remaining: int


class IDDStatusCharacteristic(BaseCharacteristic[IDDStatusData]):
    """IDD Status characteristic (0x2B21).

    org.bluetooth.characteristic.idd_status

    Reports therapy control state, operational state, and
    reservoir remaining for an Insulin Delivery Device.
    """

    min_length = 4  # therapy(1) + operational(1) + reservoir(2)
    allow_variable_length = True

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> IDDStatusData:
        """Parse IDD Status data.

        Format: TherapyControlState (uint8) + OperationalState (uint8) +
                ReservoirRemaining (uint16 LE).
        """
        therapy_control_state = TherapyControlState(DataParser.parse_int8(data, 0, signed=False))
        operational_state = IDDOperationalState(DataParser.parse_int8(data, 1, signed=False))
        reservoir_remaining = DataParser.parse_int16(data, 2, signed=False)

        return IDDStatusData(
            therapy_control_state=therapy_control_state,
            operational_state=operational_state,
            reservoir_remaining=reservoir_remaining,
        )

    def _encode_value(self, data: IDDStatusData) -> bytearray:
        """Encode IDD Status data."""
        result = bytearray()
        result.extend(DataParser.encode_int8(int(data.therapy_control_state), signed=False))
        result.extend(DataParser.encode_int8(int(data.operational_state), signed=False))
        result.extend(DataParser.encode_int16(data.reservoir_remaining, signed=False))
        return result
