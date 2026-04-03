"""IDD Status characteristic (0x2B21).

Reports the current status of the Insulin Delivery Device including
therapy control state, operational state, and reservoir remaining.

References:
    Bluetooth SIG Insulin Delivery Service 1.0.1, Table 4.3
"""

from __future__ import annotations

from enum import IntEnum, IntFlag

import msgspec

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser, IEEE11073Parser


class TherapyControlState(IntEnum):
    """IDD therapy control state (Hamming-coded)."""

    UNDETERMINED = 0x0F
    STOP = 0x33
    PAUSE = 0x3C
    RUN = 0x55


class IDDOperationalState(IntEnum):
    """IDD operational state (Hamming-coded)."""

    UNDETERMINED = 0x0F
    OFF = 0x33
    STANDBY = 0x3C
    PREPARING = 0x55
    PRIMING = 0x5A
    WAITING = 0x66
    READY = 0x96


class IDDStatusFlags(IntFlag):
    """IDD Status flags (8-bit)."""

    RESERVOIR_ATTACHED = 0x01


class IDDStatusData(msgspec.Struct, frozen=True, kw_only=True):
    """Parsed data from IDD Status characteristic.

    Attributes:
        therapy_control_state: Current therapy control state.
        operational_state: Current operational state.
        reservoir_remaining: Reservoir remaining amount (SFLOAT).
        flags: Status flags.

    """

    therapy_control_state: TherapyControlState
    operational_state: IDDOperationalState
    reservoir_remaining: float
    flags: IDDStatusFlags


class IDDStatusCharacteristic(BaseCharacteristic[IDDStatusData]):
    """IDD Status characteristic (0x2B21).

    org.bluetooth.characteristic.idd_status

    Reports therapy control state, operational state, and
    reservoir remaining for an Insulin Delivery Device.
    """

    min_length = 5  # therapy(1) + operational(1) + reservoir_sfloat(2) + flags(1)
    allow_variable_length = True

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> IDDStatusData:
        """Parse IDD Status data.

        Format: TherapyControlState (uint8) + OperationalState (uint8) +
                ReservoirRemainingAmount (SFLOAT, 2 bytes) + Flags (uint8).
        """
        therapy_control_state = TherapyControlState(DataParser.parse_int8(data, 0, signed=False))
        operational_state = IDDOperationalState(DataParser.parse_int8(data, 1, signed=False))
        reservoir_remaining = IEEE11073Parser.parse_sfloat(data, 2)
        flags = IDDStatusFlags(DataParser.parse_int8(data, 4, signed=False))

        return IDDStatusData(
            therapy_control_state=therapy_control_state,
            operational_state=operational_state,
            reservoir_remaining=reservoir_remaining,
            flags=flags,
        )

    def _encode_value(self, data: IDDStatusData) -> bytearray:
        """Encode IDD Status data."""
        result = bytearray()
        result.extend(DataParser.encode_int8(int(data.therapy_control_state), signed=False))
        result.extend(DataParser.encode_int8(int(data.operational_state), signed=False))
        result.extend(IEEE11073Parser.encode_sfloat(data.reservoir_remaining))
        result.extend(DataParser.encode_int8(int(data.flags), signed=False))
        return result
