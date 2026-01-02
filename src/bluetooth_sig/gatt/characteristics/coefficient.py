"""Coefficient characteristic implementation."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import Float32Template


class CoefficientCharacteristic(BaseCharacteristic):
    """Coefficient characteristic (0x2AFA).

    org.bluetooth.characteristic.coefficient

    Represents a coefficient value using IEEE-754 32-bit float.
    """

    _template = Float32Template()
