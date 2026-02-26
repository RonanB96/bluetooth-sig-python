"""Torque characteristic (0x2B21)."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import ScaledSint32Template


class TorqueCharacteristic(BaseCharacteristic[float]):
    """Torque characteristic (0x2B21).

    org.bluetooth.characteristic.torque

    Torque in Newton metres with a resolution of 0.01 Nm.
    M=1, d=-2, b=0 → scale factor 0.01.
    Positive = clockwise around the given axis.
    A value of 0x7FFFFFFF represents 'value is not known'.

    Raises:
        SpecialValueDetectedError: If raw value is a sentinel (e.g. 0x7FFFFFFF).
    """

    _template = ScaledSint32Template.from_letter_method(M=1, d=-2, b=0)
