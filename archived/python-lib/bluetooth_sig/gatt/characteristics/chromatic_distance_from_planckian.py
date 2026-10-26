"""Chromatic Distance from Planckian characteristic (0x2AE3)."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import ScaledSint16Template


class ChromaticDistanceFromPlanckianCharacteristic(BaseCharacteristic[float]):
    """Chromatic Distance from Planckian characteristic (0x2AE3).

    org.bluetooth.characteristic.chromatic_distance_from_planckian

    Unitless distance from the Planckian locus.
    M=1, d=-5, b=0 -> resolution 0.00001 (-0.05 to 0.05).
    A value of 0x7FFF represents 'value is not valid'.
    A value of 0x7FFE represents 'value is not known'.

    Raises:
        SpecialValueDetectedError: If raw value is a sentinel (e.g. 0x7FFF).
    """

    _template = ScaledSint16Template.from_letter_method(M=1, d=-5, b=0)
