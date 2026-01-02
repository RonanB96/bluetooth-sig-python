"""Chromaticity Coordinate characteristic implementation."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import ScaledUint16Template


class ChromaticityCoordinateCharacteristic(BaseCharacteristic):
    """Chromaticity Coordinate characteristic (0x2B1C).

    org.bluetooth.characteristic.chromaticity_coordinate

    Represents chromaticity coordinate with resolution 1/65535.
    """

    _template = ScaledUint16Template.from_letter_method(M=1, d=0, b=-16)
