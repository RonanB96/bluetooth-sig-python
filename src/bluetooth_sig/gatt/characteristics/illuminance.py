"""Illuminance characteristic implementation."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import ScaledUint24Template

# pylint: disable=duplicate-code
# Justification: This file follows the standard BLE characteristic base class pattern,
# which is intentionally duplicated across multiple characteristic implementations.
# These patterns are required by Bluetooth SIG specifications and represent legitimate
# code duplication for protocol compliance.


class IlluminanceCharacteristic(BaseCharacteristic):
    """Illuminance characteristic (0x2AFB).

    Measures light intensity in lux (lumens per square meter).
    Uses uint24 (3 bytes) with 0.01 lux resolution.
    """

    _template = ScaledUint24Template(scale_factor=0.01)

    _manual_unit: str = "lx"  # Override template's "units" default
    resolution: float = 0.01
