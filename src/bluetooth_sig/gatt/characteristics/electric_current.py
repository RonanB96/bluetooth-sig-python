"""Electric Current characteristic implementation."""

from __future__ import annotations

from ...types.units import ElectricalUnit
from .base import BaseCharacteristic
from .templates import ScaledUint16Template


class ElectricCurrentCharacteristic(BaseCharacteristic):
    """Electric Current characteristic (0x2AEE).

    org.bluetooth.characteristic.electric_current

    Electric Current characteristic.

    Measures electric current with 0.01 A resolution.
    """

    _template = ScaledUint16Template.from_letter_method(M=1, d=-2, b=0)

    _manual_unit: str = ElectricalUnit.AMPS.value  # Override template's "units" default

    # Template configuration
    resolution: float = 0.01  # 0.01 A resolution
    max_value: float = 655.35  # 65535 * 0.01 A max
