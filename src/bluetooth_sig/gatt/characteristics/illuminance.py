"""Illuminance characteristic implementation."""

from dataclasses import dataclass, field

from .templates import Uint24ScaledCharacteristic

# pylint: disable=duplicate-code
# Justification: This file follows the standard BLE characteristic base class pattern,
# which is intentionally duplicated across multiple characteristic implementations.
# These patterns are required by Bluetooth SIG specifications and represent legitimate
# code duplication for protocol compliance.


@dataclass
class IlluminanceCharacteristic(Uint24ScaledCharacteristic):
    """Illuminance characteristic (0x2AFB).

    Measures light intensity in lux (lumens per square meter).
    """

    _characteristic_name: str = "Illuminance"
    _manual_unit: str | None = field(default="lx", init=False)  # Override template's "units" default
    resolution: float = 0.01
