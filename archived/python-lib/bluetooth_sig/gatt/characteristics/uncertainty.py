"""Uncertainty characteristic implementation.

IPS v1.0 §3.8: uint8 bitfield encoding stationary indicator,
update time, and position precision.
"""

from __future__ import annotations

import msgspec

from ..context import CharacteristicContext
from .base import BaseCharacteristic

# IPS v1.0 §3.8: Lookup table for update-time and precision sub-fields.
# Index = 3-bit value (0-7), value = round(e^(1.35 * index)).
_EXP_LOOKUP: tuple[int, ...] = (1, 4, 5, 7, 10, 14, 20, 28)


class UncertaintyData(msgspec.Struct, frozen=True, kw_only=True):
    """Parsed Uncertainty bitfield per IPS v1.0 §3.8.

    Attributes:
        stationary: False if the transmitter is stationary, True if mobile.
        update_time: Estimated time between position updates (seconds).
        precision: Estimated position precision (decimetres).
    """

    stationary: bool
    update_time: int
    precision: int


class UncertaintyCharacteristic(BaseCharacteristic[UncertaintyData]):
    """Uncertainty characteristic (0x2AB4).

    org.bluetooth.characteristic.uncertainty

    IPS v1.0 §3.8: uint8 bitfield.
      Bit 0:   Stationary (0 = stationary, 1 = mobile)
      Bits 1-3: Update Time - encoded as round(e^(1.35 * value)) seconds
      Bits 4-6: Precision  - encoded as round(e^(1.35 * value)) decimetres
      Bit 7:   RFU
    """

    expected_length = 1
    min_length = 1
    max_length = 1
    _is_bitfield = True

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> UncertaintyData:
        """Decode Uncertainty bitfield per IPS v1.0 §3.8."""
        raw = data[0]
        stationary = bool(raw & 0x01)
        update_time_idx = (raw >> 1) & 0x07
        precision_idx = (raw >> 4) & 0x07
        return UncertaintyData(
            stationary=stationary,
            update_time=_EXP_LOOKUP[update_time_idx],
            precision=_EXP_LOOKUP[precision_idx],
        )

    def _encode_value(self, value: UncertaintyData) -> bytearray:
        """Encode Uncertainty bitfield per IPS v1.0 §3.8."""
        update_idx = _EXP_LOOKUP.index(value.update_time)
        precision_idx = _EXP_LOOKUP.index(value.precision)
        raw = (int(value.stationary) & 0x01) | ((update_idx & 0x07) << 1) | ((precision_idx & 0x07) << 4)
        return bytearray([raw])
