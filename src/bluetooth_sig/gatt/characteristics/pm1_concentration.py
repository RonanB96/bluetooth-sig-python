"""PM1 Concentration characteristic implementation."""

from __future__ import annotations

from ...types.gatt_enums import ValueType
from .base import BaseCharacteristic
from .templates import ConcentrationTemplate


class PM1ConcentrationCharacteristic(BaseCharacteristic):
    """Particulate Matter - PM1 Concentration characteristic (0x2BD5).

    org.bluetooth.characteristic.particulate_matter_pm1_concentration

    PM1 particulate matter concentration characteristic (0x2BD7).

    Represents particulate matter PM1 concentration in micrograms per
    cubic meter with a resolution of 1 μg/m³.
    """

    _template = ConcentrationTemplate()

    _characteristic_name: str = "Particulate Matter - PM1 Concentration"
    _manual_value_type: ValueType | str | None = ValueType.INT
    _manual_unit: str = "µg/m³"  # Override template's "ppm" default

    # Template configuration
    resolution: float = 1.0
