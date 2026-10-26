"""Chromaticity Tolerance characteristic (0x2AE6)."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import ScaledUint8Template


class ChromaticityToleranceCharacteristic(BaseCharacteristic[float]):
    """Chromaticity Tolerance characteristic (0x2AE6).

    org.bluetooth.characteristic.chromaticity_tolerance

    Unitless chromaticity tolerance value.
    M=1, d=-4, b=0 -> resolution 0.0001 (0-0.0255).
    """

    _template = ScaledUint8Template.from_letter_method(M=1, d=-4, b=0)
