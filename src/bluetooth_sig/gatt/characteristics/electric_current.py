"""Electric Current characteristic implementation."""

from .base import BaseCharacteristic
from .templates import ScaledUint16Template


class ElectricCurrentCharacteristic(BaseCharacteristic):
    """Electric Current characteristic.

    Measures electric current with 0.01 A resolution.
    """

    _template = ScaledUint16Template()

    _characteristic_name: str = "Electric Current"
    _manual_unit: str = "A"  # Override template's "units" default

    # Template configuration
    resolution: float = 0.01  # 0.01 A resolution
    max_value: float = 655.35  # 65535 * 0.01 A max
