"""Average Current characteristic implementation."""

from __future__ import annotations

from ...types.units import ElectricalUnit
from .base import BaseCharacteristic
from .templates import ScaledUint16Template


class AverageCurrentCharacteristic(BaseCharacteristic):
    """Average Current characteristic (0x2AE0).

    org.bluetooth.characteristic.average_current

    Average Current characteristic.

    Measures average electric current with 0.01 A resolution.
    """

    _template = ScaledUint16Template.from_letter_method(M=1, d=-2, b=0)

    _manual_unit: str = ElectricalUnit.AMPS.value  # Override template's "units" default
    resolution: float = 0.01
