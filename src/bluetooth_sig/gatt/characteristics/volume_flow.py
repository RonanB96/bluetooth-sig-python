"""Volume Flow characteristic (0x2B22)."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import ScaledUint16Template


class VolumeFlowCharacteristic(BaseCharacteristic[float]):
    """Volume Flow characteristic (0x2B22).

    org.bluetooth.characteristic.volume_flow

    Volume flow in litres per second with a resolution of 0.001 (1 mL).
    M=1, d=-3, b=0 → scale factor 0.001.
    A value of 0xFFFF represents 'value is not known'.

    Raises:
        SpecialValueDetectedError: If raw value is a sentinel (e.g. 0xFFFF).
    """

    _template = ScaledUint16Template.from_letter_method(M=1, d=-3, b=0)
