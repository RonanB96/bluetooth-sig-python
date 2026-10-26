"""Sulfur Hexafluoride Concentration characteristic (0x2BD9)."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import IEEE11073FloatTemplate


class SulfurHexafluorideConcentrationCharacteristic(BaseCharacteristic[float]):
    """Sulfur Hexafluoride Concentration characteristic (0x2BD9).

    org.bluetooth.characteristic.sulfur_hexafluoride_concentration

    Concentration in kg/m³ using IEEE 11073 SFLOAT format (medfloat16).
    Special IEEE 11073 values NRes (out of range) and NaN (invalid/missing) are
    supported via the SFLOAT encoding.

    Raises:
        SpecialValueDetectedError: If raw value is a sentinel (NaN, NRes).
    """

    _template = IEEE11073FloatTemplate()
