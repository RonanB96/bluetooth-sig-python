"""Electric Current characteristic implementation."""

from dataclasses import dataclass

from .templates import ScaledUint16Characteristic


@dataclass
class ElectricCurrentCharacteristic(ScaledUint16Characteristic):
    """Electric Current characteristic.

    Measures electric current with 0.01 A resolution.
    """

    _characteristic_name: str = "Electric Current"

    # Template configuration
    resolution: float = 0.01  # 0.01 A resolution
    measurement_unit: str = "A"
    max_value: float = 655.35  # 65535 * 0.01 A max
