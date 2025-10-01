"""Electric Current characteristic implementation."""

from dataclasses import dataclass, field

from .templates import ScaledUint16Characteristic


@dataclass
class ElectricCurrentCharacteristic(ScaledUint16Characteristic):
    """Electric Current characteristic.

    Measures electric current with 0.01 A resolution.
    """

    _characteristic_name: str = "Electric Current"
    _manual_unit: str | None = field(default="A", init=False)  # Override template's "units" default

    # Template configuration
    resolution: float = 0.01  # 0.01 A resolution
    max_value: float = 655.35  # 65535 * 0.01 A max
